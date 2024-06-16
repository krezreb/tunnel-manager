#!/usr/bin/env python3

import os
import yaml
import time
from subprocess import Popen, PIPE

from multiprocessing import Process
import sys


def log(prefix, msg):
    for l in msg.splitlines():
        print("{}: {}".format(prefix, l))


def run(cmd, splitlines=False):
    # you had better escape cmd cause it's goin to the shell as is
    proc = Popen([cmd], stdout=PIPE, stderr=PIPE,
                 universal_newlines=True, shell=True)
    out, err = proc.communicate()
    if splitlines:
        out_split = []
        for line in out.split("\n"):
            line = line.strip()
            if line != '':
                out_split.append(line)
        out = out_split

    exitcode = int(proc.returncode)

    return (out, err, exitcode)


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)


def run_with_agent(cmd: str):
    """
    Run the given command in a shell session with a running ssh-agent
    :param cmd:     The command to run
    :return:        The stdout of the process
    """
    return run("eval `ssh-agent -s` && " + cmd)


def tunnelDaemon(host, dynamic_ports=[], local_ports=[], remote_ports=[], keepalive=60, with_agent=False, connect_timeout=30):

    cmd = ["ssh"]
    cmd.append("-N")
    cmd.append("-o ExitOnForwardFailure=yes")
    cmd.append("-o ConnectTimeout={}".format(connect_timeout))
    # cmd.append("-4")

    try:
        if keepalive > 0:
            cmd.append("-o ServerAliveInterval={}".format(keepalive))
    except:
        pass

    port_count = 0

    for p in dynamic_ports:
        cmd.append("-D")
        cmd.append("{}".format(p))
        port_count += 1

    for p in local_ports:
        cmd.append("-L")
        p1, p2 = p.split(":")
        cmd.append("{}:127.0.0.1:{}".format(p1, p2))
        port_count += 1

    for p in remote_ports:
        cmd.append("-R")
        cmd.append("{}".format(p))
        port_count += 1

    cmd.append(host)

    if port_count == 0:
        log(host, "No ports configured, nothing to do")
        return False

    while True:
        log(host, "Starting tunnel...")
        (out, err, exitcode) = tunnelProcess(cmd, with_agent)

        log(host, "Tunnel exited with error code {}".format(exitcode))
        log(host, err)
        log(host, out)

        log(host,  "Retrying in 10 seconds...")
        time.sleep(10)


def tunnelProcess(cmd=[], with_agent=False):
    # print (" ".join(cmd))
    if run_with_agent:
        (out, err, exitcode) = run_with_agent(" ".join(cmd))
    else:
        (out, err, exitcode) = run(" ".join(cmd))
    return (out, err, exitcode)


if __name__ == '__main__':

    conf_file = os.path.expanduser('~')+"/.ssh/tunnels.yml"

    with open(conf_file) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    # print (conf)

    for t in conf["tunnels"].keys():
        print(t)

        try:
            host = conf["tunnels"][t]["host"]
        except KeyError:
            host = t

        try:
            dynamic_ports = conf["tunnels"][t]["dynamic"]
        except KeyError:
            dynamic_ports = []

        try:
            local_ports = conf["tunnels"][t]["local"]
        except KeyError:
            local_ports = []

        try:
            remote_ports = conf["tunnels"][t]["remote"]
        except KeyError:
            remote_ports = []

        try:
            keepalive = int(conf["tunnels"][t]["keepalive"])
        except:
            try:
                keepalive = int(conf["defaults"]["keepalive"])
            except:
                keepalive = 60

        try:
            timeout = int(conf["tunnels"][t]["timeout"])
        except:
            try:
                timeout = int(conf["defaults"]["timeout"])
            except:
                timeout = 10

        try:
            with_agent = conf["tunnels"][t]["ssh_agent"]
        except KeyError:
            with_agent = False

        p = Process(target=tunnelDaemon, args=(host, dynamic_ports,
                    local_ports, remote_ports, keepalive, with_agent, timeout))
        p.start()
        # p.join()
