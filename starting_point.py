import snap7
from snap7.util import *
import time

# Replace IP_ADDRESS with the IP address of your PLC
IP_ADDRESS = "192.168.0.244"
RACK = 0
SLOT = 1

# Define the tags
tags = [
    {"name": "I_0.0", "type": "bool", "area": snap7.types.Areas.PE, "byte": 0, "bit": 0},
    {"name": "AI_80", "type": "int", "area": snap7.types.Areas.PE, "byte": 80},
    {"name": "AI_100", "type": "int", "area": snap7.types.Areas.PE, "byte": 100},
    {"name": "O_0.0", "type": "bool", "area": snap7.types.Areas.PA, "byte": 0, "bit": 0},
    {"name": "O_0.1", "type": "bool", "area": snap7.types.Areas.MK, "byte": 0, "bit": 5},
    {"name": "M_10.6", "type": "bool", "area": snap7.types.Areas.MK, "byte": 0, "bit": 6},
    {"name": "M_0.7", "type": "bool", "area": snap7.types.Areas.MK, "byte": 0, "bit": 7},
    # Add more tags here
]

def main():    
    plc = snap7.client.Client()
    plc.connect(IP_ADDRESS, RACK, SLOT)

    try:
        while True:
            print("\033c", end="")
            for tag in tags:
                value = read_tag(plc, tag)
                # clear the terminal
                print(f"{tag['name']}:", value)
            time.sleep(1)  # Adjust the sleep time according to your needs
    except KeyboardInterrupt:
        print("Terminating...")
    finally:
        plc.disconnect()

def read_tag(plc, tag):
    if tag["type"] == "bool":
        data = plc.read_area(tag["area"], 0, tag["byte"], 1)
        return get_bool(data, 0, tag["bit"])
    elif tag["type"] == "int":
        data = plc.read_area(tag["area"], 0, tag["byte"], 2)
        return get_int(data, 0)

if __name__ == "__main__":
    main()