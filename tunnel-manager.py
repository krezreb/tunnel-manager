#!/usr/bin/env python3

import os
import yaml
import time
import subprocess

from multiprocessing import Process
import sys


def log(prefix, msg):
    for l in msg.splitlines():
        print("{}: {}".format(prefix, l))


def run(cmd=[], splitlines=False):
    p = subprocess.run(cmd, capture_output=True)

    return  p.stdout, p.stderr, p.returncode


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


def tunnelDaemon(host, dynamic_ports=[], local_ports=[], remote_ports=[], keepalive=60, connect_timeout=30):

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
        (out, err, exitcode) = tunnelProcess(cmd)

        log(host, "Tunnel exited with error code {}".format(exitcode))
        log(host, err)
        log(host, out)

        log(host,  "Retrying in 10 seconds...")
        time.sleep(10)


def tunnelProcess(cmd=[]):
    # print (" ".join(cmd))

    out, err, exitcode = run(cmd)
    return out, err, exitcode


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

        p = Process(target=tunnelDaemon, args=(host, dynamic_ports,
                    local_ports, remote_ports, keepalive, timeout))
        p.start()
        # p.join()
