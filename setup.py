import requests
import argparse
import subprocess
import os

# Change this to your domain name or IP address of the server running wg-easy
base_url = 'http://monitorvpn.pund-it.ca:51821'

# Make sure to update the password to the password you set for your web GUI
def get_session_id(base_url=base_url):
    path = base_url + '/api/session'
    headers = {'Content-Type': 'application/json'}
    data = '{"password": "pun!Zlrn6006"}'  # Update with the actual password

    # Make initial request to obtain session ID
    response = requests.post(path, headers=headers, data=data)

    # Extract session ID from Set-Cookie header
    session_id = response.cookies.get('connect.sid')
    return session_id

def get_client_data(base_url=base_url, session_id=None):
    if not session_id:
        session_id = get_session_id(base_url)
    
    # Make second request with session ID in Cookie header
    path = base_url + '/api/wireguard/client'
    headers = {'Cookie': f'connect.sid={session_id}'}
    response = requests.get(path, headers=headers)

    # Check if the request was successful and print client data
    if response.status_code == 200:
        client_data = response.json()
        print(f'Number of clients: {len(client_data)}')
        for client in client_data:
            print(f'Client name: {client["name"]}')
    else:
        print(f'Error: {response.status_code} - {response.text}')

def create_new_client(client_name, base_url=base_url, session_id=None):
    if not session_id:
        session_id = get_session_id(base_url)
    
    # Make third request with session ID in Cookie header and provide a name for the new client to be created
    path = base_url + '/api/wireguard/client'
    headers = {'Content-Type': 'application/json', 'Cookie': f'connect.sid={session_id}'}
    data = '{"name":"'+client_name+'"}'
    response = requests.post(path, headers=headers, data=data)

    # Check if the request was successful and print new client data
    if response.status_code == 200:
        new_client_data = response.json()
        print('New client created:')
        print(f'Client name: {new_client_data["name"]}')
        client_id = new_client_data['id']  # Assuming the response contains an 'id' field (UUID)
        # Call function to download the configuration file
        download_client_config(client_id, client_name, base_url, session_id)
        
        # Prompt for the Clients Subnet and update the defaultroute.sh file
        subnet = prompt_for_subnet()
        update_defaultroute_script(subnet)
        
        # Ask the user for confirmation before triggering Docker Compose
        if prompt_docker_compose():
            execute_pre_docker_script()  # Add this step to run the chmod command
            trigger_docker_compose()
        else:
            print("Docker Compose was not triggered.")
    else:
        print(f'Error: {response.status_code} - {response.text}')

def download_client_config(client_id, client_name, base_url=base_url, session_id=None):
    if not session_id:
        session_id = get_session_id(base_url)
    
    # Construct the URL to download the configuration file using client UUID
    path = f"{base_url}/api/wireguard/client/{client_id}/configuration"
    headers = {'Cookie': f'connect.sid={session_id}'}
    
    # Request the configuration file
    response = requests.get(path, headers=headers, stream=True)

    # Check if the request was successful and save the configuration file
    if response.status_code == 200:
        config_file_path = f"./wg/wg_confs/wg0.conf"
        with open(config_file_path, "wb") as config_file:
            for chunk in response.iter_content(chunk_size=8192):
                config_file.write(chunk)
        print(f"Configuration file saved as {config_file_path}")
    else:
        print(f"Failed to download configuration file: {response.status_code}")
        print(response.text)

def update_defaultroute_script(subnet):
    try:
        # Check if the defaultroute.sh file exists
        defaultroute_file = './scripts/defaultroute.sh'
        if os.path.exists(defaultroute_file):
            # Open the file and read all the lines
            with open(defaultroute_file, 'r') as file:
                lines = file.readlines()

            # Find the index of the line that contains '# Start the original container process'
            insert_index = None
            for i, line in enumerate(lines):
                if '# Start the original container process' in line:
                    insert_index = i
                    break

            if insert_index is not None:
                # Create the line to be inserted
                route_line = f'ip route add {subnet} via 192.168.254.1\n'
                
                # Insert the new line before the identified line
                lines.insert(insert_index, route_line)
                
                # Write the updated content back to the file
                with open(defaultroute_file, 'w') as file:
                    file.writelines(lines)
                print(f"Added route for {subnet} in {defaultroute_file}")
            else:
                print("Could not find the line '# Start the original container process' in the script.")
        else:
            print(f"{defaultroute_file} not found.")
    except Exception as e:
        print(f"Error updating defaultroute.sh: {e}")


def execute_pre_docker_script():
    try:
        # Run 'chmod +x ./wg/custom-cont-init.d/iptables-setup.sh' before running docker-compose
        print("Running chmod +x on iptables-setup.sh...")
        subprocess.run(['chmod', '+x', './wg/custom-cont-init.d/iptables-setup.sh'], check=True)
        print("Permission changed for iptables-setup.sh.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while changing permissions: {e}")

def trigger_docker_compose():
    try:
        # Run 'docker-compose up -d' to start the services in the background
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
    # Check if the subnet format matches 10.255.x.0/24 (basic validation)
    import re
    pattern = r"^10\.255\.\d{1,3}\.0/24$"
    return bool(re.match(pattern, subnet))

def prompt_docker_compose():
    # Prompt the user to confirm if they want to trigger Docker Compose
    while True:
        user_input = input("Do you want to trigger 'docker-compose up -d' to start the services? (y/n): ").strip().lower()
        if user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    # Use argparse to accept user arguments
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
