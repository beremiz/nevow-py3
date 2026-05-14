
Divmod Nevow
============

This Beremiz-focused fork keeps only the server-rendered Nevow and formless
pieces used by Beremiz runtime.

Removed from this fork are the legacy or unused parts of upstream Nevow,
including Athena/COMET support, canvas/ActionScript support, example and
documentation trees, obsolete CI packaging files, and unrelated compatibility
layers.

Installation
------------

Before installing Nevow, you should install `Twisted`_, unless you are going to
write very simple CGI applications. Nevow integrates fully with the twisted.web
server providing easy deployment.

Nevow uses the standard distutils method of installation::

    python setup.py install

Validation
----------

The remaining smoke tests can be run with Twisted Trial::

    python -m twisted.trial nevow.test.test_package

.. _`Twisted`: http://twistedmatrix.com/
