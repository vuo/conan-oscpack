from conans import ConanFile, tools
import platform

class OscPackConan(ConanFile):
    name = 'oscpack'

    # There are no tagged releases, so just use package_version.
    source_version = '0'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.rossbencina.com/code/oscpack'
    license = 'http://www.rossbencina.com/code/oscpack'
    description = 'A cross-platform library for packing and unpacking OSC packets'
    source_dir = 'oscpack'
    install_dir = '_install'
    exports_sources = '*.patch'

    def source(self):
        if platform.system() == 'Darwin':
            flags = '-mmacosx-version-min=10.10'
        elif platform.system() == 'Linux':
            flags = '-fPIC'

        self.run("git clone https://github.com/vuo/oscpack.git")
        with tools.chdir(self.source_dir):
            self.run("git checkout facab13")
            tools.replace_in_file('Makefile',
                                  'CXX := g++',
                                  'CXX := %s' % self.deps_cpp_info['llvm'].rootpath + '/bin/clang++')
            tools.replace_in_file('Makefile',
                                  'COPTS  := -Wall -Wextra -O3',
                                  'COPTS  := -Wall -Wextra -Oz -stdlib=libstdc++ ' + flags)
            tools.replace_in_file('Makefile',
                                  '	$(CXX) -dynamiclib -Wl,-install_name,$(LIBSONAME) -o $(LIBFILENAME) $(LIBOBJECTS) -lc',
                                  '	$(CXX) -dynamiclib -Wl,-install_name,@rpath/liboscpack.dylib -Oz -mmacosx-version-min=10.10 -stdlib=libstdc++ -o $(LIBFILENAME) $(LIBOBJECTS) -lc')
            tools.replace_in_file('Makefile',
                                  '	@ldconfig',
                                  '	echo skipping ldconfig')

        # http://web.archive.org/web/20170102013425/https://code.google.com/archive/p/oscpack/issues/15
        tools.patch(patch_file='udpsocket-get-port.patch', base_path=self.source_dir)

        self.run('mv %s/LICENSE %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.install_dir)
        tools.mkdir('%s/lib' % self.install_dir)
        with tools.chdir(self.source_dir):
            self.run('make install PREFIX=../%s' % self.install_dir)

        with tools.chdir('%s/lib' % self.install_dir):
            self.run('rm liboscpack.so')
            if platform.system() == 'Darwin':
                self.run('mv liboscpack.so.1.1.0 liboscpack.dylib')
            elif platform.system() == 'Linux':
                self.run('mv liboscpack.so.1.1.0 liboscpack.so')

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h',     src='%s/include' % self.install_dir, dst='include')
        self.copy('liboscpack.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['oscpack']
