import argparse
from os import listdir
from os import path
import os


class ChallangeBuild(object):
    def __init__(self, directory, is_compile, is_move_flags):
        """
        Scan and build challanges
        :param directory:
        :param is_compile:
        :param is_move_flags:
        """
        if not directory:
            directory = os.getcwd()
        self.directory = directory
        self.challanges = None
        self.sources = None
        self.flags = None
        self.is_compile = is_compile
        self.is_move_flags = is_move_flags

    def __enter__(self):
        self.generate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def _move_flags(self):
        for f in self.flags:
            matching_source = filter(lambda sourcefile: f.split('_flag')[0] == sourcefile.split('.c')[0], self.sources)
            if matching_source:
                os.system('cp {flag_file} {challange_folder}/flag'.format(flag_file=f, challange_folder=f.split('_flag')[0]))

    def _compile_sources(self):
        for f in self.sources:
            os.system('rm -f -r {source_out}'.format(source_out=f.split('.c')[0]))
            os.system('mkdir -p {source_out}'.format(source_out=f.split('.c')[0]))
            #os.system('gcc {source} -fno-stack-protector -z execstack -o {source_out}/{source_out}'.format(source=f, source_out=f.split('.c')[0]))
            os.system('cp {source} {source_out}/{source}'.format(source=f, source_out=f.split('.c')[0]))

    def generate(self):
        folder_files = [f for f in listdir(self.directory) if path.isfile(path.join(self.directory, f))]
        self.sources = filter(lambda filename: filename.endswith('.c'), folder_files)
        self.flags = filter(lambda filename: filename.endswith('_flag'), folder_files)
        if self.is_compile:
            self._compile_sources()
        if self.is_move_flags:
            self._move_flags()


def main(directory=None, is_compile=False, is_move_flags=False):
    with ChallangeBuild(directory=directory, is_compile=is_compile, is_move_flags=is_move_flags) as handle:
        print handle.sources


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan directory and prepares Challanges & Flags')
    parser.add_argument('-d', '--directory', type=str, help='main directory', required=False, dest='directory')
    parser.add_argument('-c', '--compile', help='compile source files', required=False, dest='is_compile', action='store_true')
    parser.add_argument('-m', '--move', help='move flags files', required=False, dest='is_move_flags', action='store_true')
    main(**vars(parser.parse_args()))
