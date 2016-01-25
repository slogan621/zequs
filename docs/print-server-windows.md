Print Serving ID Cards on Windows
=================================

The current usage of this software in the Thousand Smiles clinics is based
on the print server running on a Windows 7 laptop. Various wall-mounted
tablets are located in our clinic. Volunteers use these tablets to perform
a PIN-based signin with our cloud based web-service. Our signin tablets are
configured to use the laptops where zequs is running as print servers. A Zebra 
ZXP series 1 ID card printer is connected to the USB port of the laptop, and 
Zebra printing software and drivers have been installed on the laptop. 

The instructions have been tested on Windows 7 systems, but should also work
on later Windows versions (8, 10, etc.).

This document assumes you have installed cygwin and pulled Zequs from our
git repository. 

Configuring Zequs as a Print Spooler
------------------------------------

From the cygwin prompt, cd to the location of the configuration file that is
supplied with zequs: 

$ cd zequs/misc

Copy zequs.conf to /etc:

$ cp zequs.conf /etc

Using vim (or other editor, feel free to use an editor from Windows Desktop,
but make sure it is configured to use Unix line endings) modify
/etc/zequs.conf to contain the following lines. The key things to note are:

In the [printer] section:

* uncomment spoolonly and make sure it is set to true
* set spooldir to a cygwin path (hint, from the Windows Explorer, you can
find /tmp/idcards by navigating to c:\\cygwin\tmp\idcards)
* set rotate to 0 (or comment it out)

In the [plugin] section, set the name to "template".

The following is a correctly configured /etc/zequs.conf that spools ID cards
to /tmp/idcards:

# /etc/zequs.conf example

[printer]

# if spoolonly is true, files are written to disk, job is marked as completed,
# and the printer driver is not called. This allows for the badges to be 
# sent to the print server to be spooled and then printed manually via some 
# other means, such as a system print dialog. This is useful if the printer is 
# not supported by a zequs plugin or there is some bug in the plugin that 
# prohibits it from working properly. Files written when spool is True are 
# never deleted by zequs and must be removed manually.

spoolonly: true

# store spooled badge image files in the following directory. Default is
# system dependent. spooldir should be system dependent as well, e.g., /tmp
# on Unix systems, or c:\somedir on Windows/DOS systems.

spooldir: /tmp

# rotate badge images number of degrees before writing to disc. Default is 0

#rotate: 90


[plugin]

# name of the plugin

name: template

Starting Zequs
--------------

Once the configuration file is created, start zequs.

Configuring the Client
----------------------

The client that is issuing print requests with Zequs' REST API should be
configured to point at the IP and port that zequs was started on.

Printing ID Cards
-----------------

The operator of the laptop will need to install whatever drivers and software
required by the ID card printer. For example, a user of Zebra ZXP Series 1 and
3 printers will need to obtain the drivers and software from Zebra that
support the printing of ID cards from the Windows print dialog. The drivers
for the series 1 are located at
https://www.zebra.com/us/en/support-downloads/card/zxp-series-1.html

The operator should have a Windows Explorer window open to view the directory
that images will be spooled to, this is specified in /etc/zequs.conf in the
[printer] section via the spooldir variable.

The operator can then print cards written by zequs by right clicking on the
badge images and using the standard Windows print dialog.
