Installing on Windows
=====================

This document covers installing and maintaining the software on Windows
systems.

The instructions have been tested on Windows 7 systems, but should also work
on later Windows versions (8, 10, etc.).

Install Cygwin
--------------

Visit https://cygwin.com/install.html and download the installer appropriate
for your version of Windows and CPU architecture.

From the setup program, find and install Python, which should be located in 
the interpreters category. Select any Python 2.x version that is greater than 
or equal to 2.7. Do not install Python 3.x. These instructions have been
tested with version 2.7.10-1

Also, install git. Git is located in the Devel category. Any version of git
will do.

If you have some diskspace and time, you can of course install all of cygwin. 

When prompted, allow Cygwin installer to create Desktop and Start Menu items.

Verifying the Cygwin Install
----------------------------

Double click the Cygwin terminal from your desktop that was installed by 
cygwin. This will launch a terminal window that accepts Unix-like commands.

To test if Python was installed, from the terminal prompt, type:

$ python --version

Python should display something like:

Python 2.7.6

Next, verify git was installed:

$ git --version
git version 1.9.1

Downloading and Installing Zequs
--------------------------------

Launch the cygwin terminal from your desktop. Then type:

$ git clone git@github.com:slogan621/zequs.git

You should see something like this:

Cloning into 'zequs'...
remote: Counting objects: 117, done.
remote: Total 117 (delta 0), reused 0 (delta 0), pack-reused 117
Receiving objects: 100% (117/117), 47.07 KiB | 0 bytes/s, done.
Resolving deltas: 100% (64/64), done.
Checking connectivity... done.
$

Configuring Zequs
-----------------

Zequs is configured via a configuration file named /etc/zequs.conf (in 
DOS or Windows, this file is c:\\cygwin\etc\zequs.conf). 

A template is located in the repository pulled by git. We suggest you
copy the file zequs/misc/zequs.conf to /etc and then edit it. Comments
in the file should guide you in configuring this file. Specific directions
for configuring Zequs as a print spooler are located in the file named
print-server-windows.md 

Starting Zequs
--------------

The following steps should be used to start Zequs:

* Launch a cygwin terminal
* Determine your IP address:

$ ipconfig

(we'll assume the IP address of the laptop is 192.168.1.100)

* cd in the zequs directory:

$ cd zequs

* start zequs

$ python server.py 8081 192.168.1.100

Stopping Zequs
--------------

In a separate cygwin terminal:

$ ps | grep python

The first number reported on the output line is the PID. Using this PID

$ kill -9 PID

For more information
--------------------

See the document print-server-windows.md for more details on how to configure
and use zequs on Windows as a print server (until a plugin for printing 
directly to a printer is developed, print spooling is the only supported 
mode).

