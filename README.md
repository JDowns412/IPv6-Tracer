# IPv6-Tracer
CS 653 Semester Project
Tim Contois
Jacob Downs
Joshua Pikovsky


Please see the Project proposal at:
https://drive.google.com/a/umass.edu/file/d/0B-QXyc0377JqMG0wWkhOTGstRlU/view?usp=sharing

## Background​ ​and​ ​Motivation

Initially deployed in 1983 for ARPANET, the Internet Protocol version 4 (or IPv4) is still one of
the core protocols of the modern-day Internet, and continues to route most traffic in the network layer. In
its earliest documentation, the Internet Protocol was described as a way of transmitting blocks of data
between sources and destinations identified by a fixed length address. The initial address length was set to
32 bits, which provided for an address space of 4,294,967,296 (2^32) addresses. While this seemed an
extremely large number at the time, the 90s saw a rapidly growing Internet, and Internet user-base, which
began to slowly deplete the available address pool. Decades later, the number of Internet pages and users
has exploded, and the common-place nature of mobile phones and laptops has necessitated many more IP
address assignments than ever foreseen in the days of ARPANET. In 2011, the top-level IP addresses
were exhausted, and the need for a solution became more urgent. IPv6 was proposed as the new standard,
and with address lengths increased to 128 bits, the problem would effectively be dealt with.
While IPv6 seems like an effective and somewhat necessary change, there are still large parts of
the Internet that have not adopted the new protocol. IPv4 continues to carry the vast majority of Internet
traffic, and recent statistics show that the migration to IPv6 is occurring at a very slow pace. Some hosts
may be hesitant to switch to IPv6 due to fears of slower speeds or decreased quality.

##Project​ ​Scope
For our semester project, we intend to gain a better understanding of how popular websites and
autonomous systems are adopting IPv6, and whether or not there are noticeable changes to the Internet
experience. In particular, we are interested in finding places where IPv6 has already been implemented,
and how the speed compares to IPv4.

Our work will begin with developing a script that, given a list of websites, will access the targets
and produce statistics on which ones support full IPv6 connections, which ones have downgraded back to
IPv4, and the various informatics associated with the connection. This will be accomplished by running
an IPv6 traceroute to all targets. If we discover a resultant set of sites that support both IPv4 and IPv6,
then we will request the page using both protocols to compare the access speeds.
If some sites have downgraded to IPv4, then the script will attempt to follow the traceroute in
search of the point where the downgrade occurred. If we discover these points in the traceroute output, we
will collect them, and attempt to find out pertinent information like the device on which the downgrade
occurred, the device’s AS, and the downgrading software.


###Related work

*“Beyond Counting: New Perspectives on the Active IPv4 Address Space” -
	(https://arxiv.org/abs/1606.00360)
	This paper provides a background on the current usage of IPv4 addresses. The techniques used to
	measure the active IPv4 space provides a better perspective on the IPv6 adoption debate.
*“Forming an IPv6-only Core for Today's Internet” -
	(http://conferences.sigcomm.org/sigcomm/2007/ipv6/1569042987.pdf)
	We plan on looking into places where IPv6 traffic needs to be converted to IPv4 and sent over
	some links in IPv4. This papers information on an IPv6-only core could give insight on the
	performance differences between completely IPv6 traffic and IPv6 traffic that has to be
	“tunnelled” down to IPv4.
*“A Scalable Routing System Design for Future Internet” -
	(http://conferences.sigcomm.org/sigcomm/2007/ipv6/1569043163.pdf)
	While IPv6 helps with the IP address shortage issue, the huge expansion of the number of IP
	addresses poses scalability concerns for IPv6. The ideas mention in this paper are of interest for
	investigating the performance implications of IPv6.
*“A Comparison of IPv6-over-IPv4 Tunnel Mechanisms” - (https://tools.ietf.org/html/rfc7059)
The information on these “tunnelling” mechanisms will help us analyze the performance of
traceroutes revealing a downgrade from IPv6 to IPv4. Our performance techniques can compare
these techniques with an IPv6-only network.