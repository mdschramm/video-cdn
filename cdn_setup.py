from datetime import datetime, timezone, timedelta
import itertools
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager
from nodes import make_servers, make_clients, client_sites, list_server_nodes,list_client_nodes, site1, site2, site3, site4
import os
import json

fablib = fablib_manager()

slice_name = 'client_server_video'

lb_node_name = 'Load_Balancer'

video_file_name = 'cars.mp4'

def renew_slice():
    end_date = (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S %z")
    
    try:
        slice = fablib.get_slice(name=slice_name)
    
        slice.renew(end_date)
    except Exception as e:
        print(f"Exception: {e}")

def delete_slice():
    try:
        slice = fablib.get_slice(name=slice_name)
        slice.delete()
    except Exception as e:
        print(f"Exception: {e}")

"""
def ping(my_slice, from_name, to_name):
    print(f'Pinging from {from_name} to {to_name}')
    from_node = my_slice.get_node(name=from_name)
    to_node = my_slice.get_node(name=to_name)
    to_addr = to_node.get_interface(network_name=f'FABNET_IPv4_{to_node.get_site()}').get_ip_addr()
    stdout, stderr = from_node.execute(f'ping -c 5 {to_addr}')
"""

def ping(my_slice, from_name, to_name):
    failed_connections = []
    
    print(f'Pinging from {from_name} to {to_name}')
    from_node = my_slice.get_node(name=from_name)
    to_node = my_slice.get_node(name=to_name)
    to_addr = to_node.get_interface(network_name=f'FABNET_IPv4_{to_node.get_site()}').get_ip_addr()
    
    print(f'{from_name} pinging {to_name}')
    stdout, stderr = from_node.execute(f'ping -c 5 {to_addr}', quiet = True)

    if '0% packet loss' in stdout:
        print(f'SUCCESS: connection from {from_name} to {to_name}\n')
    else:
        print(f'FAILED: connection from {from_name} to {to_name}')
        print(stdout, '\n')
        failed_connections.append((from_name, to_name))

    if failed_connections:
        return failed_connections
    else:
        return 'No failed connections'

def verify_nodes():
    node_names = [node['name'] for node in json.loads(my_slice.list_nodes(output='json', quiet=True))]
    pairs = list(itertools.combinations(node_names, 2))
    
    for pair in pairs:
        from_name = pair[0]
        to_name = pair[1]
        ping(my_slice, from_name, to_name)

"""
def make_slice():
    
    my_slice = fablib.new_slice(name=slice_name)
    
    print(f"Sites: {site1}, {site2}, {site3}, {site4}")

    make_servers(my_slice)

    make_clients()
    #client_node = my_slice.add_node(name=client_node_name, site=site2, image='default_ubuntu_22')
    #client_node.add_fabnet()

    lb_node = my_slice.add_node(name=lb_node_name, site=site3, image='default_ubuntu_22')
    lb_node.add_fabnet()

    my_slice.submit()
    return my_slice
"""

def make_slice(client_sites):
    """
    :param client_sites: a list containing the sites you want to use for your clients
    """
    
    my_slice = fablib.new_slice(name=slice_name)
    
    print(f"Sites: {site1}, {site2}, {site3}, {site4}")

    # create servers
    make_servers(my_slice)

    # create clients
    make_clients(my_slice, client_sites=client_sites)

    # create load balancer
    lb_node = my_slice.add_node(name=lb_node_name, site=site3, image='default_ubuntu_22')
    lb_node.add_fabnet()

    my_slice.submit()
    return my_slice


def server_setup(server_node, video_path='/home/fabric/work/video_streamer_files/cars.mp4'):
    # TODO threadify
    video_path = video_path if os.path.exists(video_path) else '/home/fabric/work/video_streamer_files/soccer_vid.mp4'
        

    # Install necessary packages
    stdout, stderr = server_node.execute('sudo apt-get update && sudo apt install net-tools && sudo apt-get -y install apache2 && sudo apt install tcpdump && sudo a2enmod lua')
    # Upload video file to server

    # source data file
    server_node.upload_file(video_path, '/home/ubuntu/cars.mp4')
    server_node.execute(f'sudo mv /home/ubuntu/cars.mp4 /var/www/html')

    # load lua script for server dashboard into server /etc/apache2 dir
    lua_script_path = '/home/fabric/work/server-status.lua'
    server_node.upload_file(lua_script_path, '/home/ubuntu/server-status.lua')
    server_node.execute('sudo mv /home/ubuntu/server-status.lua /etc/apache2')

    # Replace existing status.conf file with lua module enabled
    # This seems bad
    status_conf_path = '/home/fabric/work/status.conf'
    server_node.upload_file(status_conf_path, '/home/ubuntu/status.conf')
    server_node.execute('sudo mv /home/ubuntu/status.conf /etc/apache2/mods-enabled')

    lua_module_command = 'LoadModule lua_module modules/mod_lua.so'
    # load lua module in apache2.conf
    server_node.execute(f'echo -e "{lua_module_command}" | sudo tee -a /etc/apache2/apache2.conf')

    # reload server with new configuration
    server_node.execute('sudo systemctl reload apache2')

    
def client_setup(client_node):
    stdout, stderr = client_node.execute('sudo apt-get update && sudo apt install net-tools && sudo apt-get upgrade -y && sudo apt install tcpdump')

def get_interface_name(node):
    return node.get_interface(network_name=f'FABNET_IPv4_{node.get_site()}').get_device_name()

def get_node_site_ip_addr(node):
    return node.get_interface(network_name=f'FABNET_IPv4_{node.get_site()}').get_ip_addr()

def write_reverse_proxy_conf(server_nodes, lbmethod):
    """
    :param server_nodes: a list of the server nodes
    :param lbmethod: the load balancing method to use
    """
    # get the IP address of the server nodes
    server_nodes_ips = []
    
    for server in server_nodes:
        server_node = my_slice.get_node(name = server)
        server_ip = server_node.get_interface(network_name=f'FABNET_IPv4_{server_node.get_site()}').get_ip_addr()
        server_ip_string = str(server_ip)
        server_nodes_ips.append(server_ip_string)

    # create reverse-proxy.conf string
    reverse_proxy_conf_content = '<Proxy balancer://videostreamer>'
    
    for ip in server_nodes_ips:
        balancer_member = f'\n\tBalancerMember http://{ip}'
        reverse_proxy_conf_content += balancer_member
    
    reverse_proxy_conf_content += f'\n\tProxySet lbmethod={lbmethod}'
    reverse_proxy_conf_content += '''\n</Proxy>
    \nProxyPass /balancer-manager !\nProxyPass "/" "balancer://videostreamer/"\nProxyPassReverse "/" "balancer://videostreamer/"
    '''

    # write reverse_proxy_conf_content to local file
    try:
        with open('reverse-proxy.conf', 'w') as file:
            file.write(reverse_proxy_conf_content)

    except Exception as e:
        print(e)

    # write the reverse-proxy.conf file to /etc/apache2
    escaped_rpc_content = reverse_proxy_conf_content.replace("\n", "\\n").replace('"', '\\"')
    rpc_command = f'echo -e "{escaped_rpc_content}" | sudo tee /etc/apache2/reverse-proxy.conf'
    output = lb_node.execute(rpc_command)

def lb_setup(lb_node, lbmethod):
    """
    :param lb_node: the load balancer
    :param lbmethod: the load balancer method to use
    """
    # update and install net-tools and apache2
    stdout, stderr = lb_node.execute('sudo apt-get update && sudo apt install net-tools && sudo apt-get -y install apache2 && sudo a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests && sudo apt install tcpdump')


    server_node_names = [n.get_name() for n in list_server_nodes(my_slice)]
    # create and upload the reverse-proxy.conf file
    write_reverse_proxy_conf(server_nodes = server_node_names, lbmethod = lbmethod)
    
    # append line to apache2.conf UNCOMMENT IF FIRST TIME RUNNING
    ac_command = 'echo "Include reverse-proxy.conf" | sudo tee -a /etc/apache2/apache2.conf'
    lb_node.execute(ac_command)

    # Enable balancer manager dashboard
    status_conf_path = '/home/fabric/work/proxy_balancer.conf'
    lb_node.upload_file(status_conf_path, '/home/ubuntu/proxy_balancer.conf')
    lb_node.execute('sudo mv /home/ubuntu/proxy_balancer.conf /etc/apache2/mods-enabled')
    
    # restart apache2
    lb_node.execute('sudo systemctl restart apache2')



def get_slice():
    try:
        return make_slice(client_sites)
    except Exception as e:
        print(f'Slice already exists - fetching slice')
        return fablib.get_slice(name=slice_name)


my_slice = get_slice()
lb_node = my_slice.get_node(name=lb_node_name)


def setup_nodes():
    for sn in list_server_nodes(my_slice):
        server_setup(sn)

    for cn in list_client_nodes(my_slice):
        client_setup(cn)

    lb_setup(lb_node, lbmethod = 'byrequests')


tunnel_port = 10010
'''
Print commands to tunnel local requests to localhost:<tunnel_port>
to any server node. This is required in order to view the server-status
dashboard
'''
def print_local_tunneling_commands():
    print('Run these from a local folder containing a copy of slice_key and ssh_config')
    print('Server tunnels===================')
    server_nodes = list_server_nodes(my_slice)
    for i, sn in enumerate(server_nodes):
        username = sn.get_username()
        manage_ip = sn.get_management_ip()
        print(f'{sn.get_name()} command:')
        print(f'ssh -L {tunnel_port+i}:localhost:80 -F ssh_config -i slice_key {username}@{manage_ip}')
    print('LB tunnel======================')
    username = lb_node.get_username()
    manage_ip = lb_node.get_management_ip()
    print(f'ssh -L {tunnel_port+len(server_nodes)}:localhost:80 -F ssh_config -i slice_key {username}@{manage_ip}')

    
def print_node_sshs():
    for sn in list_server_nodes(my_slice):
        print(sn.get_name())
        print(sn.get_ssh_command())
    
    for cn in list_client_nodes(my_slice):
        print(cn.get_name())
        print(cn.get_ssh_command())
    
    print(lb_node.get_name())
    print(lb_node.get_ssh_command())

def print_node_ips():
    for sn in list_server_nodes(my_slice):
        print(f'{sn.get_name()} site IP: {get_node_site_ip_addr(sn)}')
    for cn in list_client_nodes(my_slice):
        print(f'{cn.get_name()} site IP: {get_node_site_ip_addr(cn)}')
    print(f'LB site IP: {get_node_site_ip_addr(lb_node)}')


        
if __name__ == '__main__':
    fablib.show_config()
    verify_nodes()
    setup_nodes()
    # renew_slice()
    # delete_slice()
    print_local_tunneling_commands()