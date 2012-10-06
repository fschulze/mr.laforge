from supervisor.options import ClientOptions
from supervisor.xmlrpc import SupervisorTransport
import argparse
import os
import socket
import subprocess
import sys
import time
import xmlrpclib


def get_rpc(options):
    transport = SupervisorTransport(
        options.username,
        options.password,
        options.serverurl)
    return xmlrpclib.ServerProxy('http://127.0.0.1', transport)


def find_supervisord():
    process_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    supervisord = os.path.join(process_path, 'supervisord')
    if os.path.exists(supervisord):
        return supervisord
    supervisord = os.path.join(os.getcwd(), 'bin', 'supervisord')
    if os.path.exists(supervisord):
        return supervisord
    print >> sys.stderr, "Couldn't find supervisord"
    sys.exit(1)


def get_supervisor_args(kwargs):
    return kwargs.get('supervisor_args',
        os.environ.get('MR_LAFORGE_SUPERVISOR_ARGS', '').split())


def up(*args, **kwargs):
    if not args:
        args = sys.argv[1:]
    supervisor_args = get_supervisor_args(kwargs)
    options = ClientOptions()
    options.realize(args=supervisor_args)
    status = "init"
    while 1:
        try:
            rpc = get_rpc(options)
            rpc.supervisor.getPID()
            if status == 'shutdown':
                sys.stderr.write("\n")
            break
        except socket.error:
            if status == 'shutdown':
                sys.stderr.write("\n")
            sys.stderr.write("Starting supervisord\n")
            supervisord = find_supervisord()
            cmd = [supervisord] + supervisor_args
            retcode = subprocess.call(cmd)
            if retcode != 0:
                sys.exit(retcode)
            status = 'starting'
        except xmlrpclib.Fault as e:
            if e.faultString == 'SHUTDOWN_STATE':
                if status == 'init':
                    sys.stderr.write("Supervisor currently shutting down ")
                    sys.stderr.flush()
                    status = 'shutdown'
                else:
                    sys.stderr.write(".")
                    sys.stderr.flush()
                time.sleep(1)
    if len(args):
        for name in args:
            info = rpc.supervisor.getProcessInfo(name)
            if info['statename'] != 'RUNNING':
                print "Starting %s" % name
                try:
                    rpc.supervisor.startProcess(name)
                except xmlrpclib.Fault as e:
                    if e.faultCode == 60:  # already started
                        continue
                    print >> sys.stderr, e.faultCode, e.faultString
                    sys.exit(1)
            else:
                print >> sys.stderr, "%s is already running" % name


def down(*args, **kwargs):
    if not args:
        args = sys.argv[1:]
    supervisor_args = get_supervisor_args(kwargs)
    options = ClientOptions()
    options.realize(args=supervisor_args)
    status = "init"
    while 1:
        try:
            rpc = get_rpc(options)
            rpc.supervisor.getPID()
            if status == 'shutdown':
                sys.stderr.write("\n")
            break
        except socket.error:
            if status == 'shutdown':
                sys.stderr.write("\n")
            sys.stderr.write("Starting supervisord\n")
            supervisord = find_supervisord()
            cmd = [supervisord] + supervisor_args
            retcode = subprocess.call(cmd)
            if retcode != 0:
                sys.exit(retcode)
            status = 'starting'
        except xmlrpclib.Fault as e:
            if e.faultString == 'SHUTDOWN_STATE':
                if status == 'init':
                    sys.stderr.write("Supervisor currently shutting down ")
                    sys.stderr.flush()
                    status = 'shutdown'
                else:
                    sys.stderr.write(".")
                    sys.stderr.flush()
                time.sleep(1)
    if len(args):
        for name in args:
            info = rpc.supervisor.getProcessInfo(name)
            if info['statename'] != 'STOPPED':
                print "Stopping %s" % name
                try:
                    rpc.supervisor.stopProcess(name)
                except xmlrpclib.Fault as e:
                    # if e.faultCode == 60:  # already stopped
                    #     continue
                    print >> sys.stderr, e.faultCode, e.faultString
                    sys.exit(1)
            else:
                print >> sys.stderr, "%s is already stopped" % name


def shutdown(**kwargs):
    supervisor_args = get_supervisor_args(kwargs)
    options = ClientOptions()
    options.realize(args=supervisor_args)
    try:
        rpc = get_rpc(options)
        rpc.supervisor.shutdown()
        print >> sys.stderr, "Shutting down supervisor"
    except socket.error:
        print >> sys.stderr, "Supervisor already shut down"
    except xmlrpclib.Fault as e:
        if e.faultString == 'SHUTDOWN_STATE':
            print >> sys.stderr, "Supervisor already shutting down"


def waitforports(*args, **kwargs):
    if not args:
        args = sys.argv[1:]
    timeout = kwargs.get('timeout', 30)
    default_host = kwargs.get('host', 'localhost')
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeout', type=int, default=timeout)
    parser.add_argument('-H', '--default-host', default=default_host)
    parser.add_argument('ports', nargs='+')
    args = parser.parse_args(map(str, args))
    default_ip = socket.gethostbyname(args.default_host)
    timeout = args.timeout
    ports = set()
    for port in args.ports:
        if ':' in port:
            host, port = port.split(':')
            port = int(port)
            if not host.strip():
                ip = default_ip
            else:
                ip = socket.gethostbyname(host)
        else:
            port = int(port)
            ip = default_ip
        ports.add((ip, port))
    sys.stderr.write(
        "Waiting for %s " % ", ".join(
            "%s:%s" % x for x in sorted(ports)))
    sys.stderr.flush()
    while ports and timeout > 0:
        for ip, port in list(ports):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if s.connect_ex((ip, port)) == 0:
                ports.remove((ip, port))
            s.close()
        if ports:
            time.sleep(1)
            sys.stderr.write(".")
            sys.stderr.flush()
            timeout -= 1
    sys.stderr.write("\n")
    sys.stderr.flush()
    if ports:
        sys.stderr.write(
            "Timeout on %s\n" % ", ".join(
                "%s:%s" % x for x in sorted(ports)))
        sys.stderr.flush()
        sys.exit(1)
