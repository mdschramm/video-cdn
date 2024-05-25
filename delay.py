from cdn_setup import get_interface_name

def run_tcpdump(node):
    interface_name = get_interface_name(node)
    node.execute(f'sudo tcpdump -i {interface_name} port 80 -n -w - -U')

def add_delay(node):
    pass