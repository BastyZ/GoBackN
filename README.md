# Go Back N Client

This project is an implementation of a Go Back N client over **UDP** by using Python 3. It also implements the Karn's 
algorithm to improve timeout between packages retransmissions based on the round time trip (RTT) of the successfully
received packages.

In brief, the main objective of this client is to send a file over UDP to a **server** simulating TCP over UDP, i.e., 
tries to ensure the integrity of the sent message to the server by using an unreliable protocol.

Before using our client, you need to know our implementation has only be tested using text files. It works slowly (but
surely), and it does not manage congestion or flow control. In other words, it means that transmission speed of
data depends on the initial parameters given by the user. 

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

Below you'll find the default values of our client where you **must** pass the path to the file to be transmitted:
```
-A = localhost
-W = 10
-P = 10
-S = 3
-I = 3020
-O = 2030
```

## Brief explanations and assumptions
This client sends and receives messages at different threads, keeping track of sent messages by using a window of 
fixed size. This window is a *shared resource* for both threads, this means that a thread must acquire the window's
 lock in order to be able to use it, releasing it after finish its usage.

Our most important assumption is that the server will be fine receiving messages for a given window size, if the server
can't keep track of the sent messages at the beginning (freezing the advance of the file transfer due to throughput), 
the transfer _must_ be canceled and started again, with a smaller window size. In our tests works fine with 10 as window 
size, but collapses for windows of size greater than 150.

On the other hand, it is assumed the file to be sent is a plain text file (as a `.txt` for example), so we don't assure
this client will work perfectly for other file types.  

### Sender Thread
This thread asks to the window object for a package waiting to be sent. It also contains a timer which is started using 
a timeout (calculated using Karn's algorithm) whom when it's reached retransmits all the packages of the window.

### Receiver Thread
This thread receives ACKs (which contains a sequence number and its respective checksum) from the server and checks the 
integrity of incoming packages by calculating the checksum of the sequence number and checking if it matches the
checksum that comes with it.

If the ACK is not corrupt, then delegates the final verification to the window, finally waiting for the next ACK.  

### Window Object
This object is the core of our implementation. It handles the advancement of the window while receiving ACKs by loading
more packages waiting to be sent (if there is any left). Also records shipping and receiving times of packages
to update the retransmission timeout (calculated by the Karn Computation object).

### Other objects and functions
There are other objects that helps the computation of specific tasks, an example of this is the Karn Calculator that 
implements Karn's algorithm which is used by Window object. You will also find the `checksum ` function that 
computes _md5_ checksum of a given string, and it's used to compute the checksum of sequence number as well as data
 sent to the server. 

