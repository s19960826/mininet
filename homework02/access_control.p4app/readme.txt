In this program we want to drop the packet which has IPv4 source address 10.0.1.10.

To test the program, just run

""""""""""""""""""""""""""""""""""""""
sudo ./p4app exec m h1 /tmp/receive.py

""""""""""""""""""""""""""""""""""""""
and

""""""""""""""""""""""""""""""""""""""
sudo ./p4app exec m h2 /tmp/send.py 10.0.0.10 "Hello World"

""""""""""""""""""""""""""""""""""""""

We can find out that there is nothing happen on h1's terminal. 
However, if we let h1 run 'send.py', and let h2 run 'receive.py', the packet's information will be displayed on h2's terminal, which means that h2 receives the packet.

If we don't want to drop the packet by its IPv4 source address, but decide to drop the packet who's TCP destination port is 1234, we can

1. uncomment the following code in 'access_control.p4'

"""""""""""""""""""""""""""""""""""""
/*hdr.tcp.dport: exact;*/ (line 50)

//if (hdr.tcp.isValid()) { (line 61)
//    acl.apply();
//}

""""""""""""""""""""""""""""""""""""""


2. comment the following code in 'access_control.p4'

""""""""""""""""""""""""""""""""""""""
acl.apply(); (lin3 59)

""""""""""""""""""""""""""""""""""""""


3. change the following code in 's1.config' from

""""""""""""""""""""""""""""""""""""""
table_add acl _drop 10.0.1.10 => 

""""""""""""""""""""""""""""""""""""""

to 

""""""""""""""""""""""""""""""""""""""

table_add acl _drop 1234 =>

""""""""""""""""""""""""""""""""""""""


If we want to test the code, we can change the value of dport in 'send.py'. If dport = 1234, all packets will be droped.
