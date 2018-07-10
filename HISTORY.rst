Changelog
=========

0.8 - 2018-07-10
----------------

* Fix ``do_kill`` for Python 3.x.
  [fschulze]


0.7 - 2018-07-02
----------------

* Add Python 3.x support.
  [fschulze]

* Add timeout to socket, so we don't hang on unavailable hosts.
  [fschulze]


0.6 - 2012-10-06
----------------

* Added ``supervisordown`` script and matching ``down`` method to make sure a
  process is stopped.
  [fschulze]


0.5 - 2012-05-23
----------------

* Allow setting supervisor arguments via the ``MR_LAFORGE_SUPERVISOR_ARGS``
  environment variable.
  [witsch]

* Added ``shutdown`` function to shutdown supervisord from Python code.
  [fschulze]


0.4 - 2012-05-09
----------------

* Added waitforports script and function to wait until a process is listening
  on specified ports.
  [fschulze, witsch]


0.3 - 2012-04-03
----------------

* Don't pass command line options to supervisor code.
  [fschulze]

* Add supervisor_args keyword argument to ``up`` function.
  [fschulze, witsch (Andreas Zeidler)]


0.2 - 2011-04-20
----------------

* Added supervisord plugin with ``kill`` command to send signals to processes.
  [fschulze]


0.1 - 2011-04-20
----------------

* Initial release
