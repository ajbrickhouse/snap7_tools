import snap7
import re

def parse_logical_address(logical_address):
    result = re.match(r"%([IQM])([W]?)(\d+)(\.(\d+))?", logical_address)
    if result:
        area_letter, word_flag, byte_str, _, bit_str = result.groups()
        byte = int(byte_str)
        bit = int(bit_str) if bit_str else None

        area = {
            'I': snap7.types.Areas.PE,
            'Q': snap7.types.Areas.PA,
            'M': snap7.types.Areas.MK,
        }[area_letter]

        if word_flag == 'W':
            tag_type = 'int'
        elif bit is not None:
            tag_type = 'bool'
        else:
            raise ValueError(f"Invalid logical address format: {logical_address}")

        return {
            'area': area,
            'type': tag_type,
            'byte': byte,
            'bit': bit,
        }

    raise ValueError(f"Invalid logical address format: {logical_address}")

# Example usage:
logical_addresses = [
    "%I0.0", "%I0.1", "%I0.2", "%I0.3", "%I0.4", "%I0.5", "%I0.7", "%I1.0",
    "%I1.1", "%I1.2", "%I1.3", "%I1.4", "%I1.5", "%I2.0", "%I2.1", "%I2.2",
    "%I2.3", "%I2.4", "%I2.5", "%I2.6", "%I2.7", "%I3.0", "%I3.1", "%I3.2",
    "%I3.3", "%I3.4", "%I3.5", "%I3.6", "%I3.7", "%I4.0", "%I4.1", "%I4.2",
    "%I4.3", "%I4.4", "%I4.5", "%I4.6", "%I4.7", "%I5.0", "%I5.1", "%I5.2",
    "%I5.3", "%I5.5", "%I5.6", "%I5.7", "%IW80", "%IW100", "%IW102", "%IW104",
    "%IW108", "%Q0.0", "%Q0.1", "%Q0.2", "%Q0.3", "%Q0.4", "%Q0.5", "%Q0.6",
    "%Q0.7", "%Q1.0", "%Q1.1", "%Q2.0", "%Q2.1", "%Q2.2", "%Q2.3", "%Q2.4",
    "%Q2.5", "%Q2.6", "%Q2.7", "%Q3.0", "%Q3.1", "%Q3.2", "%Q3.3", "%Q3.4",
    "%Q3.5", "%Q3.6", "%Q3.7", "%Q4.0", "%Q4.1", "%Q4.2", "%Q4.3", "%Q4.4",
    "%Q4.5", "%Q4.6", "%Q4.7", "%Q5.0", "%Q5.1", "%Q5.2", "%Q5.3", "%Q5.4",
    "%Q5.5", "%Q5.6", "%Q5.7", "%M10.6", "%M10.7", "%D11.0"
]
for logical_address in logical_addresses:
    try:
        result = parse_logical_address(logical_address)
    except ValueError as e:
        result = e
        
    print(f"{logical_address}: {result}")
