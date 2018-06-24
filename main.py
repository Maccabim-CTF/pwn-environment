import argparse
import os
from DockerFile import DockerFile
from ChallangeBuild import ChallangeBuild


def main(directory=None, is_compile=False, is_move_flags=False, docker_name='', no_cache=False, build_run=False, port='13377'):

    if not directory:
        directory = os.getcwd()

    with ChallangeBuild(directory=directory, is_compile=is_compile, is_move_flags=is_move_flags) as challange_handle:
        if build_run:
            if not docker_name:
                raise Exception("missing docker name")
        with DockerFile(sources=challange_handle.sources, docker_name=docker_name, no_cache=no_cache, build_run=build_run, port=port) as docker_handle:
            print challange_handle.challanges
            print docker_handle.docker_name
            interactive = raw_input('execute `rm -f ~/.ssh/known_hosts` y/n?')
            if interactive == 'y':
                print 'rm -f ~/.ssh/known_hosts'
                os.system('rm -f ~/.ssh/known_hosts')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize linux ctf environment')
    parser.add_argument('-dir', '--directory', type=str, help='main directory', required=False, dest='directory')
    parser.add_argument('-c', '--compile', help='compile source files', required=False, dest='is_compile', action='store_true')
    parser.add_argument('-m', '--move', help='move flags files', required=False, dest='is_move_flags', action='store_true')

    parser.add_argument('-d', '--docker-name', help='docker name', required=False, dest='docker_name')
    parser.add_argument('-ca', '--no-cache', help='use cache when building docker', required=False, dest='no_cache', action='store_true')
    parser.add_argument('-r', '--build-run', help='build and run docker', required=False, dest='build_run', action='store_true')
    parser.add_argument('-p', '--port', help='running docker port', required=False, dest='port')
    main(**vars(parser.parse_args()))
