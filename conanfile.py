from conans import ConanFile, CMake, tools
import os
import platform

class OscPackConan(ConanFile):
    name = 'oscpack'

    # The latest tag (`release_1_1_0`) refers to a nonexistent commit, so just use package_version.
    source_version = '0'
    package_version = '5'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-5@vuo+conan+llvm/stable',
        'macos-sdk/11.0-0@vuo+conan+macos-sdk/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.rossbencina.com/code/oscpack'
    license = 'http://www.rossbencina.com/code/oscpack'
    description = 'A cross-platform library for packing and unpacking OSC packets'
    source_dir = 'oscpack'
    generators = 'cmake'
    build_dir = '_build'
    exports_sources = '*.patch'

    def source(self):
        self.run("git clone https://github.com/RossBencina/oscpack.git")
        with tools.chdir(self.source_dir):
            self.run("git checkout 3e7e3a102e316d75fe176885a6dd08f216f2eac0")  # Latest commit as of 2021.05.24.
            tools.replace_in_file('CMakeLists.txt',
                                  'ADD_LIBRARY(oscpack',
                                  'ADD_LIBRARY(oscpack SHARED')

        # http://web.archive.org/web/20170102013425/https://code.google.com/archive/p/oscpack/issues/15
        tools.patch(patch_file='udpsocket-get-port.patch', base_path=self.source_dir)

        tools.download('https://github.com/RossBencina/oscpack/pull/22.patch', '22.patch')
        tools.patch(patch_file='22.patch', base_path=self.source_dir)

        self.run('mv %s/LICENSE %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        cmake = CMake(self)
        cmake.definitions['CONAN_DISABLE_CHECK_COMPILER'] = True
        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['CMAKE_CXX_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang++'
        cmake.definitions['CMAKE_C_COMPILER']   = self.deps_cpp_info['llvm'].rootpath + '/bin/clang'
        cmake.definitions['CMAKE_C_FLAGS'] = cmake.definitions['CMAKE_CXX_FLAGS'] = '-Oz -DNDEBUG'
        cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
        cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath

        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.',
                            args=['-Wno-dev', '--no-warn-unused-cli'])
            cmake.build(target='oscpack')
            self.run('install_name_tool -id @rpath/liboscpack.dylib liboscpack.dylib')

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src=self.source_dir, dst='include/oscpack')
        self.copy('liboscpack.%s' % libext, src=self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['oscpack']
