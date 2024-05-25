import datetime
from time import timezone
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager
import os


fablib = fablib_manager()

fablib.show_config();

slice_name = 'client_server_video'

server_node_name = 'Server'
server_node_name2 = 'Server2'
client_node_name = 'Client'
lb_node_name = 'Load_Balancer'

slice_file = 'cdn_setup.graphml'


def renew_slice():
    end_date = (datetime.now(timezone.utc) + datetime.timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S %z")
    
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

def ping(my_slice, from_name, to_name):
    from_node = my_slice.get_node(name=from_name)
    to_node = my_slice.get_node(name=to_name)
    to_addr = to_node.get_interface(network_name=f'FABNET_IPv4_{to_node.get_site()}').get_ip_addr()
    stdout, stderr = from_node.execute(f'ping -c 5 {to_addr}')
    

def make_slice():
    try:
        my_slice = fablib.new_slice(name=slice_name)
        my_slice.load(slice_file)
        my_slice.submit()
        return my_slice
    except Exception as e:
        print('Slice file not found - creating new slice')
        
        my_slice = fablib.new_slice(name=slice_name)
        
        [site1, site2, site3, site4] = ['PSC', 'MASS', 'WASH', 'PRIN']
        print(f"Sites: {site1}, {site2}, {site3}, {site4}")
    
        server_node = my_slice.add_node(name=server_node_name, site=site1, image='default_ubuntu_22')
        server_node.add_fabnet()

        server_node2 = my_slice.add_node(name=server_node_name2, site=site4, image='default_ubuntu_22')
        server_node2.add_fabnet()
    
        client_node = my_slice.add_node(name=client_node_name, site=site2, image='default_ubuntu_22')
        client_node.add_fabnet()

        lb_node = my_slice.add_node(name=lb_node_name, site=site3, image='default_ubuntu_22')
        lb_node.add_fabnet()
    

        my_slice.submit()
        my_slice.save(slice_file)
        return my_slice


def server_setup(server_node, video_path='/home/fabric/work/video_streamer_files/cars.mp4'):
    # TODO threadify
    video_path = video_path if os.path.exists(video_path) else '/home/fabric/work/video_streamer_files/soccer_vid.mp4'
        

    # Install necessary packages
    stdout, stderr = server_node.execute('sudo apt-get update && sudo apt install net-tools && sudo apt-get -y install apache2')
    # Upload video file to server

    server_node.upload_file(video_path, '/home/ubuntu/cars.mp4')

    server_node.execute(f'sudo mv /home/ubuntu/cars.mp4 /var/www/html')
    
def client_setup(client_node):
    stdout, stderr = client_node.execute('sudo apt-get update && sudo apt install net-tools && sudo apt-get upgrade -y')

def get_node_site_ip_addr(node):
    return node.get_interface(network_name=f'FABNET_IPv4_{node.get_site()}').get_ip_addr()

def lb_setup(lb_node, server_node):
    # update and install net-tools and apache2
    stdout, stderr = lb_node.execute('sudo apt-get update && sudo apt install net-tools && sudo apt-get -y install apache2')

    # get the IP address of the server node
    server_ip = get_node_site_ip_addr(server_node)
    server_ip_string = str(server_ip)
    
    # create and write to reverse-proxy.conf file
    file_name = "reverse-proxy.conf"
    
    reverse_proxy_conf_content = f'''"ProxyPass" "/" "http://{server_ip_string}”
    "ProxyPassReverse" "/" "{server_ip_string}”'''
    escaped_rpc_content = reverse_proxy_conf_content.replace("\n", "\\n").replace('"', '\\"')
    
    rpc_command = f'sudo echo -e "{escaped_rpc_content}" | sudo tee /etc/apache2/{file_name}'
    lb_node.execute(rpc_command)
    
    # append line to apache2.conf
    ac_command = 'echo "Include reverse-proxy.conf" | sudo tee -a /etc/apache2/apache2.conf'
    lb_node.execute(ac_command)
    
    # restart apache2
    lb_node.execute('sudo a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests && sudo systemctl restart apache2')    
    
    # Steps:
        # - Get server IP Address (public facing address always seems to be associated with enp7s0)
        # - Create reverse-proxy.conf file:
        
        # "ProxyPass" "/" "http://<server ip>”
        # "ProxyPassReverse" "/" "<server ip>”
        
        # - Upload reverse-proxy.conf file to /etc/apache2
        # - Append line to file /etc/apache2/apache2.conf: Include reverse-proxy.conf
        # - Execute: “sudo a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests && sudo systemctl restart apache2”


# my_slice = make_slice()

my_slice = fablib.get_slice(name=slice_name)
# delete_slice()
server_node = my_slice.get_node(name=server_node_name)
server_setup(server_node)

server2 = my_slice.get_node(name=server_node_name2)
server_setup(server_node)

client_node = my_slice.get_node(name=client_node_name)
client_setup(client_node)

lb_node = my_slice.get_node(name=lb_node_name)
lb_setup(lb_node, server_node)

# verify communication
print(f'{server_node_name} pinging {client_node_name}')
ping(my_slice, server_node_name, client_node_name)

print(f'{server_node_name2} pinging {client_node_name}')
ping(my_slice, server_node_name2, client_node_name)

print(f'{server_node_name} pinging {lb_node_name}')
ping(my_slice, server_node_name, lb_node_name)

print(f'{server_node_name2} pinging {lb_node_name}')
ping(my_slice, server_node_name2, lb_node_name)

print(f'{lb_node_name} pinging {client_node_name}')
ping(my_slice, lb_node_name, client_node_name)

print(server_node.get_ssh_command())
print(client_node.get_ssh_command())
print(lb_node.get_ssh_command())

print(get_node_site_ip_addr(server_node))
print(get_node_site_ip_addr(client_node))
print(get_node_site_ip_addr(lb_node))
