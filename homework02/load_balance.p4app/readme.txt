In this problem, there are 1 client and 2 servers. We want the packet whose TCP source port is 0xb___, 0xc___ or 0xd___ be received by server h2, and the packet whose TCP source port is 0xe___ or 0xf___ be received by server h3.

For example, in the script 'send.py', the code would randomly select a number between 49152 and 65535 to be the source port number. If the program selects 55537 to be the source port number, since 55537 is equal to 0xd8f1, the packet would be transmitted to the server h2. If the program selects the number 60893, which is equal to 0xeddd, the switch would transmit the packet to server h3.

To test the code, we can type

""""""""""""""""""""""""""""""
sudo ./p4app exec m h2 /tmp/receive.py

sudo ./p4app exec m h3 /tmp/receive.py 

""""""""""""""""""""""""""""""
and

""""""""""""""""""""""""""""""

sudo ./p4app exec m h1 /tmp/send.py 10.0.0.99 "Hello World"

""""""""""""""""""""""""""""""

We will find out that either h2 or h3 would receive the packet. 

