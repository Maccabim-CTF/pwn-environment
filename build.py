import argparse
import os
from zipfile import ZipFile
import time


def main(directory=None, name=None):
    if not directory:
        directory = os.getcwd()
    if not name:
        name = time.strftime('mctf_env_%d_%m_%Y_%H_%M_%S')

    with ZipFile('{name}.zip'.format(name=name), 'w') as env_zip:
        for root, sub_dirs, files in os.walk(directory):
            if '.idea' in root:
                continue
            for f in files:
                if 'mctf_env' in f:
                    continue
                print 'file:{file}'.format(file=f)
                env_zip.write(filename=os.path.join(root, f), arcname=f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Zip current version of linux ctf environment')
    parser.add_argument('-d', '--directory', type=str, help='main directory', required=False, dest='directory')
    parser.add_argument('-n', '--name', type=str, help='zip name', required=False, dest='name')
    main(**vars(parser.parse_args()))
