from cdn_setup import get_interface_name, get_node_site_ip_addr, my_slice, video_file_name
from time import sleep

def run_tcpdump(node):
    print(f'Listening on {node.get_name()}')
    while True:
        interface_name = get_interface_name(node)
        node.execute(f'sudo tcpdump -i {interface_name} -n -c 1')

def add_delay(node):
    pass


def visit_node(from_node_name, to_node_name):
    from_node = my_slice.get_node(name=from_node_name)
    to_node = my_slice.get_node(name=to_node_name)
    to_node_ip = get_node_site_ip_addr(to_node)
    print(f'curl -O {to_node_ip}')
    return from_node.execute_thread(f'curl -O {to_node_ip}/{video_file_name}')
    

'''
Used to simulate artificial load by
requesting the index.html page directly from the server.
Quit with Ctrl-C
'''

def generate_traffic_from_node(client_name, server_name, num_threads=2):
    while True:
        print(f'Making {num_threads} requests from {client_name} to {server_name}')
        threads = [visit_node(client_name, server_name) for _ in range(num_threads)]
        results = [thread.result() for thread in threads]
        sleep(0.5)



