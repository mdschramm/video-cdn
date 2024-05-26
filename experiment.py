import sys
from cdn_setup import my_slice, lb_node, print_node_sshs, print_node_ips
from nodes import list_server_nodes, list_client_nodes
from delay import run_tcpdump, generate_traffic_from_node

'''
Usage for tcpdump:
python experiment.py tcpdump <name of server>

Testing scenario:
Terminal 1: python experiment.py tcpdump server1
Terminal 2: python experiment.py tcpdump server2

ssh into client:
curl -O <load_balancer ip>/cars.mp4

Observe traffic on servers from Terminal 1 or 2
================================================

Usage for gen_traffic:
python experiment.py gen_traffic <name of server>

Testing scenario:
Terminal 1: python experiment.py tcpdump server
Terminal 2: python experiment.py tcpdump server2
Terminal 3: python experiment.py gen_traffic server
'''

print_node_sshs() 
print_node_ips()


actions = ['tcpdump', 'gen_traffic']
server_names = [n.get_name() for n in list_server_nodes(my_slice)]

def tcpdump(node_name):
    node = my_slice.get_node(name=node_name)
    run_tcpdump(node)


def gen_traffic(server_node_name):
    # TODO don't just pick first client
    client_name = list_client_nodes(my_slice)[0].get_name()
    generate_traffic_from_node(client_name, server_node_name)


if __name__ == '__main__':
    action = sys.argv[1]
    if action not in actions:
        print(f'Action {action} not found. Available actions:', actions)
        sys.exit(0)

    server_name = sys.argv[2]
    if server_name not in server_names:
        print(f'Servername {server_name} not found. Available servers:', server_names)
        sys.exit(0)

    if action == actions[0]: # TCPDUMP
        tcpdump(server_name)
    else:
        gen_traffic(server_name)



