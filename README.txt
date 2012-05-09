Introduction
============

**mr.laforge** is a utility and plugin for `supervisord`_.

It let's you easily make sure that ``supervisord`` and specific processes
controlled by it are running from within shell and Python scripts.

The plugin part adds a ``kill`` command to send signals to processes.

.. _`supervisord`: http://supervisord.org/


Usage
=====

Installation as a script
------------------------

One way to use it, is by installing it as a script. That's also the way to use
it in shell scripts. You can either just install it as an egg or you can
install it in a buildout::

    [mr.laforge]
    recipe = zc.recipe.egg
    eggs = mr.laforge

Either way you will get a ``supervisorup`` and a ``waitforports`` script.

Running ``supervisorup`` without arguments will check whether ``supervisord``
is running and if not will start it. You can also provide process names on the
command line and those will be started if they are not already running.

With ``waitforports`` you can check whether one or more processes are listening
on the specified ports. The script has some additional arguments you can list
with ``-h`` or ``--help``.

You can set the ``supervisor_args`` keyword argument to set supervisor arguments
for the ``supervisorup`` script like the config file location::

    [mr.laforge]
    recipe = zc.recipe.egg
    eggs = mr.laforge
    arguments = supervisor_args=['-c', 'etc/my_supervisord.conf']

Usage from a Python script
--------------------------

You can use the ``up`` method in ``mr.laforge`` which similar to the
``supervisorup`` script takes process names as arguments.

One example is a `zc.recipe.testrunner`_ part in a buildout like this::

    [test]
    recipe = zc.recipe.testrunner
    eggs =
        ...
        mr.laforge
    initialization =
        import mr.laforge
        mr.laforge.up('solr-test')

As you can see, you have to add the egg, so it can be imported by the
initialization code added to the ``test`` script created by
`zc.recipe.testrunner`_. The ``up`` call gets ``solr-test`` as an argument
to make sure that the ``solr-test`` process is running for the tests.

Another example is an initialization snippet in a script created by
`zc.recipe.egg`_::

    [paster]
    recipe = zc.recipe.egg
    eggs =
        ...
        mr.laforge
    dependent-scripts = true
    scripts = paster
    initialization =
        import mr.laforge
        mr.laforge.up('solr')

Now everytime you run the ``paster`` script created by this, it's checked that
``supervisord`` and the ``solr`` process controlled by it are running.

The equivalent for the ``waitforports`` script is ``mr.laforge.waitforports``.

.. _`zc.recipe.testrunner`: http://pypi.python.org/pypi/zc.recipe.testrunner
.. _`zc.recipe.egg`: http://pypi.python.org/pypi/zc.recipe.egg

Add as plugin to supervisord
----------------------------

To use the plugin part of mr.laforge, you have to add the following to your
supervisord config::

    [rpcinterface:laforge]
    supervisor.rpcinterface_factory = mr.laforge.rpcinterface:make_laforge_rpcinterface

    [ctlplugin:laforge]
    supervisor.ctl_factory = mr.laforge.controllerplugin:make_laforge_controllerplugin

You have to make sure that mr.laforge is importable by supervisord. In a
buildout you would have to add the egg to supervisor like this::

    [supervisor]
    recipe = zc.recipe.egg
    eggs =
        supervisor
        mr.laforge

Now you can use the ``kill`` command::

    ./bin/supervisorctl kill HUP nginx
