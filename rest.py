import json
import requests
import ipaddress
import logging
from pathlib import Path

requests.packages.urllib3.disable_warnings()

# Configuración de logging
logging.basicConfig(filename='router_config.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

api_url_base = "https://172.20.10.4/restconf/data/Cisco-IOS-XE-native:native"
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("cisco", "cisco123!")

config_file = Path("router_config.json")

def load_config():
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

def get_interfaces():
    api_url = f"{api_url_base}/interface"
    resp = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
    if resp.status_code == 200:
        response_json = resp.json()
        return response_json
    else:
        print(f"Error: {resp.status_code} - {resp.reason}")
        return None

def validate_ip(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False

def validate_subnet_mask(subnet_mask):
    try:
        ipaddress.IPv4Network(f"0.0.0.0/{subnet_mask}")
        return True
    except ValueError:
        return False

def add_interface(interface_name, description, ip_address, subnet_mask):
    if not validate_ip(ip_address):
        print(f"Dirección IP inválida: {ip_address}")
        return

    if not validate_subnet_mask(subnet_mask):
        print(f"Máscara de subred inválida: {subnet_mask}")
        return

    config = load_config()
    config[interface_name] = {
        "description": description,
        "ip_address": ip_address,
        "subnet_mask": subnet_mask
    }
    save_config(config)

    # Ajustar el tipo de interfaz en función del nombre
    if interface_name.startswith("GigabitEthernet"):
        interface_type = "GigabitEthernet"
        interface_number = interface_name.replace("GigabitEthernet", "")
    elif interface_name.startswith("Loopback"):
        interface_type = "Loopback"
        interface_number = interface_name.replace("Loopback", "")
    else:
        print(f"Tipo de interfaz no soportado: {interface_name}")
        return

    api_url = f"{api_url_base}/interface/{interface_type}={interface_number}"
    
    if interface_type == "GigabitEthernet":
        payload = {
            "Cisco-IOS-XE-native:GigabitEthernet": {
                "name": interface_number,
                "description": description,
                "ip": {
                    "address": {
                        "primary": {
                            "address": ip_address,
                            "mask": subnet_mask
                        }
                    }
                }
            }
        }
    elif interface_type == "Loopback":
        payload = {
            "Cisco-IOS-XE-native:Loopback": {
                "name": interface_number,
                "description": description,
                "ip": {
                    "address": {
                        "primary": {
                            "address": ip_address,
                            "mask": subnet_mask
                        }
                    }
                }
            }
        }

    print("Payload:", json.dumps(payload, indent=4))  # Debugging: print payload
    logging.info(f"Payload enviado: {json.dumps(payload, indent=4)}")
    
    resp = requests.put(api_url, auth=basicauth, headers=headers, data=json.dumps(payload), verify=False)
    if resp.status_code in [200, 201, 204]:
        print(f"Interfaz {interface_name} agregada/modificada con éxito.")
        logging.info(f"Interfaz {interface_name} agregada/modificada: {description}, {ip_address}/{subnet_mask}")
    else:
        print(f"Error: {resp.status_code} - {resp.reason}")
        print(resp.text)
        logging.error(f"Error al agregar/modificar interfaz {interface_name}: {resp.status_code} - {resp.reason}")

def delete_interface(interface_name):
    config = load_config()
    if interface_name in config:
        del config[interface_name]
        save_config(config)
        interface_type = "GigabitEthernet"  # Para simplificar, solo usaremos GigabitEthernet
        interface_number = interface_name.replace("GigabitEthernet", "")
        api_url = f"{api_url_base}/interface/{interface_type}={interface_number}"
        
        resp = requests.delete(api_url, auth=basicauth, headers=headers, verify=False)
        if resp.status_code in [200, 204]:
            print(f"Interfaz {interface_name} eliminada con éxito.")
            logging.info(f"Interfaz {interface_name} eliminada")
        else:
            print(f"Error: {resp.status_code} - {resp.reason}")
            print(resp.text)
            logging.error(f"Error al eliminar interfaz {interface_name}: {resp.status_code} - {resp.reason}")
    else:
        print(f"La interfaz {interface_name} no existe en la configuración.")

def main():
    while True:
        print("\nMenu")
        print("1- Ver interfaces")
        print("2- Agregar una nueva interfaz")
        print("3- Eliminar una interfaz")
        print("4- Salir")

        choice = input("Selecciona una opción: ")

        if choice == "1":
            interfaces = get_interfaces()
            if interfaces:
                print(json.dumps(interfaces, indent=4))
        elif choice == "2":
            interface_name = input("Nombre de la interfaz (e.g., GigabitEthernet1): ")
            description = input("Descripción de la interfaz: ")
            ip_address = input("Dirección IP: ")
            subnet_mask = input("Máscara de subred: ")
            add_interface(interface_name, description, ip_address, subnet_mask)
        elif choice == "3":
            interface_name = input("Nombre de la interfaz a eliminar (e.g., GigabitEthernet1): ")
            delete_interface(interface_name)
        elif choice == "4":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    main()

