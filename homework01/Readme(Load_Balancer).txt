
We assume that there are 30 hosts and 1 switch in the network. User can define the number of switch by changing the parameter "self.N" in the python code, but self.N should smaller than 99.

Our controller will choose the back-end servers through Round-robin.


Please test the program through following step:
1. run "./pox.py load_balancer" to setup the controller
2. run "sudo mn --topo single,30 --mac --switch ovsk --controller remote" to add hosts and a switch

We assume h1 is the client.
3. run "h1 arp -s 10.0.0.99 00:00:00:00:00:99"

We use 'ping' command to check whether the controller chooses the different back-end server.
4. run "h1 ping -c30 10.0.0.99".
   In the terminal, we can get a message:
    ""
        PING 10.0.0.99 (10.0.0.99) 56(84) bytes of data.
        64 bytes from 10.0.0.99: icmp_seq=1 ttl=64 time=48.2 ms
        ......
    ""
 
   In our progam, we print the chosen server's ip and ethernet address, so we can see the message like:
    
    ""
        [Request]: From 10.0.0.1 to 10.0.0.99
        The chosen server is 10.0.0.2
        00:00:00:00:00:02
    ""
    which means that server 10.0.0.2 is choosed. The message
    ""
        [Response]: Server 2 response
    ""
    means that the server change its source IP to 10.0.0.99 and respond to the client's request.

    Sometime we also can see the messsage like
    ""
       Normal Message from 10.0.0.1 to 10.0.0.2
    "" 
    which means that neither the packet source IP nor destination IP is 10.0.0.99.
  