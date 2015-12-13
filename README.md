Zequs
=====

A python 2.x based web service for printing badges to the Zebra ZXP series
1 and series 3 printers.

What is Zequs?
--------------

Zequs is the web-service component of software that would run on a Linux
server to which a Zebra ZXP printer is connected. It manages print jobs
and, via a command line interface that is implemented by a separate 
project (zequs-java-cli) that interfaces with a Java library provided by
Zebra that can control a Zebra ZXP printer.

Badge images are sent across the API as PNG files, a job is created and
stored in a sqlite3 database, and a thread drains the database printing
each badge image in order.

What is the status of Zequs?
----------------------------

Zequs is currently in development.

API Documentation
-----------------

See the wiki located here on github (TBD)

Why the name Zequs?
-------------------

It's a play on the genus of Zebras, Equus. I added Z to the front, taken
from the first letter of "Zebra", removed a "u" from equus, and noticed
that it read like "Zebra queues", which works because the service is in
effect managing a queue of print jobs for a Zebra.

Zequs is pronounced something like "Zeck us".


