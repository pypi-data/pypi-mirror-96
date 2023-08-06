Chat Relater
============

**Chat Relater** is a tool consisting of two command-line scripts:

* The analyzer extracts user relations from chat logs. The gained data
  is serialized as JSON.

* The visualizer takes that data, generates a DOT_ file, and calls the
  GraphViz_ application to render the graph in the requested output
  format (e. g. PDF, PNG, SVG).

It is actually a conceptual clone of the PieSpy_ Social Network Bot.
However, Chat Relater does not act as an IRC bot (although this could be
easily accomplished by making use of the irc_ package), but therefore
allows to be run on any logfiles that produce similar output to those
created by XChat_. Of course, this includes logs from Jabber, SILC or
any other communication (but it might require some minor changes to the
log reader).

The GraphViz_ usage is pretty basic and output may be improved somehow,
but so far, the graphs created by PieSpy_ look **much** nicer.


Requirements
------------

Python_ 3.7 or later is required.

Chat Relater can be installed via pip:

.. code:: sh

    $ pip install ChatRelater


Tests
-----

Install the test dependencies:

.. code:: sh

    $ pip install -r requirements-test.txt

Install the local source files as package in development mode:

.. code:: sh

    $ pip install -e .

Run the tests:

.. code:: sh

    $ pytest


Usage
-----

Run the analyzer on one or more log files, saving the intermediate
results to another file (``chat.json``):

.. code:: sh

    $ chatrelater-analyze -o chat.json chat_today.log chat_yesterday.log

Create a nice graph (using the 'twopi' program) from the results
(``chat.json``) and save it to a PNG image (``graph.png``):

.. code:: sh

    $ chatrelater-visualize -f png -p neato chat.json chat

And intermediate file containing the 'dot' description (``graph``) will
be created in the process.


.. _DOT:        https://www.graphviz.org/doc/info/lang.html
.. _GraphViz:   https://www.graphviz.org/
.. _PieSpy:     http://www.jibble.org/piespy/
.. _irc:        https://github.com/jaraco/irc
.. _XChat:      http://www.xchat.org/
.. _Python:     https://www.python.org/


:Copyright: 2007-2021 `Jochen Kupperschmidt <https://homework.nwsnet.de/>`_
:License: MIT, see LICENSE for details.
