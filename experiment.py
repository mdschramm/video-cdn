import sys
from cdn_setup import my_slice, lb_node, print_node_sshs, print_node_ips
from nodes import list_server_nodes, list_client_nodes
from delay import run_tcpdump, generate_traffic_from_node, stream_on_client

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
Terminal 1: python experiment.py tcpdump server1
Terminal 2: python experiment.py tcpdump server2
Terminal 3: python experiment.py gen_traffic server1
'''

print_node_sshs() 
print_node_ips()


actions = ['tcpdump', 'gen_traffic', 'stream_on_client']
node_names = [n.get_name() for n in list_server_nodes(my_slice)] + [n.get_name() for n in list_client_nodes(my_slice)]

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

    node_name = sys.argv[2]
    if node_name not in node_names:
        print(f'Node {server_name} not found. Available nodes:', node_names)
        sys.exit(0)

    if action == actions[0]: # TCPDUMP
        tcpdump(node_name)
    elif action ==actions[1]:
        gen_traffic(node_name)
    else:
        stream_on_client(node_name)



