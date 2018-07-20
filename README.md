# Gopher Project
This repository contains a gopher client and server, as well as the "root" directory with .links files and downloadables
used by the server.

Currently the repository contains the following files:
* SimpleTCPClient.py -- a simple TCP client.
* SimpleTCPServer.py -- a simple TCP server.

After our original submission, we made the following changes:
* Client:  Displays files in the command line rather than downloading them
* Client:  Sends <CR><LF> on empty line
* Client:  Improved connections with servers such as quux.org's
* Client:  No longer breaks on decode errors.  If it cannot decode a specific character, it does not render it.
* Server:  Handles errors more rigorously, including errors from over-length inputs
* Server:  Ends error messages with <CR><LF>
* Server:  Sorts lines from a .links file before sending them
* Other:  Tidied some of the files which can be downloaded from our server and their encodings