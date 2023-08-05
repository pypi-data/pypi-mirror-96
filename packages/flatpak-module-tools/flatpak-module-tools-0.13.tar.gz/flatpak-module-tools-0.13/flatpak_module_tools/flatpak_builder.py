"""
Copyright (c) 2017 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.

This file is code for generating Flatpak OCI images out of a filesystem
image. It is shared between:

 https://github.com/projectatomic/atomic-reactor
 https://pagure.io/flatpak-module-tools
"""

import errno
import functools
import hashlib
import json
import logging
import os
from six.moves import configparser
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
from textwrap import dedent
from xml.etree import ElementTree


FLATPAK_METADATA_LABELS = "labels"
FLATPAK_METADATA_ANNOTATIONS = "annotations"
FLATPAK_METADATA_BOTH = "both"


# Work around lack of RawConfigParser space_around_delimeters in Python-2.7
if sys.version_info[0] == 2:
    class MyConfigParser(configparser.RawConfigParser):
        # Copy from configparser.RawConfigParser - Copyright (c) 2017 Python Software Foundation
        # https://www.python.org/download/releases/2.7/license/
        def write(self, fp, space_around_delimiters=False):
            """Write an .ini-format representation of the configuration state."""
            for section in self._sections:
                fp.write("[%s]\n" % section)
                for (key, value) in self._sections[section].items():
                    if key == "__name__":
                        continue
                    if (value is not None) or (self._optcre == self.OPTCRE):
                        key = "=".join((key, str(value).replace('\n', '\n\t')))
                    fp.write("%s\n" % (key))
                fp.write("\n")

    CP = MyConfigParser
else:
    CP = configparser.RawConfigParser


@functools.cache
def get_flatpak_arch():
    """Return Flatpak's name for the current architecture"""
    return subprocess.check_output(['flatpak', '--default-arch'],
                                   universal_newlines=True).strip()


# Returns flatpak's name for the current arch
@functools.cache
def get_rpm_arch():
    """Return RPM's name for the current architecture"""
    return subprocess.check_output(['rpm', '--eval', '%{_arch}'],
                                   universal_newlines=True).strip()


# flatpak build-init requires the sdk and runtime to be installed on the
# build system (so that subsequent build steps can execute things with
# the SDK). While it isn't impossible to download the runtime image and
# install the flatpak, that would be a lot of unnecessary complexity
# since our build step is just unpacking the filesystem we've already
# created. This is a stub implementation of 'flatpak build-init' that
# doesn't check for the SDK or use it to set up the build filesystem.
def build_init(directory, appname, sdk, runtime, runtime_branch, tags=[]):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    with open(os.path.join(directory, "metadata"), "w") as f:
        f.write(dedent("""\
                       [Application]
                       name={appname}
                       runtime={runtime}/{arch}/{runtime_branch}
                       sdk={sdk}/{arch}/{runtime_branch}
                       """.format(appname=appname,
                                  sdk=sdk,
                                  runtime=runtime,
                                  runtime_branch=runtime_branch,
                                  arch=get_flatpak_arch())))
        if tags:
            f.write("tags=" + ";".join(tags) + "\n")
    os.mkdir(os.path.join(directory, "files"))


class ModuleInfo(object):
    def __init__(self, name, stream, version, mmd, rpms):
        self.name = name
        self.stream = stream
        self.version = version
        self.mmd = mmd
        self.rpms = rpms

    def get_profile_packages(self, profile):
        result = self.mmd.get_profile(profile).get_rpms()

        arch_profile = profile + '-' + get_rpm_arch()
        if arch_profile in self.mmd.get_profile_names():
            result.extend(self.mmd.get_profile(arch_profile).get_rpms())

        return result


class FileTreeProcessor(object):
    def __init__(self, builddir, flatpak_yaml):
        self.app_root = os.path.join(builddir, "files")
        self.app_id = flatpak_yaml['id']

        self.appdata_license = flatpak_yaml.get('appdata-license', None)
        self.appstream_compose = flatpak_yaml.get('appstream-compose', True)
        self.copy_icon = flatpak_yaml.get('copy-icon', False)
        self.desktop_file_name_prefix = flatpak_yaml.get('desktop-file-name-prefix')
        self.desktop_file_name_suffix = flatpak_yaml.get('desktop-file-name-suffix')
        self.rename_appdata_file = flatpak_yaml.get('rename-appdata-file', None)
        self.rename_desktop_file = flatpak_yaml.get('rename-desktop-file')
        self.rename_icon = flatpak_yaml.get('rename-icon')

        self.log = logging.getLogger(__name__)

    def _find_appdata_file(self):
        # We order these so that share/appdata/XXX.appdata.xml if found
        # first, as this is the target name, and apps may have both, which will
        # cause issues with the rename.
        extensions = [
            ".appdata.xml",
            ".metainfo.xml",
        ]

        dirs = [
            "share/appdata",
            "share/metainfo",
        ]

        for d in dirs:
            appdata_dir = os.path.join(self.app_root, d)
            for ext in extensions:
                if self.rename_appdata_file is not None:
                    basename = self.rename_appdata_file
                else:
                    basename = self.app_id + ext

                source = os.path.join(appdata_dir, basename)
                if os.path.exists(source):
                    return source

        return None

    def _rewrite_appdata(self):
        tree = ElementTree.parse(self.appdata_file)

        # replace component/id
        n_root = tree.getroot()
        if n_root.tag != "component" and n_root.tag != "application":
            raise RuntimeError("Root node is not <application> or <component>")

        n_license = n_root.find("project_license")
        if n_license is not None:
            n_license.text = self.appdata_license

        tree.write(self.appdata_file, encoding="UTF-8", xml_declaration=True)

    def _process_appdata_file(self):
        appdata_source = self._find_appdata_file()
        self.appdata_file = None

        if appdata_source:
            # We always use the old name / dir, in case the runtime has older appdata tools
            appdata_dir = os.path.join(self.app_root, "share", "appdata")
            appdata_basename = self.app_id + ".appdata.xml"
            self.appdata_file = os.path.join(appdata_dir, appdata_basename)

            if appdata_source != self.appdata_file:
                src_basename = os.path.basename(appdata_source)
                self.log.info("Renaming %s to share/appdata/%s", src_basename, appdata_basename)

                if not os.path.exists(appdata_dir):
                    os.makedirs(appdata_dir)
                os.rename(appdata_source, self.appdata_file)

            if self.appdata_license:
                self._rewrite_appdata()

    def _rename_desktop_file(self):
        if not self.rename_desktop_file:
            return

        applications_dir = os.path.join(self.app_root, "share", "applications")
        src = os.path.join(applications_dir, self.rename_desktop_file)
        desktop_basename = self.app_id + ".desktop"
        dest = os.path.join(applications_dir, desktop_basename)

        self.log.info("Renaming %s to %s", self.rename_desktop_file, desktop_basename)
        os.rename(src, dest)

        if self.appdata_file:
            tree = ElementTree.parse(self.appdata_file)

            # replace component/id
            n_root = tree.getroot()
            if n_root.tag != "component" and n_root.tag != "application":
                raise RuntimeError("Root node is not <application> or <component>")

            n_id = n_root.find("id")
            if n_id is not None:
                if n_id.text == self.rename_desktop_file:
                    n_id.text = self.app_id

            # replace any optional launchable
            n_launchable = n_root.find("launchable")
            if n_launchable is not None:
                if n_launchable.text == self.rename_desktop_file:
                    n_launchable.text = desktop_basename

            tree.write(self.appdata_file, encoding="UTF-8", xml_declaration=True)

    def _rename_icon(self):
        if not self.rename_icon:
            return

        found_icon = False
        icons_dir = os.path.join(self.app_root, "share/icons")

        for full_dir, dirnames, filenames in os.walk(icons_dir):
            relative = full_dir[len(icons_dir):]
            depth = relative.count("/")

            for source_file in filenames:
                if source_file.startswith(self.rename_icon):
                    source_path = os.path.join(full_dir, source_file)
                    is_file = os.path.isfile(source_path)
                    extension = source_file[len(self.rename_icon):]

                    if is_file and depth == 3 and (extension.startswith(".") or
                                                   extension.startswith("-symbolic")):
                        found_icon = True
                        new_name = self.app_id + extension

                        self.log.info("%s icon %s/%s to %s/%s",
                                      "Copying" if self.copy_icon else "Renaming",
                                      relative[1:], source_file,
                                      relative[1:], new_name)

                        dest_path = os.path.join(full_dir, new_name)
                        if self.copy_icon:
                            shutil.copy(source_path, dest_path)
                        else:
                            os.rename(source_path, dest_path)
                    else:
                        if not is_file:
                            self.log.debug("%s/%s matches 'rename-icon', but not a regular file",
                                           full_dir, source_file)
                        elif depth != 3:
                            self.log.debug("%s/%s matches 'rename-icon', but not at depth 3",
                                           full_dir, source_file)
                        else:
                            self.log.debug("%s/%s matches 'rename-icon', but name does not "
                                           "continue with '.' or '-symbolic.'",
                                           full_dir, source_file)

        if not found_icon:
            raise RuntimeError("icon {} not found below {}".format(self.rename_icon, icons_dir))

    def _rewrite_desktop_file(self):
        if not (self.rename_icon or self.desktop_file_name_prefix or self.desktop_file_name_suffix):
            return

        applications_dir = os.path.join(self.app_root, "share/applications")
        desktop_basename = self.app_id + ".desktop"
        desktop = os.path.join(applications_dir, desktop_basename)

        self.log.debug("Rewriting contents of %s", desktop_basename)

        cp = CP()
        cp.optionxform = str
        with open(desktop) as f:
            cp.readfp(f)

        desktop_keys = cp.options('Desktop Entry')

        if self.rename_icon:
            if self.rename_icon:
                original_icon_name = cp.get('Desktop Entry', 'Icon')
                cp.set('Desktop Entry', 'Icon', self.app_id)

                for key in desktop_keys:
                    if key.startswith("Icon["):
                        if cp.get('Desktop Entry', key) == original_icon_name:
                            cp.set('Desktop Entry', key, self.app_id)

        if self.desktop_file_name_suffix or self.desktop_file_name_prefix:
            for key in desktop_keys:
                if key == "Name" or key.startswith("Name["):
                    name = cp.get('Desktop Entry', key)
                    new_name = ((self.desktop_file_name_prefix or "") +
                                name +
                                (self.desktop_file_name_suffix or ""))
                    cp.set('Desktop Entry', key, new_name)

        with open(desktop, "w") as f:
            cp.write(f, space_around_delimiters=False)

    def _compose_appstream(self):
        if not self.appstream_compose or not self.appdata_file:
            return

        subprocess.check_call(['appstream-compose',
                               '--verbose',
                               '--prefix', self.app_root,
                               '--basename', self.app_id,
                               '--origin', 'flatpak',
                               self.app_id])

    def process(self):
        self._process_appdata_file()
        self._rename_desktop_file()
        self._rename_icon()
        self._rewrite_desktop_file()
        self._compose_appstream()


class FlatpakSourceInfo(object):
    def __init__(self, flatpak_yaml, modules, base_module, profile=None):
        self.flatpak_yaml = flatpak_yaml
        self.modules = modules
        self.base_module = base_module

        # A runtime module must have a 'runtime' profile, but can have other
        # profiles for SDKs, minimal runtimes, etc.
        self.runtime = 'runtime' in base_module.mmd.get_profile_names()

        if profile is None:
            profile = 'runtime' if self.runtime else 'default'

        if profile not in base_module.mmd.get_profile_names():
            raise ValueError("{}:{}:{} doesn't have a profile '{}'".format(
                base_module.name, base_module.stream, base_module.version,
                profile))

        self.profile = profile

    # The module for the Flatpak runtime that this app runs against
    @property
    def runtime_module(self):
        assert not self.runtime

        dependencies = self.base_module.mmd.get_dependencies()
        # A built module should have its dependencies already expanded
        assert len(dependencies) <= 1

        if len(dependencies) == 1:
            for module_name in dependencies[0].get_buildtime_modules():
                try:
                    module = self.modules[module_name]
                    if 'runtime' in module.mmd.get_profile_names():
                        return module
                except KeyError:
                    pass

        raise RuntimeError("Failed to identify runtime module in the buildrequires for {}"
                           .format(self.base_module.name))

    # All modules that were build against the Flatpak runtime,
    # and thus were built with prefix=/app. This is primarily the app module
    # but might contain modules shared between multiple flatpaks as well.
    @property
    def app_modules(self):
        runtime_module_name = self.runtime_module.mmd.props.module_name

        def is_app_module(m):
            dependencies = m.mmd.get_dependencies()
            return runtime_module_name in dependencies[0].get_buildtime_modules()

        return [m for m in self.modules.values() if is_app_module(m)]


class FlatpakBuilder(object):
    def __init__(self, source, workdir, root, parse_manifest=None,
                 flatpak_metadata=FLATPAK_METADATA_ANNOTATIONS):
        self.source = source
        self.workdir = workdir
        self.root = root
        self.parse_manifest = parse_manifest

        if flatpak_metadata not in (FLATPAK_METADATA_ANNOTATIONS,
                                    FLATPAK_METADATA_LABELS,
                                    FLATPAK_METADATA_BOTH):
            raise ValueError("Bad flatpak_metadata value %s" % flatpak_metadata)
        self.flatpak_metadata = flatpak_metadata

        self.log = logging.getLogger(__name__)

        self.extra_labels = {}

    def add_labels(self, labels):
        """Specify additional labels to add to the generated image"""

        self.extra_labels.update({k: str(v) for k, v in labels.items()})

    def precheck(self):
        source = self.source

        # For a runtime, certain information is duplicated between the container.yaml
        # and the modulemd, check that it matches
        if source.runtime:
            flatpak_yaml = source.flatpak_yaml
            flatpak_xmd = self.source.base_module.mmd.get_xmd()['flatpak']

            def check(condition, what):
                if not condition:
                    raise RuntimeError(
                        "Mismatch for {} betweeen module xmd and container.yaml".format(what))

            check(flatpak_yaml['branch'] == flatpak_xmd['branch'], "'branch'")
            check(source.profile in flatpak_xmd['runtimes'], 'profile name')

            profile_xmd = flatpak_xmd['runtimes'][source.profile]

            check(flatpak_yaml['id'] == profile_xmd['id'], "'id'")
            check(flatpak_yaml.get('runtime', None) ==
                  profile_xmd.get('runtime', None), "'runtime'")
            check(flatpak_yaml.get('sdk', None) == profile_xmd.get('sdk', None), "'sdk'")

    def get_enable_modules(self):
        # We need to enable all the modules other than the platform pseudo-module
        # sorted for testability.
        return sorted(m.mmd.props.module_name + ':' + m.mmd.props.stream_name
                      for m in self.source.modules.values()
                      if m.mmd.props.module_name != 'platform')

    def get_install_packages(self):
        source = self.source
        packages = source.base_module.get_profile_packages(source.profile)
        if not source.runtime:
            # The flatpak-runtime-config package is needed when building an application
            # Flatpak because it includes file triggers for files in /app. (Including just
            # this package avoids having to install the entire runtime package set; if
            # we need to make this configurable it could be a separate profile of
            # the runtime.)
            packages.append('flatpak-runtime-config')

        return packages

    def get_includepkgs(self):
        source = self.source

        # For a runtime, we want to make sure that the set of RPMs that is installed
        # into the filesystem is *exactly* the set that is listed in the runtime
        # profile. Requiring the full listed set of RPMs to be listed makes it
        # easier to catch unintentional changes in the package list that might break
        # applications depending on the runtime. It also simplifies the checking we
        # do for application flatpaks, since we can simply look at the runtime
        # modulemd to find out what packages are present in the runtime.
        #
        # For an application, we want to make sure that each RPM that is installed
        # into the filesystem is *either* an RPM that is part of the 'runtime'
        # profile of the base runtime, or from a module that was built with
        # flatpak-rpm-macros in the install root and, thus, prefix=/app.
        #
        # We achieve this by restricting the set of available packages in the dnf
        # configuration to just the ones that we want.
        #
        # The advantage of doing this upfront, rather than just checking after the
        # fact is that this makes sure that when a application is being installed,
        # we don't get a different package to satisfy a dependency than the one
        # in the runtime - e.g. aajohan-comfortaa-fonts to satisfy font(:lang=en)
        # because it's alphabetically first.

        if not source.runtime:
            runtime_module = source.runtime_module
            available_packages = sorted(runtime_module.get_profile_packages('runtime'))

            for m in source.app_modules:
                # Strip off the '.rpm' suffix from the filename to get something
                # that DNF can parse.
                available_packages.extend(x[:-4] for x in m.rpms)
        else:
            base_module = source.base_module
            available_packages = sorted(base_module.get_profile_packages(source.profile))

        return available_packages

    def get_cleanup_script(self):
        cleanup_commands = self.source.flatpak_yaml.get('cleanup-commands')
        if cleanup_commands is not None:
            return cleanup_commands.rstrip() + '\n'
        else:
            return ''

    # Compiles a list of path mapping rules to a simple function that matches
    # against a list of fixed patterns, see below for rule syntax
    def _compile_target_rules(self, rules):
        patterns = []
        for source, target in rules:
            source = re.sub("^ROOT", self.root, source)
            if source.endswith("/"):
                patterns.append((re.compile(source + "(.*)"), target, False))
                patterns.append((source[:-1], target, True))
            else:
                patterns.append((source, target, True))

        def get_target_func(path):
            for source, target, is_exact_match in patterns:
                if is_exact_match:
                    if source == path:
                        return target
                else:
                    m = source.match(path)
                    if m:
                        return os.path.join(target, m.group(1))

            return None

        return get_target_func

    # Rules for mapping paths within the exported filesystem image to their
    # location in the final flatpak filesystem
    #
    # ROOT = root of the filesystem to extract - e.g. var/tmp/flatpak-build
    # No trailing slash - map a directory itself exactly
    # trailing slash - map a directory and everything inside of it

    def _get_target_path_runtime(self):
        return self._compile_target_rules([
            # We need to make sure that 'files' is created before 'files/etc',
            # which wouldn't happen if just relied on ROOT/usr/ => files.
            # Instead map ROOT => files and omit ROOT/usr
            ("ROOT", "files"),
            ("ROOT/usr", None),

            # We map ROOT/usr => files and ROOT/etc => files/etc. This creates
            # A conflict between ROOT/usr/etc and /ROOT/etc. Just assume there
            # is nothing useful in /ROOT/usr/etc.
            ("ROOT/usr/etc/", None),

            ("ROOT/usr/", "files"),
            ("ROOT/etc/", "files/etc")
        ])

    def _get_target_path_app(self):
        return self._compile_target_rules([
            ("ROOT/app/", "files")
        ])

    def _export_from_stream(self, export_stream, close_stream=True):
        if self.source.runtime:
            get_target_path = self._get_target_path_runtime()
        else:
            get_target_path = self._get_target_path_app()

        outfile = os.path.join(self.workdir, 'filesystem.tar.gz')
        manifestfile = os.path.join(self.workdir, 'flatpak-build.rpm_qf')

        out_fileobj = open(outfile, "wb")
        compress_process = subprocess.Popen(['gzip', '-c'],
                                            stdin=subprocess.PIPE,
                                            stdout=out_fileobj)
        in_tf = tarfile.open(fileobj=export_stream, mode='r|')
        out_tf = tarfile.open(fileobj=compress_process.stdin, mode='w|')

        for member in in_tf:
            if member.name == 'var/tmp/flatpak-build.rpm_qf':
                reader = in_tf.extractfile(member)
                with open(manifestfile, 'wb') as out:
                    out.write(reader.read())
                reader.close()
            target_name = get_target_path(member.name)
            if target_name is None:
                continue

            # Match the ownership/permissions changes done by 'flatpak build-export'.
            # See commit_filter() in:
            #   https://github.com/flatpak/flatpak/blob/master/app/flatpak-builtins-build-export.c
            #
            # We'll run build-export anyways in the app case, but in the runtime case we skip
            # flatpak build-export and use ostree directly.
            member.uid = 0
            member.gid = 0
            member.uname = "root"
            member.gname = "root"

            if member.isdir():
                member.mode = 0o0755
            elif member.isreg():
                if member.mode & 0o0100:
                    member.mode = 0o0755
                else:
                    member.mode = 0o0644

            member.name = target_name

            # if member.name was > 100 characters, but target_name <= 100 characters,
            # member.pax_headers["path"] will stick around and override member.name;
            # it will be recreated if target_name > 100 characters
            if "path" in member.pax_headers:
                del member.pax_headers["path"]

            if member.islnk():
                # Hard links have full paths within the archive (no leading /)
                link_target = get_target_path(member.linkname)
                if link_target is None:
                    self.log.debug("Skipping %s, hard link to %s", target_name, link_target)
                    continue
                member.linkname = link_target

                # if member.linkname was > 100 characters, but link_target < 100 characters,
                # member.pax_headers["path"] will stick around and override member.name
                # it will be recreated if link_target > 100 characters
                if "linkpath" in member.pax_headers:
                    del member.pax_headers["linkpath"]

                out_tf.addfile(member)
            elif member.issym():
                # Symlinks have the literal link target, which will be
                # relative to the chroot and doesn't need rewriting
                out_tf.addfile(member)
            else:
                f = in_tf.extractfile(member)
                out_tf.addfile(member, fileobj=f)

        in_tf.close()
        out_tf.close()
        if close_stream:
            export_stream.close()
        compress_process.stdin.close()
        if compress_process.wait() != 0:
            raise RuntimeError("gzip failed")
        out_fileobj.close()

        return outfile, manifestfile

    def _get_components(self, manifest):
        with open(manifest, 'r') as f:
            lines = f.readlines()

        return self.parse_manifest(lines)

    def _filter_app_manifest(self, components):
        # DNF filtering from get_includepkgs() restricts the installed packages
        # to:
        #
        #  Runtime packages: libfoo
        #  App module packages: libbar-0:1.2.3-1.module_1.33+11439+4b44cd2d.x86_64.rpm
        #
        # We want to filter the set of installed packages to only ones installed from
        # the app module packages. We used to do this by excluding packages where
        # c['name'] was in the runtime, but this doesn't work - even if 'libfoo' is in
        # the runtime, a different 'libfoo' might be in a module. We need to instead
        # compare against the particular versions in the app modules.

        app_packages = set()
        for m in self.source.app_modules:
            app_packages.update(m.rpms)

        def is_app_package(component):
            pkg_string = ('{name}-{epochnum}:{version}-{release}.{arch}.rpm'
                          .format(epochnum=component['epoch'] or 0, **component))
            return pkg_string in app_packages

        return [c for c in components if is_app_package(c)]

    def get_components(self, manifest):
        all_components = self._get_components(manifest)
        if self.source.runtime:
            image_components = all_components
        else:
            image_components = self._filter_app_manifest(all_components)

        return image_components

    def _build_finish(self, builddir):
        info = self.source.flatpak_yaml

        finish_args = []
        if 'finish-args' in info:
            # shlex.split(None) reads from standard input, so avoid that
            finish_args = shlex.split(info['finish-args'] or '', comments=True)
        if 'command' in info and not self.source.runtime:
            finish_args = ['--command', info['command']] + finish_args

        subprocess.check_call(['flatpak', 'build-finish'] + finish_args + [builddir])

    def _create_runtime_oci(self, tarred_filesystem, outfile):
        info = self.source.flatpak_yaml

        builddir = os.path.join(self.workdir, "build")
        os.mkdir(builddir)

        filesdir = os.path.join(builddir, "files")
        os.mkdir(filesdir)

        repo = os.path.join(self.workdir, "repo")
        subprocess.check_call(['ostree', 'init', '--mode=archive-z2', '--repo', repo])

        id_ = info['id']
        runtime_id = info.get('runtime', id_)
        sdk_id = info.get('sdk', id_)
        branch = info['branch']

        args = {
            'id': id_,
            'runtime_id': runtime_id,
            'sdk_id': sdk_id,
            'arch': get_flatpak_arch(),
            'branch': branch
        }

        METADATA_TEMPLATE = dedent("""\
            [Runtime]
            name={id}
            runtime={runtime_id}/{arch}/{branch}
            sdk={sdk_id}/{arch}/{branch}
            """)

        with open(os.path.join(builddir, 'metadata'), 'w') as f:
            f.write(METADATA_TEMPLATE.format(**args))

        # Run flatpak-build-finish to add extra metadata, based on finish-args
        self._build_finish(builddir)

        with open(os.path.join(builddir, 'metadata'), 'r') as f:
            metadata = f.read()

        runtime_ref = 'runtime/{id}/{arch}/{branch}'.format(**args)

        commit_args = ['--repo', repo, '--owner-uid=0',
                       '--owner-gid=0', '--no-xattrs',
                       '--canonical-permissions',
                       '--branch', runtime_ref,
                       '-s', 'build of ' + runtime_ref,
                       '--tree=tar=' + tarred_filesystem,
                       '--tree=dir=' + builddir,
                       '--add-metadata-string', 'xa.metadata=' + metadata]

        if 'end-of-life' in info:
            commit_args += ['--add-metadata-string',
                            'ostree.endoflife=' + info['end-of-life']]
        if 'end-of-life-rebase' in info:
            commit_args += ['--add-metadata-string',
                            'ostree.endoflife-rebase=' + info['end-of-life-rebase']]

        subprocess.check_call(['ostree', 'commit'] + commit_args)
        subprocess.check_call(['ostree', 'summary', '-u', '--repo', repo])

        subprocess.check_call(['flatpak', 'build-bundle', repo,
                               '--oci', '--runtime',
                               outfile, id_, branch])

        return runtime_ref

    def _find_runtime_info(self):
        runtime_module = self.source.runtime_module

        flatpak_xmd = runtime_module.mmd.get_xmd()['flatpak']
        runtime_id = flatpak_xmd['runtimes']['runtime']['id']
        sdk_id = flatpak_xmd['runtimes']['runtime'].get('sdk', runtime_id)
        runtime_version = flatpak_xmd['branch']

        return runtime_id, sdk_id, runtime_version

    def _create_app_oci(self, tarred_filesystem, outfile):
        info = self.source.flatpak_yaml
        app_id = info['id']
        app_branch = info.get('branch', 'master')

        builddir = os.path.join(self.workdir, "build")
        os.mkdir(builddir)

        repo = os.path.join(self.workdir, "repo")

        runtime_id, sdk_id, runtime_version = self._find_runtime_info()

        # See comment for build_init() for why we can't use 'flatpak build-init'
        # subprocess.check_call(['flatpak', 'build-init',
        #                        builddir, app_id, runtime_id, runtime_id, runtime_version])
        build_init(builddir, app_id, sdk_id, runtime_id, runtime_version, tags=info.get('tags', []))

        # with gzip'ed tarball, tar is several seconds faster than tarfile.extractall
        subprocess.check_call(['tar', 'xCfz', builddir, tarred_filesystem])

        processor = FileTreeProcessor(builddir, info)
        processor.process()

        self._build_finish(builddir)

        # If we don't have a working bubblewrap, then we need to pass --disable-sandbox
        # to 'flatpak build-export'. On some systems, bwrap may be part
        # of the Flatpak install.

        def try_bwrap(exec_name):
            # return: True - works; False - doesn't work; None - not found
            try:
                return subprocess.call([exec_name, '--bind', '/', '/', 'true'],
                                       stdout=devnull, stderr=devnull) == 0
            except OSError as e:
                if e.errno == errno.ENOENT:
                    return None
                raise

        def try_export(disable_sandbox):
            args = ['flatpak', 'build-export', repo, builddir, app_branch]
            if disable_sandbox:
                args += ['--disable-sandbox']
            if 'end-of-life' in info:
                args += ['--end-of-life=' + info['end-of-life']]
            if 'end-of-life-rebase' in info:
                args += ['--end-of-life-rebase=' + info['end-of-life-rebase']]
            subprocess.check_call(args)

        with open(os.devnull) as devnull:
            have_bwrap = try_bwrap('bwrap')
            if have_bwrap is None:
                have_bwrap = try_bwrap('/usr/libexec/flatpak-bwrap')

        if have_bwrap:
            try_export(disable_sandbox=False)
        else:
            self.log.info('No working bubblewrap, callling flatpak build-export --disable-sandbox')
            try:
                try_export(disable_sandbox=True)
            except subprocess.CalledProcessError:
                # Older flatpak without --disable-sandbox?
                self.log.info('Retrying without --disable-sandbox')
                try_export(disable_sandbox=False)

        subprocess.check_call(['flatpak', 'build-bundle', repo, '--oci',
                               outfile, app_id, app_branch])

        app_ref = 'app/{app_id}/{arch}/{branch}'.format(app_id=app_id,
                                                        arch=get_flatpak_arch(),
                                                        branch=app_branch)

        return app_ref

    # Update the config JSON for the image:
    #
    #  * Convert OCI images with labels (Flatpak >= 1.6) to OCI images
    #    with annotations (Flaptak < 1.6), and vice-versa, or generate
    #    compat images with both labels and annotations.
    #  * Add in extra labels specified by the caller
    #  * Add a history entry if missing - old versions of Flatpak write an
    #    image config file without any history entries.
    #    History isn't required by OCI spec, but multiple tools have problems
    #    without history entries matching the layers of the image.
    #    https://github.com/flatpak/flatpak/commit/be9961ecf65a081aac24e2007a0af7be1424eb38
    def _fixup_config(self, outfile):
        def get_path_from_descriptor(descriptor):
            assert descriptor["digest"].startswith("sha256:")
            return os.path.join(outfile, "blobs", "sha256", descriptor["digest"][len("sha256:"):])

        def update_descriptor(descriptor, contents_json):
            old_path = get_path_from_descriptor(descriptor)
            contents_bytes = json.dumps(contents_json, indent=4).encode("UTF-8")
            digest = hashlib.sha256(contents_bytes).hexdigest()
            descriptor["digest"] = "sha256:" + digest
            descriptor["size"] = len(contents_bytes)
            new_path = get_path_from_descriptor(descriptor)
            with open(new_path, "wb") as f:
                f.write(contents_bytes)
            os.remove(old_path)

        with open(os.path.join(outfile, "index.json")) as f:
            index_json = json.load(f)

        old_manifest = get_path_from_descriptor(index_json["manifests"][0])
        with open(old_manifest) as f:
            manifest_json = json.load(f)
        annotations = manifest_json.setdefault("annotations", {})
        old_config = get_path_from_descriptor(manifest_json["config"])
        with open(old_config) as f:
            config_json = json.load(f)

        if config_json.get("history") is None:
            self.log.warning("No history in the image config, adding one")
            config_json["history"] = [
                {
                    "created": config_json["created"],
                    "created_by": "flatpak build-bundle",
                },
            ]

        config = config_json.setdefault("config", {})
        labels = config.setdefault("Labels", {})

        if self.flatpak_metadata != FLATPAK_METADATA_ANNOTATIONS:
            # Merge in the annotations as labels
            to_delete = list()
            for k, v in annotations.items():
                if k.startswith("org.flatpak.") or k.startswith("org.freedesktop."):
                    if k not in labels:
                        labels[k] = v
                    if self.flatpak_metadata != FLATPAK_METADATA_BOTH:
                        to_delete.append(k)

            for k in to_delete:
                del annotations[k]

        if self.flatpak_metadata != FLATPAK_METADATA_LABELS:
            # And merge the labels as annotations the other way
            to_delete = list()
            for k, v in labels.items():
                if k.startswith("org.flatpak.") or k.startswith("org.freedesktop."):
                    if k not in annotations:
                        annotations[k] = v
                    if self.flatpak_metadata != FLATPAK_METADATA_BOTH:
                        to_delete.append(k)

            for k in to_delete:
                del labels[k]

        labels.update(self.extra_labels)

        update_descriptor(manifest_json["config"], config_json)
        update_descriptor(index_json["manifests"][0], manifest_json)

        with open(os.path.join(outfile, "index.json"), "w") as f:
            json.dump(index_json, f, indent=4)

    def build_container(self, tarred_filesystem):
        outfile = os.path.join(self.workdir, 'flatpak-oci-image')

        if self.source.runtime:
            ref_name = self._create_runtime_oci(tarred_filesystem, outfile)
        else:
            ref_name = self._create_app_oci(tarred_filesystem, outfile)

        self._fixup_config(outfile)

        tarred_outfile = outfile + '.tar'
        with tarfile.TarFile(tarred_outfile, "w") as tf:
            for f in os.listdir(outfile):
                tf.add(os.path.join(outfile, f), f)

        return ref_name, outfile, tarred_outfile
