import requests
import argparse
import subprocess
import os
import re

# Change this to your domain name or IP address of the server running wg-easy
base_url = 'http://monitorvpn.pund-it.ca:51821'

# Make sure to update the password to the password you set for your web GUI
def get_session_id(base_url=base_url):
    path = base_url + '/api/session'
    headers = {'Content-Type': 'application/json'}
    data = '{"password": "pun!Zlrn6006"}'  # Update with the actual password

    response = requests.post(path, headers=headers, data=data)
    session_id = response.cookies.get('connect.sid')
    return session_id

def highlight_variable(variable):
    return f"\033[92m{variable}\033[0m"  # Green color for highlighting

def get_client_data(base_url=base_url, session_id=None):
    if not session_id:
        session_id = get_session_id(base_url)
    
    path = base_url + '/api/wireguard/client'
    headers = {'Cookie': f'connect.sid={session_id}'}
    response = requests.get(path, headers=headers)

    if response.status_code == 200:
        client_data = response.json()
        #print(f'Number of clients: {len(client_data)}')
        #for client in client_data:
            #print(f'Client name: {client["name"]}, Client id: {client["id"]}')
        return client_data  # Return the client data
    else:
        print(f'Error: {response.status_code} - {response.text}')
        return None  # Return None if there's an error

def create_new_client(client_name, base_url=base_url, session_id=None):
    if not session_id:
        session_id = get_session_id(base_url)
    
    path = base_url + '/api/wireguard/client'
    headers = {'Content-Type': 'application/json', 'Cookie': f'connect.sid={session_id}'}
    data = '{"name":"'+client_name+'"}'
    response = requests.post(path, headers=headers, data=data)

    if response.status_code == 200:
        print(f"\nNew client '{highlight_variable(client_name)}' created successfully.")
        client_data = get_client_data(base_url, session_id)
        
        if client_data:
            client_id = next((client['id'] for client in client_data if client['name'] == client_name), None)

            if client_id:
                print(f"Client ID for '{highlight_variable(client_name)}': {highlight_variable(client_id)}")
                download_client_config(client_id, client_name, base_url, session_id)
                subnet = prompt_for_subnet()
                update_defaultroute_script(subnet)

                if prompt_docker_compose():
                    execute_pre_docker_script()
                    trigger_docker_compose()
                else:
                    print("Docker Compose was not triggered.")
            else:
                print(f"Client '{client_name}' not found in the client list.")
        else:
            print("Error retrieving client data.")
    else:
        print(f'Error creating client: {response.status_code} - {response.text}')

def download_client_config(client_id, client_name, base_url=base_url, session_id=None):
    if not session_id:
        session_id = get_session_id(base_url)
    
    path = f"{base_url}/api/wireguard/client/{client_id}/configuration"
    headers = {'Cookie': f'connect.sid={session_id}'}
    response = requests.get(path, headers=headers, stream=True)

    if response.status_code == 200:
        config_file_path = f"./wg/wg_confs/wg0.conf"
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, "wb") as config_file:
            for chunk in response.iter_content(chunk_size=8192):
                config_file.write(chunk)
        #print(f"Configuration file saved as {config_file_path}")

        try:
            with open(config_file_path, "r") as config_file:
                for line in config_file:
                    if line.startswith("Address ="):
                        address = line.split("=")[1].strip()
                        print(f"Assigned Address for '{highlight_variable(client_name)}': {highlight_variable(address)}\n")
                        break
        except Exception as e:
            print(f"Error reading the configuration file: {e}")
    else:
        print(f"Failed to download configuration file: {response.status_code}")
        print(response.text)

def update_defaultroute_script(subnet):
    try:
        defaultroute_file = './scripts/defaultroute.sh'
        if os.path.exists(defaultroute_file):
            with open(defaultroute_file, 'r') as file:
                lines = file.readlines()

            insert_index = next((i for i, line in enumerate(lines) if '# Start the original container process' in line), None)
            if insert_index is not None:
                route_line = f'ip route add {subnet} via 192.168.254.1\n'
                lines.insert(insert_index, route_line)

                with open(defaultroute_file, 'w') as file:
                    file.writelines(lines)
                #print(f"Added route for {subnet} in {defaultroute_file}")
            else:
                print("Could not find the line '# Start the original container process' in the script.")
        else:
            print(f"{defaultroute_file} not found.")
    except Exception as e:
        print(f"Error updating defaultroute.sh: {e}")

def execute_pre_docker_script():
    try:
        print("Running chmod +x on necessary scripts...")
        subprocess.run(['chmod', '+x', './wg/custom-cont-init.d/iptables-setup.sh'], check=True)
        subprocess.run(['chmod', '+x', './scripts/defaultroute.sh'], check=True)
        print("Permissions updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while changing permissions: {e}")

def trigger_docker_compose():
    try:
        print("Triggering docker-compose up -d...")
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        print("Docker Compose has been triggered successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running docker-compose: {e}")

def prompt_for_subnet():
    while True:
        subnet = input("Enter Clients Subnet (e.g., 10.255.x.0/24): ").strip()
        if validate_subnet(subnet):
            return subnet
        else:
            print("Invalid subnet format. Please try again.")

def validate_subnet(subnet):
    bogon_patterns = [
        r"^10\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d+$",          # 10.0.0.0/8
        r"^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}/\d+$",  # 172.16.0.0/12
        r"^192\.168\.\d{1,3}\.\d{1,3}/\d+$",             # 192.168.0.0/16
    ]
    
    for pattern in bogon_patterns:
        if re.match(pattern, subnet):
            return True
    return False

def prompt_docker_compose():
    while True:
        user_input = input("Do you want to trigger 'docker-compose up -d' to start the services? (y/n): ").strip().lower()
        if user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show Wireguard clients or create a new client')
    parser.add_argument('action', metavar='ACTION', type=str, choices=['status', 'create'], help='Action to perform')
    parser.add_argument('name', metavar='NAME', type=str, nargs='?', help='Name for new client (required for "create" action)')
    args = parser.parse_args()

    if args.action == 'status':
        get_client_data()
    elif args.action == 'create':
        if not args.name:
            parser.error('Name is required for "create" action')
        create_new_client(args.name)
