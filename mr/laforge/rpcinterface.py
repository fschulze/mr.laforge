from supervisor.options import split_namespec
from supervisor.rpcinterface import isRunning, make_allfunc
from supervisor.states import RUNNING_STATES
from supervisor.supervisord import SupervisorStates
from supervisor.xmlrpc import Faults
from supervisor.xmlrpc import RPCError
import signal


API_VERSION = '0.1'


class LaForgeRPCInterface(object):
    def __init__(self, supervisord):
        self.supervisord = supervisord

    def _update(self, text):
        if self.supervisord.options.mood < SupervisorStates.RUNNING:
            raise RPCError(Faults.SHUTDOWN_STATE)

    def getAPIVersion(self):
        """ Return the version of the RPC API used by mr.laforge

        @return string  version
        """
        self._update('getAPIVersion')
        return API_VERSION

    def getMrLaForgeVersion(self):
        """ Return the version of the mr.laforge package

        @return string version version id
        """
        self._update('getMrLaForgeVersion')
        import pkg_resources
        return pkg_resources.get_distribution("mr.laforge").version

    def _getGroupAndProcess(self, name):
        # get process to start from name
        group_name, process_name = split_namespec(name)

        group = self.supervisord.process_groups.get(group_name)
        if group is None:
            raise RPCError(Faults.BAD_NAME, name)

        if process_name is None:
            return group, None

        process = group.processes.get(process_name)
        if process is None:
            raise RPCError(Faults.BAD_NAME, name)

        return group, process

    def _getSignalFromString(self, name):
        try:
            return int(name)
        except ValueError:
            pass
        name = name.upper()
        sig = getattr(signal, name, None)
        if isinstance(sig, int):
            return sig
        sig = getattr(signal, "SIG%s" % name, None)
        if isinstance(sig, int):
            return sig

    def killProcess(self, name, signal):
        """ Send signal to a process

        @param string signal Signal identifier
        @param string name Process name (or 'group:name', or 'group:*')
        @return boolean result     Always true unless error

        """
        self._update('killProcess')
        group, process = self._getGroupAndProcess(name)
        if process is None:
            group_name, process_name = split_namespec(name)
            return self.killProcessGroup(signal, group_name)

        sig = self._getSignalFromString(signal)

        if sig is None:
            raise RPCError(Faults.BAD_ARGUMENTS, signal)

        killed = []
        called  = []
        kill = self.supervisord.options.kill

        def killit():
            if not called:
                if process.get_state() not in RUNNING_STATES:
                    raise RPCError(Faults.NOT_RUNNING)
                # use a mutable for lexical scoping; see startProcess
                called.append(1)

            if not killed:
                kill(process.pid, sig)
                killed.append(1)

            return True

        killit.delay = 0.2
        killit.rpcinterface = self
        return killit # deferred


    def killProcessGroup(self, name, signal):
        """ Send signal to all processes in the group named 'name'

        @param string signal      Signal identifier
        @param string name        The group name
        @return struct result     A structure containing start statuses
        """
        self._update('killProcessGroup')

        group = self.supervisord.process_groups.get(name)

        if group is None:
            raise RPCError(Faults.BAD_NAME, name)

        processes = group.processes.values()
        processes.sort()
        processes = [ (group, process) for process in processes ]

        killall = make_allfunc(processes, isRunning, self.killProcess, signal=signal)

        killall.delay = 0.05
        killall.rpcinterface = self
        return killall # deferred


def make_laforge_rpcinterface(supervisord, **config):
    return LaForgeRPCInterface(supervisord)
