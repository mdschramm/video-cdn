import sys
from cdn_setup import my_slice, server_node, server2_node, server_node_name, server_node_name2, lb_node, print_node_sshs, print_node_ips
from delay import run_tcpdump

'''
Usage:
python experiment.py <name of server>

Testing scenario:
Terminal 1: python experiment.py Server
Terminal 2: python experiment.py Server2

ssh into client:
curl -O <load_balancer ip>/cars.mp4

Observe traffic on servers from Terminal 1 or 2
'''

print_node_sshs() 
print_node_ips()


def experiment1(node):
    while True:
        run_tcpdump(node)



if __name__ == '__main__':
    node_name = sys.argv[1]
    if node_name == server_node_name:
        print('Listening on', server_node_name)
        experiment1(server_node)
    elif node_name == server_node_name2:
        print('Listening on', server_node_name2)
        experiment1(server2_node)
    else:
        print('available node names: ', server_node_name, server_node_name2)



