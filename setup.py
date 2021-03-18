import setuptools
import os
import re
import sys

import platform
from distutils.version import LooseVersion
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import subprocess

is_linux = False
is_mac = False

if platform.system() == 'Linux':
    is_linux = True
if platform.system() == 'Darwin':
    is_mac = True

# identify which engines to build
build_gnu = os.environ.get('GNUPROLOG_HOME')
build_xsb = os.environ.get('XSB_HOME')
build_swi = os.environ.get("SWIPL_HOME")

# check if gnu-prolog is installed on the system
if build_gnu is None:
    results = subprocess.run(['which', 'gprolog'], stdout=subprocess.PIPE)
    result = results.stdout.decode('utf-8').strip()

    if len(result) > 1:
        result = result.replace("/bin/gprolog", "")

        if is_mac:
            apd = [x for x in os.listdir(result) if x.startswith('gprolog')]
            print(f"found GNU: {result}/{apd}")
            build_gnu = f"{result}/{apd[0]}"
        if is_linux:
            result = f"{result}/lib"
            apd = [x for x in os.listdir(result) if x.startswith('gprolog')]
            print(f"found GNU: {result}/{apd}")
            build_gnu = f"{result}/{apd[0]}"


# check if XSB is installed on the system
if build_xsb is None:
    results = subprocess.run(['which', 'xsb'], stdout=subprocess.PIPE)
    result = results.stdout.decode('utf-8').strip()

    if len(result) > 1:
        result = result.replace("/bin/xsb", "")
        build_xsb = result

# check if swipl is installed on the system
if build_swi is None:
    results = subprocess.run(['which', 'swipl'], stdout=subprocess.PIPE)
    result = results.stdout.decode('utf-8').strip()

    if len(result) > 1:
        # it does not matter what it is because the paths are automatically identified in CMakeLists.txt
        build_swi = result



# discover the correct paths
if build_gnu:
    gnu_var_path = build_gnu
    os.environ['GNU_LIB_PATH'] = gnu_var_path

if build_xsb:
    xsb_path = build_xsb
    xsb_path += "/config"
    arch_dir = [x.path for x in os.scandir(xsb_path) if x.is_dir()][0]
    os.environ['XSB_LIB_PATH'] = arch_dir

if build_swi:
    # !! not needed anymore - everything set up in the CMakeLists.txt
    # swi_path = build_swi
    # if is_mac:
    #     swi_path += "/lib"
    #     arch_dir = [x.path for x in os.scandir(swi_path) if x.is_dir()][0]
    # else:
    #     arch_dir = swi_path
    os.environ['SWIPL_LIB_PATH'] = build_swi #arch_dir

print(f"Building:\n\tGNU:{build_gnu}\n\tXSB:{build_xsb}\n\tSWIPL:{build_swi}")


class CMakeExtension(Extension):

    def __init__(self, name, sourcedir='.'):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):

    def run(self):
        # check if cmake exists
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)',
                                                   out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        print(f"Building extension: {ext}")
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={}'.format(self.build_temp),
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        print(f"   extdir: {extdir}\n     outputdir: {self.build_temp}")

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
                cfg.upper(),
                extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            # build_args += ['--', '-j4']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        swipl_build_dir = self.build_temp + "_swipl"
        if not os.path.exists(swipl_build_dir):
            os.makedirs(swipl_build_dir)

        if build_gnu:
            subprocess.check_call(['cmake', ext.sourcedir] + cmake_args + ['-DGPROLOG=ON'],
                                  cwd=self.build_temp, env=env)

            subprocess.check_call(['cmake', '--build', '.'] + build_args,
                                  cwd=self.build_temp)

        if build_xsb:
            subprocess.check_call(['cmake', ext.sourcedir] + cmake_args + ['-DXSBPROLOG=ON'],
                                  cwd=self.build_temp, env=env)

            subprocess.check_call(['cmake', '--build', '.'] + build_args,
                                  cwd=self.build_temp)

        if build_swi:
            subprocess.check_call(['cmake', ext.sourcedir] + cmake_args + ['-DSWIPL=ON'],
                                  cwd=swipl_build_dir, env=env)

            subprocess.check_call(['cmake', '--build', '.'] + build_args,
                                  cwd=swipl_build_dir)

        print()


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(name='pylo',
                 version='0.3.4',
                 author='Sebastijan Dumancic',
                 author_email='sebastijan.dumancic@gmail.com',
                 description="Python wrapper for several Prolog engines",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/sebdumancic/pylo2",
                 packages=setuptools.find_packages('src'),
                 package_dir={'':'src'},
                 ext_modules=[CMakeExtension('pylo')],
                 cmdclass=dict(build_ext=CMakeBuild),
                 install_requires=[
                     'networkx',
                     'miniKanren',
                     'z3-solver'
                 ],
                 python_requires=">=3.6",
                 classifiers=[
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Scientific/Engineering :: Artificial Intelligence',
                     'Topic :: Software Development :: Libraries :: Python Modules'
                 ]
                 )