from supervisor.options import split_namespec
from supervisor.supervisorctl import ControllerPluginBase
from supervisor import xmlrpc
import xmlrpclib


class LaForgeControllerPlugin(ControllerPluginBase):
    def __init__(self, controller):
        self.ctl = controller
        self.laforge = controller.get_server_proxy('laforge')

    def _killresult(self, result):
        name = result['name']
        code = result['status']
        template = '%s: ERROR (%s)'
        if code == xmlrpc.Faults.BAD_NAME:
            return template % (name, 'no such process')
        elif code == xmlrpc.Faults.BAD_ARGUMENTS:
            return template % (name, 'signal not defined')
        elif code == xmlrpc.Faults.NOT_RUNNING:
            return template % (name, 'not running')
        elif code == xmlrpc.Faults.SUCCESS:
            return '%s: signal sent' % name
        # assertion
        raise ValueError('Unknown result code %s for %s' % (code, name))

    def do_kill(self, arg):
        if not self.ctl.upcheck():
            return

        args = arg.strip().split()
        if not args:
            self.ctl.output("Error: kill requires a signal and process name")
            self.help_kill()
            return

        signal = args[0]
        names = args[1:]

        if not names:
            self.ctl.output("Error: kill requires a process name")
            self.help_start()
            return

        for name in names:
            group_name, process_name = split_namespec(name)
            if process_name is None:
                results = self.laforge.killProcessGroup(group_name, signal)
                for result in results:
                    result = self._killresult(result)
                    self.ctl.output(result)
            else:
                try:
                    result = self.laforge.killProcess(name, signal)
                except xmlrpclib.Fault, e:
                    error = self._killresult({'status':e.faultCode,
                                               'name':name,
                                               'description':e.faultString})
                    self.ctl.output(error)
                else:
                    self.ctl.output('%s: signal sent' % name)

    def help_kill(self):
        self.ctl.output("kill <signal> <name>\t\tSend signal to a process")
        self.ctl.output("kill <signal> <gname>:*\t\tSend signal to all processes in a group")
        self.ctl.output(
            "kill <signal> <name> <name>\tSend signal to multiple processes or groups")


def make_laforge_controllerplugin(controller, **config):
    return LaForgeControllerPlugin(controller)
