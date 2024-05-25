from cdn_setup import my_slice, server_node, server2_node
from delay import run_tcpdump

# Run tcpdump on servers 1 and 2
# Adds delay to both servers
def experiment1():
    server1_out, server1_err = run_tcpdump(server_node)



experiment1()





