
We assume that there are 3 hosts in the network. We add one more host here to make sure that the traffic flow won't be blocked when server and cleint are both trusted.

Please test the program through following step:

1. run "./pox.py firewall" to setup the controller
2. run "sudo mn --topo single,3 --mac --switch ovsk --controller remote" to add hosts and a switch
3. run "xterm h1 h2 h3"

We assign h1 to be the TCP server, h2 and h3 be the client.
4. run "iperf -s -i -1" on h1's terminal. 
   We will see the message "Server listening on TCP...."
5. run "iperf -c 10.0.0.1 1m 1000" on h3's terminal.
   We will see the message "local 10.0.0.0 port 5001 connected with 10.0.0.3 port 35644" and some Bandwith information on h1's terminal. We also can see the similar message on h3's terminal.
6. run "iperf -c 10.0.0.1 1m 1000" on h3's terminal. 
   We will find out there is nothing happen on h1's terminal, and there is a message "WARNING: did not receive ack of last datagram afte 10 tries.", because our controller block all packets from h2.


Now we assume that h2 is the UDP server (It can also be the TCP server, but the result is the same)
7. run "iperf -s -u -i 1" on h2's terminal
8. run "iperf -c 10.0.0.2 -u -b 1m 1000" on h3's terminal.
   We will get a warning message on h3's terminal. Although h3 send a request to h2, the controller blocks the ACK . Therefore h3 cannot receive any response.

   
