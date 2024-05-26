
[site1, site2, site3, site4] = ['PSC', 'MASS', 'WASH', 'PRIN']

# Cannot go beyond 2 cores, 10 RAM
server_specs = [
    {'cores': 1, 'ram': 4, 'name':'server1', 'site':site1},
    {'cores': 1, 'ram': 8, 'name':'server2', 'site':site4},
    {'cores': 2, 'ram': 5, 'name':'server3', 'site':site4},
    {'cores': 2, 'ram': 10, 'name':'server4', 'site':site1},
]

client_specs = {'num_clients':6, 'client_sites':['MASS', 'MASS', 'WASH', 'PRIN', 'PRIN', 'PSC']}

# Makes server nodes and returns a list of the nodes
def make_servers(my_slice):
    nodes = []
    for spec in server_specs:
        node = my_slice.add_node(image='default_ubuntu_22', **spec)
        node.add_fabnet()
    return nodes

def list_server_nodes(my_slice):
    return [my_slice.get_node(spec['name']) for spec in server_specs]

def make_clients(my_slice):
    """
    :param client_specs: a dictionary containing the number of clients you want to create and the location of each client's site
    """
    num_clients = client_specs['num_clients']
    client_sites = client_specs['client_sites']

    for i in range(1, num_clients+1):
        client_name = f"Client_{i}"
        node = my_slice.add_node(name=client_name, site=client_sites[i-1], image='default_ubuntu_22')
        node.add_fabnet()