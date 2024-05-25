from cdn_setup import get_interface_name

def run_tcpdump(node):
    interface_name = get_interface_name(node)
    return node.execute(f'sudo tcpdump -i {interface_name} -n -c 1')
    # return node.execute('echo "HELLO"')

def add_delay(node):
    pass