from supervisor.options import ClientOptions
from supervisor.xmlrpc import SupervisorTransport
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


def up(*args, **kwargs):
    if not args:
        args = sys.argv[1:]
    supervisor_args = kwargs.get('supervisor_args', [])
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
