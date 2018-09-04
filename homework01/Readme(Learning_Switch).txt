
Here we assume that the network topology is a tree structure with 3 switches, but user can define their own network topology.

In our program, we use the hash table to map the MAC address and port. When the controller get a message from switch, it will check whether the source host's MAC address is in the hash table. If the MAC address is not in the hash table, it will put the MAC address and the port in the hash table.

When the controller want to find the destination port, it will check the hash table. If the record is in the table, the controller will ask the switch send the packet through the destination port. Otherwise, the switch will broadcast the packet.


Please test the program through following step:
1. run "./pox.py learning_switch" to setup the controller
2. run "sudo mn --topo tree,2 --mac --switch ovsk --controller remote" to add hosts and a switch
3. run "h1 ping h3"

   In the controller's terminal, we can see   

   """
   S2:destination port not exist. Broadcast the packet
   S3:destination port not exist. Broadcast the packet
   S1:destination port not exist. Broadcast the packet
   S1: Install flow from Port 2 to Port 1
   S3: Install flow from Port 3 to Port 1
   S3: Install flow from Port 1 to Port 3
   ........
   """

   The first few messages are the broadcast messages. When the controller can recognize the destination port, it will install flow in the flow table.  
