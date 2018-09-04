---
layout: single
permalink: homework02.html
title: P4 Switch Project      
---

# Changelog

* v1: October 31, 2017
    
# Overview    
    
In this assignment, you will start building a fairly sophisticated
network switch in P4. Later on, we will extend this switch with
additional features, using the following schedule:
    
* Phase I: Released October 31; Due November 9th.
* Phase II: Released November 7th; Due November 21th.
* Phase III: Due December 1st

For the purposes of assigning course grades, Phases I will serve as
the 2nd homework assignments, Phase II as the 3rd homework assignment,
and Phase III will serve as the course project.

The project may be completed individually or with a partner. However,
If you choose to work with a partner, you must register on CMS, you
must complete all phases of the project as a team, and both members of
the partnership must make significant contributions to the solution.

# Academic Integrity    

All work you submit must be your own and sharing or receiving code is
forbidden, with the exception of your partner. Do not look for or
submit code you find on the Internet, and do not post solutions or
partial solutions on the discussion site. If you make use of _any_
outside materials, you must give proper attribution. You may ask
general questions about the development environment, `p4app`, `p4c`,
`bmv2`, Mininet, etc., and you may discuss high-level details of the
exercises with your classmates. If you have any questions about what
is allowed and what is not allowed, please ask the instructor first!

# Software Setup

To complete this assignment, we suggest using `p4app`, an environment
for developing P4 applications implemented using Docker. To get
started, you will need to install several software packages:

* [https://docker.com](https://docker.com)
* [https://github.com/p4lang/p4app](https://github.com/p4lang/p4app)    
    
If you prefer to have a deeper understanding of how `p4app` works
under the hood, you are also free to install and configure Mininet,
the P4 compiler (`p4c`), and software switch (`bmv2`) on a VM
manually:

* [https://github.com/mininet/mininet](https://github.com/mininet/mininet)
* [https://github.com/p4lang/p4c/](https://github.com/p4lang/p4c/)
* [https://github.com/p4lang/bmv2/](https://github.com/p4lang/bmv2/)

However, the rest of the instructions for the assignment assume you
will be using `p4app`.

# Starter Code

You can download starter code for the two programming exerises in this
assignment as a zipfile from CMS.
                
# P4 Overview

This section presents a high-level overview to the P4 language. It can
be skimmed (or skipped) on a first reading and referred back to as
needed.

## Introduction

P4 is a domain-specific language for specifying the behavior of
programmable data planes. It provides general imperative programming
constructs (variables, assignment, conditionals, etc.) as well as
network-specific packet-processing constructs (parsers, match-action
tables, etc.) This section contains a hands-on introduction to some of
the main features of language. However, for a full description, you
should consult the [language
specification](https://p4lang.github.io/p4-spec/) document.

## Types

P4 is a statically-typed language. Every component of a P4 program has
a type that is checked at compile time, and programs that are
ill-typed are rejected by the compiler.

### Primitive Types

Because packet-processing often involves manipulating bits in packet
headers, P4 provides a rich collection of types for describing various
kinds of packet data including:

* `bit<N>`: unsigned integers of width `N`, 
* `int<N>`: signed integers of width `N`, and 
* `int`: arbitrary-precision, signed integers
    
Integer literals can be written in binary (`0b`), octal (`0o`),
decimal, or hex (`0x`) notation. Programmers may also optionally
specify the width of an integer iteral---e.g., `8w0xF`, which
specifies the encoding of `15` as an 8-bit unsigned integer.

The type `int` is an internal type used by the compiler for integer
literals; it cannot be written directly by the programmer.

Signed operations are carried out using twos-complement arithmetic and
most operations truncate the result in the case of arithmetic
overflow.

To convert a value from one type to another, P4 provides casts between
different primitive types: e.g., `(bit<4>) 8w0xF` produces the
encoding of `15` as a 4-bit unsigned integer.

### Header Types

Packets typically comprise a sequence of _headers_, each of which are
a sequence of _fields_. P4 provides a special built-in type for
representing headers, using syntax that resembles C `struct`s:
```
header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}
```
Each component of a header can be accessed using standard "dot"
notation---e.g., if `ethernet` has type `ethernet_t`, then
`ethernet.dstAddr` denotes the destination address.

A header values can be in one of two states, valid or invalid, and are
initially invalid. Reading a field of an invalid header produces an
undefined value. A header can be made valid using operations such as
`isValid()`, `setValid()` and `setInvalid()`, or by `extract`ing it in
the parser (as explained below).

### Typedefs and Structs

To support giving convenient names to commonly-used types, P4 provides
type definitions:
```
typedef bit<48> macAddr_t;    
```
With this declaration, the types `bit<48>` and `macAddr_t` are
synonyms that are treated as equivalent by the type checker.

P4 also provides standard C-style structs, which are defined as follows:
```
struct headers_t {
  ethernet_t ethernet;
  ipv4_t ipv4;
}        
```
Unlike a header, a `struct` does not have a built-in notion of validity.

### Header Stacks and Unions

P4 provides several derived types including header _stacks_ and
_unions_. A _header stack_ is similar to an array, but comes with
additional operations that can be used when parsing packets. If
`header` is a header type, then the type `header[N]` denotes a header
stack type, where `N` must be an integer literal. If `stack` is an
expression whose type is a header stack then:

* `stack[i]`: denotes the header at index `i`,
* `stack.size`: denotes the size of the header stack,
* `stack.push_front(n): shifts `stack` "right" by `n`, making the `n`
   entries at the front of the stack invalid, and
* `stack.pop_front(n): shifts `stack` "left" by `n`, making the `n`
   elements at the end of the stack invalid.
    
In addition, within a parser (described below), the following
expressions may be used:
    
* `hs.next` denotes the next element of the header stack that has not
  been populated using a call to `extract(...)`, which is explained
  below, and
* `hs.last` is a reference to the last element of the header stack
  that was previously populated using a call to `extract(...)`.

A header _union_ encodes a disjoint alternative between two headers:
```
header_union l3 {
  ipv4_t ipv4;
  ipv6_t ipv6;
}    
```
Only one of the headers may be valid at run-time. The components of a
header union can be accessed and modified using standard "dot"
notation.
            
### Other types

P4 provides a number of other types including:

* Generics,
* Types for parsers, actions, tables, controls and other program
  elements, 
* Types for `extern` functions and objects,

See the language specification for details.
    
## Parsers

The first piece of a P4 program is usually a _parser_ that maps the
bits in the actual packet into typed representations. A typical parser
might be declared as follows:    
```
parser P(packet_in packet,
         out headers_t headers,
         inout meta_t meta,
         inout standard_metadata_t std_meta) {
  ...
}
```    
The `packet` argument is an object that encapsulates the packet being
parsed. It has a generic method `extract` that can be used to populate
headers. The `headers`, `meta`, and `std_meta` arguments are data
structures representing the parsed headers, along with
program-specific and standard metadata. Typically the types of
`header` and `meta` are `struct`s defined by the programmer, while
the type of `std_meta` is a `struct` defined in the standard library.

The direction annotations `out` and `inout` indicate arguments that
are write-only and read-write respectively. There is also an `in`
annotation that indicates a read-only argument.

Internally, a parser describe a state machine in which each state may
(i) extract bits out of the packet header, branch on the values of
those states, and transition to the next state. For example, the
following parser recognizes Ethernet and IPv4 packets.
```
state start {
  return parse_ethernet;
}
state parse_ethernet {
  packet.extract(headers.ethernet);
  return select(headers.ethernet.etherType) {
    0x800 : parse_ipv4;
    default : accept;
  }
}
state parse_ipv4 {
  packet.extract(headers.ipv4);
  return accept;
}                
```         
Parsers have several special states including the initial state
(`start`), which must be explicitly defined, as well as accepting
(`accept`) and rejecting (`reject`) final states.
        
## Match-Action Tables

_Match-action tables_ are the primary constructs that programmers use
to specify packet processing in most P4 programs.

An _action_ is a procedure containing block of commands that are
executed in sequence. For example, the following declaration sets the
output port for the packet to the value supplied as a parameter.
```
action set_output_port(bit<9> output_port) {
  std_meta.egress_spec = output_port;
}    
```    
As with parsers, parameters can have direction annotations. Any
parameter without a direction annotation indicates _action data_ provided
by the control plane, and must come after any parameters with direction
annotations, which are supplied by other parts of the P4 program.

A _table_ specifies the values that should be matched in the table,
how those values should be matched, and the actions that can be
applied to matching packets. For example, the following table might be
used to implement destination-based forwarding:
```
table next_hop {
  key = {
     hdr.ipv4.dstAddr : lpm;
  }
  actions = {
     set_output_port;
     drop;
  }
  default = drop;
}    
    
```
Here the `key` declaration specifies that the IPv4 destination address
should be matched in the table using longest-prefix matching
(`lpm`). The `actions` declarations specifies the set of actions that
may be used to process packets matching specific rules. The optional
`default` action specifies the action to use for packets that do not
match any rules.

Note that the rules themselves are populated by the control plane,
which is not defined in P4.
        
## Externs     
    
Many P4 targets offer other forms of packet-processing functionality
-- both built-in primitives such as hash functions, and stateful
objects such as registers. For example, a counter can be declared and
used as follows:    
```
counter(n, bytes) c;    // construct an array of byte counters of size n
...
bit<32> bkt;
hash(bkt, ... ); // compute bucket by hashing on header values
c.count(bkt);   // increment counter for bucket
```    
            
## Controls

To allow programmers to combine multiple tables and imperative
statements into larger blocks of code, P4 provies a construct called a
control. The declaration of a control is similar to that of a parser:
```
control C(inout headers_t headers, inout meta_t meta, inout standard_metadata_t std_meta) {
  ...
  apply {
     ...
  }     
}
```
The body of a `control` consists of declarations followed by an
`apply` block, which is executed when the control is applied to
values. Within a control, one can  declare `action`s and
`table`s, apply actions and tables to values,
```
tbl.apply(hdr.ipv4.dstAddr);    
```
and
```
set_output_port(511);    
```        
or use conditionals:
```
if(hdr.ipv4.isValid())
  tbl.apply(hdr.ipv4.dstAddr);
else
  drop();        
```        
Most P4 programs define top-level `ingress` and `egress` controls. It
is also possible to factor them into smaller components---e.g., one
control for Ethernet processing, and another for IPv4 processing. To
construct a control and apply it to data-plane values, use the
following notation:
```
C() c;
c.apply(hdrs, meta, std_meta);        
```        
        
## Architectures

P4 is designed to be a target-independent language and it is possible
to use P4 to program traditional switch ASICs, programmable NICs,
FPGAs, and software switches. To support this diversity of targets, P4
supports the notion of an architecture -- an abstract specification of
the capabilities and structure of the pipeline supported on that
target.

For this project, we will be using [V1
Model](https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4),
which is a simple architecture based on the design proposed in the
original [RMT paper](https://dl.acm.org/citation.cfm?id=2486011).

# Phase I

In the first phase of the project, you will build up two pieces of
functionality found on most switches.
    
## Exercise 0: Test Development Environment

To confirm that you have all required software up and running, we
suggest that you take a look at `simple_router`, which is one of the
examples provided with P4 App.

* Examine the `p4app.json` JSON file, which describes the overall
  configuration of the application, including the source files and
  topology.

* Examine the source code in `header.p4`, `parser.p4`, and
  `simple_router.p4` to get a sense of how a complete P4 program is
  implemented.

* Examine the commands in the `simple_router.config` file, which
  specify the table entries added by a (static) control plane.

* Run the example by executing the following steps:
```
% p4app simple_router.p4app
mininet> pingall    
```    
You should see the following output:
```
*** Ping: testing ping reachability
h1 -> h2 
h2 -> h1 
*** Results: 0% dropped (2/2 received)
```
        
**To submit:** Nothing!    

## Exercise 1: Access Control

In this exercise, you will extend the simple router with support for
specifying access policies. More specifically, your application will
provide one additional match-action table named `acl` that the control
plane can populate with rules to drop specified packets. This table
should support matching on any of the following header fields:

* Ethernet source addresses
* Ethernet destination address    
* IPv4 source addresses (if it exists)
* IPv4 destination addresses (if it exists)
* TCP/UDP source port (if it exists)
* TCP/UDP source port (if it exists)    

As an optional extension, you may also allow other fields (e.g.,
ingress/egress ports) to be matched in the ACL table.
    
### Implementation Steps
    
To complete this exericse, you should extend the simple router as
follows:

* Declare header types and instances for TCP and UDP.
* Extend the parser to populate the new header instances.
* Create a match-action table `acl`
* Apply `acl` at a suitable location in the pipeline.
* Edit the `s1.config` file to populate the `acl` tables with entries.

### Testing
    
To test that your program is working correctly, we have provided a
pair of Python scripts that allow you to send and receive traffic from
the command-line. You can run these scripts as follows:

```
p4app exec m h1 /tmp/receive.py    
```
and    
```
p4app exec m h2 /tmp/send.py 10.0.0.10 "Hello World"
```
    
To test that your access control rules are working correctly, try
inserting rule to the `acl` table that filters certain IP addresses. 
                
**To submit:** `access_control.p4app.{tar.gz,zip}`   
        
## Exercise 2: Load Balancer
    
In this exercise, you will extend your solution to Exercise 1 with
additional support for ECMP-style load balancing. More specifically,
your switch will take incoming traffic from host `h1` to a single
"fictious" IP address `10.0.0.99` and map it to one of hosts `h2` or
`h3`, rewriting the IP and MAC addresses to match the addresses of the
selected host.

You will want to ensure that your solution preserves "flow affinity"
-- i.e., packets in the same flow should be sent to the same
server. You can consider packets to be members of the same flow if
they have the same the source and destination IPv4 address, the same
IPv4 protocol field, and the same source and destination TCP/UDP
ports.

### Implementation Steps

To complete this exericse, you should extend the access control router
with support for ECMP-style load balancing as specified above. There
are multiple ways to achieve this, and you are free to use any
algorithm you like.    

### Testing    

To test your solution, you should verify that packets sent by `h1` to
the fictitious address above are indeed delivered to `h2` and `h3`
using the supplied `send.py` and `receive.py` scripts.
        
**To submit:** `load_balance.p4app.zip`
    
## Exercise 3: Proposal

In Phase III of the project, you will use P4 to develop a novel piece
of data plane functionality that you design. For example, you might
want to extend your switch by re-implementing a standard piece of
functionality, or you might want develop something completely
novel. The choice of what to implement is completely up to you.

To help you stay on track, you will need to write a short (!) proposal
outlining your plans. You will also have to submit a brief status
update in Phase II.

Following are a few possible project ideas to help you get started:

* Use P4 to implement a simple form of "active networking" where
  packets carry programs that are executed on switches. The paper
  [Millions of Little
  Minions](https://dl.acm.org/citation.cfm?id=2626292) provides an
  example of such a system.

* Use P4 to implement an advanced security service that executes a
  policy automaton on all packets. The paper
  [Kinetic](http://kinetic.noise.gatech.edu/) provides an example of
  such a system in the domain of SDN.

* Use P4 to implement a form of _in-band telemetry_, where each switch
  marks packets with a custom header that keeps track of aggregate
  information about how it was forwarded in the network. The P4
  [INT](http://p4lang.github.io/p4-spec/docs/In-band%20Network%20Telemetry%20(INT).pdf)
  specification provides an example of such a system.

* Use P4 to implement space-efficient traffic monitoring using
  sketches. The
  [HashPipe](https://conferences.sigcomm.org/sosr/2017/papers/sosr17-heavy-hitter.pdf)
  paper provides an example of such a system.
    
* Use P4 to implement application-level or congestion-aware load
  balancing. The
  [HULA](https://conferences.sigcomm.org/sosr/2016/papers/sosr_paper67.pdf)
  paper provides an example of such a design.

* Use P4 to implement an in-network caching service. The
  [NetCache](https://www.cs.jhu.edu/~xinjin/files/SOSP17_NetCache.pdf)
  system provides an example of such a system.

Your proposal document should explain both what you plan to build and
how you plan to evaluate your solution. Please be brief -- no more than a single page!
        
**To submit:** `project-proposal.{txt,pdf}`    
        
## Exercise 4: Debriefing    

* How many hours did you spend on this assignment? 

* Would you rate it as easy, moderate, or difficult? 

* If you worked with a partner, please briefly describe both of your
contributions to the solution you submitted.
    
* How deeply do you feel you understand the material it covers (0%-100%)?

* If you have any other comments, we would like to hear them! Please
write them down or send email to `jnfoster@cs.cornell.edu`

**To submit:** debriefing.txt


