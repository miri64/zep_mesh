ZEP Mesh
========

This library allows to create an IEEE 802.15.4 mesh out of applications that
send packets of [wireshark's ZEP format][ZEP].

[ZEP]: https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob;f=epan/dissectors/packet-zep.c;h=8f3618a3a9cf990fc9fb334cdd918d898ec5dc2a;hb=HEAD#l23

Dependencies
------------
You need a version of `socat` and `netcat` and the python libraries
`matplotlib`, `networkx`, and `pexpect` to use this library.

Using ZEP Mesh with RIOT native
-------------------------------
This library was tested with the native port of the operating system
[RIOT][RIOT]. The native port allows to run the whole operating system as a
process in Linux.

[RIOT]: https://github.com/RIOT-OS/RIOT

### Starting a random graph
You can a start a random mesh (generated by the Watts-Strogatz small-world
algorithm) using

```bash
./zep_mesh_riot_native.py -n 5 -c 0.5
```

Where `-n 5` gives the number of nodes and `-c 0.5` (maybe between 0 and 1.0)
determines its connectivity.

**Attention:** on some values of `-c` the program might fail. Just try a larger
value then.

The graph is always stored in the `mesh.json` file.

### Background
With the parameter of `-n` being *n* and the one of `-c` being
*c* the random graph is generated as a connected Watts-Strogatz small-world graph
with the following input parameters:
 * *n* is the number of nodes
 * Each node is connected to *n • c* nearest neighbors in ring topology
 * *c* is the probability of rewiring each edge

### Starting a graph from input file
You can also load a previously generated mesh:

```bash
./zep_mesh_riot_native.py -i mesh.json
```

### Connecting to the nodes in the mesh
The script will inform you about the target to connect to the nodes

```bash
./zep_mesh_riot_native.py -n 5 -c 0.5
```

```
Started node at localhost:4711
Started node at localhost:4715
Started node at localhost:4714
Started node at localhost:4713
Started node at localhost:4712
```

You can access its shell by using `netcat` 

```C
nc localhost 4711
```

or [pyterm]

```C
pyterm -ts localhost:4711
```

or any other application capable of opening arbitrary TCP connections.

[pyterm]: https://github.com/RIOT-OS/RIOT/tree/master/dist/tools/pyterm

### Dumping to Wireshark
This script is also able to dump all the traffic in the mesh in the PCAP format
to `stdout`. You can parse this using Wireshark:

```
./zep_mesh_riot_native.py -n 5 -c 0.5 | wireshark -i - -k
```
