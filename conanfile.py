from conans import ConanFile, tools

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
        self.run("git clone https://github.com/vuo/oscpack.git")
        with tools.chdir(self.source_dir):
            self.run("git checkout facab13")
            tools.replace_in_file('Makefile',
                                  'CXX := g++',
                                  'CXX := %s' % self.deps_cpp_info['llvm'].rootpath + '/bin/clang++')
            tools.replace_in_file('Makefile',
                                  'COPTS  := -Wall -Wextra -O3',
                                  'COPTS  := -Wall -Wextra -Oz -mmacosx-version-min=10.10 -stdlib=libstdc++')
            tools.replace_in_file('Makefile',
                                  '	$(CXX) -dynamiclib -Wl,-install_name,$(LIBSONAME) -o $(LIBFILENAME) $(LIBOBJECTS) -lc',
                                  '	$(CXX) -dynamiclib -Wl,-install_name,@rpath/liboscpack.dylib -Oz -mmacosx-version-min=10.10 -stdlib=libstdc++ -o $(LIBFILENAME) $(LIBOBJECTS) -lc')

        # http://web.archive.org/web/20170102013425/https://code.google.com/archive/p/oscpack/issues/15
        tools.patch(patch_file='udpsocket-get-port.patch', base_path=self.source_dir)

    def build(self):
        tools.mkdir(self.install_dir)
        tools.mkdir('%s/lib' % self.install_dir)
        with tools.chdir(self.source_dir):
            self.run('make install PREFIX=../%s' % self.install_dir)
        with tools.chdir(self.install_dir):
            self.run('rm lib/liboscpack.so')
            self.run('mv lib/liboscpack.so.1.1.0 lib/liboscpack.dylib')

    def package(self):
        self.copy('*.h',     src='%s/include' % self.install_dir, dst='include')
        self.copy('*.dylib', src='%s/lib'     % self.install_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['oscpack']
