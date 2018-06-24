import argparse
import os

DOCKERFILE_TEMPLATE = """

FROM ubuntu:16.04
RUN apt-get update

WORKDIR /



RUN apt-get update && apt-get install -y openssh-server
RUN apt-get install -y sudo
RUN apt-get install -y python
RUN apt-get install -y gdb
RUN apt-get install -y git
RUN apt-get install -y vim
RUN apt-get install -y gcc
RUN apt-get install -y strace

RUN git clone https://github.com/longld/peda.git /usr/bin/peda
RUN echo "source /usr/bin/peda/peda.py" >> ~/.gdbinit
RUN chmod 0755 /usr/bin/peda/*.py
RUN chmod 0755 /usr/bin/peda/lib/*.py

RUN sysctl -w kernel.randomize_va_space=0

{challange_template}

RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN echo "export VISIBLE=now" >> /etc/profile
RUN sysctl -w kernel.dmesg_restrict=1
RUN chmod 1733 /tmp /var/tmp /dev/shm


EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
"""

CHALLANGE_TEMPLATE = """

COPY {challange_name}/* /home/{challange_name}/

RUN adduser {challange_name}
RUN adduser {challange_name}_root

RUN usermod -G {challange_name} {challange_name}
RUN usermod -G {challange_name}_root {challange_name}_root

RUN gcc -Wl,-z,norelro -no-pie -fno-stack-protector -z execstack -o /home/{challange_name}/{challange_name} /home/{challange_name}/{challange_name}.c

RUN chown {challange_name}_root /home/{challange_name}/flag
RUN chown {challange_name}_root:{challange_name} /home/{challange_name}/{challange_name}
RUN chown {challange_name}:{challange_name} /home/{challange_name}/{challange_name}.c
RUN chown root:root /home/{challange_name}_root

RUN chmod 0400 /home/{challange_name}/flag
RUN chmod 4550 /home/{challange_name}/{challange_name}
RUN chmod 0440 /home/{challange_name}/{challange_name}.c

RUN echo '{challange_name}:{challange_name}' | chpasswd
RUN echo '{challange_name}_root:root' | chpasswd

RUN echo "source /usr/bin/peda/peda.py" > /home/{challange_name}/.gdbinit

"""


class DockerFile(object):
    def __init__(self, sources, docker_name, no_cache, port, build_run):
        """
        Generate dockerfile
        :param sources:
        :param docker_name:
        :param no_cache:
        :param port:
        :param build_run:
        """
        self.sources = sources
        self.dockerfile = None
        self.docker_name = docker_name
        self.no_cache = '--no-cache' if no_cache else ''
        self.port = port
        self.build_run = build_run

    def __enter__(self):
        self.generate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def _format_template(self):
        challange_template = ''
        for f in self.sources:
            challange_template += CHALLANGE_TEMPLATE.format(challange_name=f.split('.c')[0])
        dockerfile = DOCKERFILE_TEMPLATE.format(challange_template=challange_template)
        self.dockerfile = dockerfile

    def _docker_build_run(self):
        interactive = raw_input('execute `sudo docker stop $(sudo docker ps -a -q) ; sudo docker rm $(sudo docker ps -a -q)` y/n?')
        if interactive == 'y':
            os.system('sudo docker stop $(sudo docker ps -a -q) ; sudo docker rm $(sudo docker ps -a -q)')
        os.system('sudo docker build {no_cache} -t {docker_name} .'.format(no_cache=self.no_cache, docker_name=self.docker_name))
        os.system('sudo docker run --privileged --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -d -p {port}:22 --name {docker_name} {docker_name}'.format(port=self.port, docker_name=self.docker_name))

    def generate(self):
        self._format_template()
        with open('Dockerfile', 'w') as f:
            f.write(self.dockerfile)

        if self.build_run:
            self._docker_build_run()


def main(sources, docker_name='', port='13337', no_cache=True, build_run=False):
    with DockerFile(sources=sources, docker_name=docker_name, port=port, no_cache=no_cache, build_run=build_run) as handle:
        print handle.sources


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan directory and prepares Challanges & Flags')
    parser.add_argument('-s', '--sources', help='challanges sources names', required=True, dest='sources')
    parser.add_argument('-d', '--docker-name', help='docker name', required=False, dest='docker_name')
    parser.add_argument('-ca', '--no-cache', help='use cache when building docker', required=False, dest='no_cache', action='store_false')
    parser.add_argument('-r', '--build-run', help='build and run docker', required=False, dest='build_run', action='store_true')
    parser.add_argument('-p', '--port', help='running docker port', required=False, dest='port')
    main(**vars(parser.parse_args()))
