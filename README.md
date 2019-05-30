# Go Back N Client

On this project there's a Go Back N client implementation on python 3, using __UDP__ instead of TCP as an Uni assignment, 
we implement Karn's algorithm for round-trip time measuring based on RFC 6298 with the objective of computing and 
managing our retransmission timer.

The objective of this client is successfully sent a file over UDP to a **server** recreating using TCP over UDP
and keeping the integrity and order of the file, the file is always assumed to be a text file. 

## Basic Usage
```
python goback.py [-A address] [-F file] [-W window] [-P packages] [-S Sequence] [-I receiver port] [-O sender port]
```

The details of the parameters are shown below:

```
arguments:
  -h, --help            show this help message and exit
  -A ADDRESS, --address ADDRESS
                        IP address of the server where the files will be sent
                        to.
  -F FILE, --file FILE  Path to the file to be sent.
  -W WINDOW, --window WINDOW
                        Integer representing size (packages number) of the
                        window. The window size will be constant.
  -P PACKAGES, --packages PACKAGES
                        Integer representing the size of the packages to be
                        sent.
  -S SEQUENCE, --sequence SEQUENCE
                        Integer representing the maximum number of digits of
                        the sequence numbers.
  -I RECEIVE, --receive RECEIVE
                        Integer representing the port number used to receive
                        the ACKs.
  -O SEND, --send SEND  Integer representing the port number where the data
                        will be sent to.
```

And it comes with the following default values, and you **must** pass an path file:
```
-A = localhost
-W = 10
-P = 10
-S = 3
-I = 3020
-O = 2030
```

## Brief explanations and assumptions
This client sends an receive messages from different threads, with a fixed window size. This window is a *shared 
resource* for both threads, and this thread must acquire a lock to use it, and release it when is not at use.

Our most important assumption is that the server will be fine receiving messages for a given window size, if the server
can't keep up at the start, freezing the advance of the file transfer due to throughput, the transfer _must_ be canceled
and started again, with a lower window size, in our test works with 10 as windows size, but no for 150 or more. The
other important assumption is that the file is a text file (as an `.txt` file), we don't assure that this client will
work for other types of files as well.  

### Sender Thread
This thread ask the window object for a package to be sent, and when a timeout is reached resents all the packages of
the window at that given moment.

### Receiver Thhread
This thread receives ACKs, checks its integrity seeing that the checksum of its sequence number is the same as the
one given by the ACK, if it isn't corrupt, it delegates it to the window, and then waits for the next ACK.

### Window Object
This is by far the most important object on this implementation, it handles the window advance when an ACK is received,
loads more packages to be send while there are left, records send and received times to timeout interval computation
by the Karn Computation object, and does _callbacks_ to the Sender Thread when packages have to be retransmitted.

### Other objects and functions
There are other objects that helps the computation of specific things, and example is the Karn Calculator that 
implements Karn's algorithm and it's used by the Window object, and `checksum ` function that computes the _md5_
checksum of a given string, and it's used to compute the checksum of sequence number as well as data sent to the server. 

