#!/usr/bin/env python
# this really only works on linux systems, at the moment
from __future__ import print_function


from setuptools import setup
from setuptools.command.sdist import sdist as orig_sdist
from setuptools.command.install import install as orig_install

if True:
    # pylint: disable=import-error
    # pylint doesn't agree with virtualenv's distutils hacks
    #   https://bitbucket.org/logilab/pylint/issues/73/pylint-is-unable-to-import
    from distutils.core import Command
    from distutils.command.build import build as orig_build


# ############# NOTES #####################
# setuptools.command.sdist.sdist

# setuptools/command/egg_info.py:egg_info.find_sources()
#   seems to be in charge of generating a file list
#   writes SOURCES.txt for its list
#   also reads MANIFEST.in; maybe this is the interface

# setuptools/command/sdist.py:add_defaults
#   adds various files to the file list based on the distribution object

# distutils/command/sdist.py:sdist.make_release_tree(base_dir, files)
#   copy files to base_dir. this will become the sdist

def system(cmd):
    from os import system
    from sys import stderr
    print(': %s' % cmd, file=stderr)
    if system(cmd) != 0:
        exit('command failed: %s' % cmd)


class build(orig_build):
    sub_commands = orig_build.sub_commands + [
        ('build_s6', None),
    ]


class install(orig_install):
    sub_commands = orig_install.sub_commands + [
        ('install_cexe', None),
    ]


class sdist(orig_sdist):
    def run(self):
        self.run_command('fetch_sources')
        return orig_sdist.run(self)


class fetch_sources(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        system('./get_sources.sh')


class build_s6(Command):
    build_temp = None

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.set_undefined_options('build', ('build_temp', 'build_temp'))

    def run(self):
        self.run_command('fetch_sources')
        system('./build.sh %s' % self.build_temp)


class install_cexe(Command):
    description = 'install C executables'
    outfiles = ()
    build_dir = install_dir = None

    def initialize_options(self):
        pass

    def finalize_options(self):
        # this initializes attributes based on other commands' attributes
        self.set_undefined_options('build', ('build_temp', 'build_dir'))
        self.set_undefined_options(
            'install', ('install_data', 'install_dir'))

    def run(self):
        self.outfiles = self.copy_tree(self.build_dir, self.install_dir)

    def get_outputs(self):
        return self.outfiles


try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):

        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            # Mark us as not a pure python package
            self.root_is_pure = False

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            # We don't contain any python source
            python, abi = 'py2.py3', 'none'
            return python, abi, plat
except ImportError:
    bdist_wheel = None


import versions
if versions.s6_version == 'master':
    version = '0'
else:
    version = versions.s6_version
version += versions.suffix

setup(
    name='s6',
    version=version,
    cmdclass={
        'sdist': sdist,
        'bdist_wheel': bdist_wheel,
        'fetch_sources': fetch_sources,
        'build': build,
        'build_s6': build_s6,
        'install': install,
        'install_cexe': install_cexe,
    },
    platforms=['linux'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Topic :: System :: Boot :: Init',
        'Development Status :: 5 - Production/Stable',
    ],
)
