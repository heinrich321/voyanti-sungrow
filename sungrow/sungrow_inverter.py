from server import Server
from pymodbus.client import ModbusSerialClient
import struct

U16_MAX = 2**16-1

class SungrowInverter(Server):
    """
    Sungrow
        SG110CX
        SGKTL-20        not found
        SG33CX
        SG80KTL-20
    """
    # TODO some should be class attributes
    
    manufacturer = "Sungrow"

    # ROM 3x registers
    # TODO Combiner Board information p12 - need to check availability before reading?
    registers = {
        'Serial Number': {'addr': 4990, 'count': 10, 'dtype': 'UTF-8', 'multiplier': 1, 'unit': ''},
        'Device Type Code': {'addr': 5000, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': ''},
        'Nominal Active Power': {'addr': 5001, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'kW'},
        'Output Type': {'addr': 5002, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': ''},

        'Daily Power Yields': {'addr': 5003, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'kWh'},
        'Total Power Yields': {'addr': 5004, 'count': 2, 'dtype': 'U32', 'multiplier': 1, 'unit': 'kWh'},
        'Total Running Time': {'addr': 5006, 'count': 2, 'dtype': 'U32', 'multiplier': 1, 'unit': 'h'},
        'Internal Temperature': {'addr': 5008, 'count': 1, 'dtype': 'S16', 'multiplier': 0.1, 'unit': '°C'},
        'Total Apparent Power': {'addr': 5009, 'count': 2, 'dtype': 'U32', 'multiplier': 1, 'unit': 'VA'},
        'MPPT 1 Voltage': {'addr': 5011, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 1 Current': {'addr': 5012, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 2 Voltage': {'addr': 5013, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 2 Current': {'addr': 5014, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 3 Voltage': {'addr': 5015, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 3 Current': {'addr': 5016, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'Total DC Power': {'addr': 5017, 'count': 2, 'dtype': 'U32', 'multiplier': 1, 'unit': 'W'},
        'A-B Line Voltage/Phase A Voltage': {'addr': 5019, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},             # 5019-5021 two output types check TODO
        'B-C Line Voltage/Phase B Voltage': {'addr': 5020, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'C-A Line Voltage/Phase C Voltage': {'addr': 5019, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'Phase A Current': {'addr': 5022, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'Phase B Current': {'addr': 5023, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'Phase C Current': {'addr': 5024, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'Total Active Power': {'addr': 5031, 'count': 2, 'dtype': 'U32', 'multiplier': 1, 'unit': 'W'},
        'Total Reactive Power': {'addr': 5033, 'count': 2, 'dtype': 'U32', 'multiplier': 1, 'unit': 'Var'},
        'Power Factor': {'addr': 5035, 'count': 1, 'dtype': 'S16', 'multiplier': 0.001, 'unit': ''},                                # >0: leading, <0 lagging
        'Grid Frequency': {'addr': 5036, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'Hz'},
        'Work State': {'addr': 5038, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': ''},
        'Fault/Alarm Code 1': {'addr': 5045, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': ''},

        'Nominal Reactive Power': {'addr': 5049, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'kVar'},
        'Array Insulation Resistance': {'addr': 5071, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': 'kΩ'},
        'Active Power Regulation Setpoint': {'addr': 5077, 'count': 2, 'dtype': 'U32', 'multiplier': 1, 'unit': 'W'},
        'Reactive Power Regulation Setpoint': {'addr': 5079, 'count': 2, 'dtype': 'S32', 'multiplier': 1, 'unit': 'Var'},

        'Work State (Extended)': {'addr': 5081, 'count': 2, 'dtype': 'U32', 'multiplier': 1, 'unit': ''},
        'Meter Power': {'addr': 5083, 'count': 2, 'dtype': 'S32', 'multiplier': 1, 'unit': 'W'},
        'Meter A Phase Power': {'addr': 5085, 'count': 2, 'dtype': 'S32', 'multiplier': 1, 'unit': 'W'},
        'Meter B Phase Power': {'addr': 5087, 'count': 2, 'dtype': 'S32', 'multiplier': 1, 'unit': 'W'},
        'Meter C Phase Power': {'addr': 5089, 'count': 2, 'dtype': 'S32', 'multiplier': 1, 'unit': 'W'},
        'Load Power': {'addr': 5091, 'count': 2, 'dtype': 'S32', 'multiplier': 1, 'unit': 'W'},
        'Daily Export Energy': {'addr': 5093, 'count': 2, 'dtype': 'U32', 'multiplier': 0.1, 'unit': 'kWh'},
        'Total Export Energy': {'addr': 5095, 'count': 2, 'dtype': 'U32', 'multiplier': 0.1, 'unit': 'kWh'},
        'Daily Import Energy': {'addr': 5097, 'count': 2, 'dtype': 'U32', 'multiplier': 0.1, 'unit': 'kWh'},
        'Total Import Energy': {'addr': 5099, 'count': 2, 'dtype': 'U32', 'multiplier': 0.1, 'unit': 'kWh'},
        'Daily Direct Energy Consumption': {'addr': 5101, 'count': 2, 'dtype': 'U32', 'multiplier': 0.1, 'unit': 'kWh'},
        'Total Direct Energy Consumption': {'addr': 5103, 'count': 2, 'dtype': 'U32', 'multiplier': 0.1, 'unit': 'kWh'},
        'Daily Running Time': {'addr': 5113, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': 'min'},

        'Present Country': {'addr': 5114, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': ''},

        'MPPT 4 Voltage': {'addr': 5115, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 4 Current': {'addr': 5116, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 5 Voltage': {'addr': 5117, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 5 Current': {'addr': 5118, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 6 Voltage': {'addr': 5119, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 6 Current': {'addr': 5120, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 7 Voltage': {'addr': 5121, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 7 Current': {'addr': 5122, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 8 Voltage': {'addr': 5123, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 8 Current': {'addr': 5124, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'Monthly Power Yields': {'addr': 5128, 'count': 2, 'dtype': 'U32', 'multiplier': 0.1, 'unit': 'kWh'},
        'MPPT 9 Voltage': {'addr': 5130, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 9 Current': {'addr': 5131, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 10 Voltage': {'addr': 5132, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 10 Current': {'addr': 5133, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 11 Voltage': {'addr': 5134, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 11 Current': {'addr': 5135, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'MPPT 12 Voltage': {'addr': 5136, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'MPPT 12 Current': {'addr': 5137, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'A'},
        'Total Power Yields (Increased Accuracy)': {'addr': 5144, 'count': 2, 'dtype': 'U32', 'multiplier': 0.1, 'unit': 'kWh'},
        'Negative Voltage to the Ground': {'addr': 5146, 'count': 1, 'dtype': 'S16', 'multiplier': 0.1, 'unit': 'V'},
        'Bus Voltage': {'addr': 5147, 'count': 1, 'dtype': 'U16', 'multiplier': 0.1, 'unit': 'V'},
        'Grid Frequency (Increased Accuracy)': {'addr': 5148, 'count': 1, 'dtype': 'U16', 'multiplier': 0.01, 'unit': 'Hz'},
        'PID Work State': {'addr': 5150, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': ''},
        'PID Alarm Code': {'addr': 5151, 'count': 1, 'dtype': 'U16', 'multiplier': 1, 'unit': ''}
    }

    # Params 4x register (write) p.13
    write_registers = {
        'System clock: Year': {'addr': 5000, 'dtype': 'U16', 'unit': ''},
        'System clock: Month': {'addr': 5001, 'dtype': 'U16', 'unit': ''},
        'System clock: Day': {'addr': 5002, 'dtype': 'U16', 'unit': ''},
        'System clock: Hour': {'addr': 5003, 'dtype': 'U16', 'unit': ''},
        'System clock: Minute': {'addr': 5004, 'dtype': 'U16', 'unit': ''},
        'System clock: Second': {'addr': 5005, 'dtype': 'U16', 'unit': ''},

        'Start/Stop': {'addr': 5006, 'dtype': 'U16', 'unit': ''},

        # 'Power limitation switch': {'addr': 5007, 'dtype': 'U16', 'unit': ''},
        # 'Power limitation setting': {'addr': 5008, 'dtype': 'U16', 'unit': '0.1%'},

        # Valid for inverters:
        # SG5KTL-MT
        # SG6KTL-MT
        # SG8KTL-M
        # SG10KTL-M
        # SG10KTL-MT
        # SG12KTL-M
        # SG15KTL-M
        # SG17KTL-M
        # SG20KTL-M
        # Note: Country set to Europe Area.
        # 'Export power limitation': {'addr': 5010, 'dtype': 'U16', 'unit': ''},
        # 'Export power limitation value': {'addr': 5011, 'dtype': 'U16', 'unit': ''},
        # 'Current transformer output current': {'addr': 5012, 'dtype': 'U16', 'unit': 'A'},
        # 'Current transformer range': {'addr': 5013, 'dtype': 'U16', 'unit': 'A'},
        # 'Current transformer': {'addr': 5014, 'dtype': 'U16', 'unit': ''},
        # 'Export power limitation percentage': {'addr': 5015, 'dtype': 'U16', 'unit': '0.1%'},
        # 'Installed PV Power': {'addr': 5016, 'dtype': 'U16', 'unit': '0.01KW'},

        # valid requirement checking needed
        # 'Power factor setting': {'addr': 5019, 'dtype': 'S16', 'unit': '0.001'},
        # 'Reactive power adjustment mode': {'addr': 5036, 'dtype': 'U16', 'unit': ''},
        # 'Reactive power percentage setting': {'addr': 5037, 'dtype': 'S16', 'unit': '0.1%'},

        # model specific
        # '100% Scheduling to Achieve Active Overload': {'addr': 5020, 'dtype': 'U16', 'unit': ''},
        # 'Night SVG Switch': {'addr': 5035, 'dtype': 'U16', 'unit': ''},

        # 'Power limitation adjustment': {'addr': 5039, 'dtype': 'U16', 'unit': '0.1kW'},
        # 'Reactive power adjustment': {'addr': 5040, 'dtype': 'S16', 'unit': '0.1kVar'},
        # 'PID Recovery': {'addr': 5041, 'dtype': 'U16', 'unit': ''},
        # 'Anti-PID': {'addr': 5042, 'dtype': 'U16', 'unit': ''},
        # 'Full-Day PID Suppression': {'addr': 5043, 'dtype': 'U16', 'unit': ''},
        # 'Q(P) curve 1': {'addr': 5048, 'dtype': 'U16', 'unit': ''},
        # 'Q(U) curve 1': {'addr': 5078, 'dtype': 'U16', 'unit': ''},
        # 'Q(P) curve 2': {'addr': 5116, 'dtype': 'U16', 'unit': ''},
        # 'Q(U) curve 2': {'addr': 5135, 'dtype': 'U16', 'unit': ''}
    }

    write_valid_values = {
        'Start/Stop': {'Start': 0xCF, 'Stop': 0xCE},
        'Power limitation switch': {'Enable': 0xAA, 'Disable': 0x55},
        'Export power limitation': {'Enable': 0xAA, 'Disable': 0x55},
        'Export power limitation value': {'Rated active power': 0},                         # remove from register map?
        # 'Current transformer output current': {'Min': 1, 'Max': 100},
        # 'Current transformer range': {'Min': 1, 'Max': 10000},
        'Current transformer type': {'Internal': 0, 'External': 1},
        # 'Export power limitation percentage': {'Min': 0, 'Max': 1000, 'Unit': '0.1%'},
        # 'Installed PV Power': {'Min': 0, 'Max': 30000, 'Unit': '0.01kW'},
        # 'Power factor setting': {
        #     'Range': {'Min': -1000, 'Max': 1000},
        #     'Unit': '0.001',
        #     'Notes': '> 0 means leading, < 0 means lagging',
        # },
        '100% Scheduling to Achieve Active Overload': {'Enable': 0xAA, 'Disable': 0x55},
        'Night SVG Switch': {'Enable': 0xAA, 'Disable': 0x55},
        # 'Reactive power adjustment mode': {
        #     'OFF': 0x55,
        #     'Power factor setting valid': 0xA1,
        #     'Reactive power percentage setting valid': 0xA2,
        #     'Enable Q(P) curve configuration': 0xA3,
        #     'Enable Q(U) curve configuration': 0xA4,
        # },
        # 'Reactive power percentage setting': {
        #     'Range': {'Min': -1000, 'Max': 1000},
        #     'Unit': '0.1%',
        # },
        'PID Recovery': {'Enable': 0xAA, 'Disable': 0x55},
        'Anti-PID': {'Enable': 0xAA, 'Disable': 0x55},
        'Full-Day PID Suppression': {'Enable': 0xAA, 'Disable': 0x55},
    }

    # Device Work state (Appendix 1) register 5038
    device_work_state = {
        0x0000: "Run",  # Grid-connected power generation, normal operation mode
        0x8000: "Stop",  # Inverter is stopped
        0x1300: "Key stop",  # Manual stop via app, internal DSP stops
        0x1500: "Emergency Stop",  
        0x1400: "Standby",  # Insufficient DC side input, waiting within standby duration
        0x1200: "Initial standby",  # Initial power-on standby state
        0x1600: "Starting",  # Initializing and synchronizing with grid
        0x9100: "Alarm run",  # Warning information detected
        0x8100: "Derating run",  # Active derating due to environmental factors
        0x8200: "Dispatch run",  # Running according to monitoring background scheduling
        0x5500: "Fault",  # Automatic stop and AC relay disconnect on fault
        0x2500: "Communicate fault"  # Unconfirmed state
    }
    # Device Work state (Appendix 2) register 5081-5082 
    # deive_work_state_2 = {}
    # Fault Codes (Appendix 3)
    fault_codes = {
        0x0002: "Grid overvoltage",
        0x0003: "Grid transient overvoltage",
        0x0004: "Grid undervoltage",
        0x0005: "Grid low voltage",
        0x0007: "AC instantaneous overcurrent",
        0x0008: "Grid over frequency",
        0x0009: "Grid underfrequency",
        0x000A: "Grid power outage",
        0x000B: "Device abnormal",
        0x000C: "Excessive leakage current",
        0x000D: "Grid abnormal",
        0x000E: "10-minute grid overvoltage",
        0x000F: "Grid high voltage",
        0x0010: "Output overload",
        0x0011: "Grid voltage unbalance",
        0x0013: "Device abnormal",
        0x0014: "Device abnormal",
        0x0015: "Device abnormal",
        0x0016: "Device abnormal",
        0x0017: "PV connection fault",
        0x0018: "Device abnormal",
        0x0019: "Device abnormal",
        0x001E: "Device abnormal",
        0x001F: "Device abnormal",
        0x0020: "Device abnormal",
        0x0021: "Device abnormal",
        0x0022: "Device abnormal",
        0x0024: "Excessively high module temperature",
        0x0025: "Excessively high ambient temperature",
        0x0026: "Device abnormal",
        0x0027: "Low system insulation resistance",
        0x0028: "Device abnormal",
        0x0029: "Device abnormal",
        0x002A: "Device abnormal",
        0x002B: "Low ambient temperature",
        0x002C: "Device abnormal",
        0x002D: "Device abnormal",
        0x002E: "Device abnormal",
        0x002F: "PV input configuration abnormal",
        0x0030: "Device abnormal",
        0x0031: "Device abnormal",
        0x0032: "Device abnormal",
        0x0035: "Device abnormal",
        0x0036: "Device abnormal",
        0x0037: "Device abnormal",
        0x0038: "Device abnormal",
        0x003B: "Device abnormal",
        0x003C: "Device abnormal",
        0x0046: "Fan alarm",
        0x0047: "AC-side SPD alarm",
        0x0048: "DC-side SPD alarm",
        0x004A: "Communication alarm",
        0x004C: "Device abnormal",
        0x004E: "PV1 abnormal",
        0x004F: "PV2 abnormal",
        0x0050: "PV3 abnormal",
        0x0051: "PV4 abnormal",
        0x0057: "Electric arc detection module abnormal",
        0x0058: "Electric arc fault",
        0x0059: "Electric arc detection disabled",
        0x0069: "Grid-side protection self-check failure",
        0x006A: "Grounding cable fault",
        0x0074: "Device abnormal",
        0x0075: "Device abnormal",
        0x00DC: "PV5 abnormal",
        0x00DD: "PV6 abnormal",
        0x00DE: "PV7 abnormal",
        0x00DF: "PV8 abnormal",
        0x00E0: "PV9 abnormal",
        0x00E1: "PV10 abnormal",
        0x00E2: "PV11 abnormal",
        0x00E3: "PV12 abnormal",
        0x0202: "Meter communication abnormal alarm",
        0x0214: "String 1 reverse connection alarm",
        0x0215: "String 2 reverse connection alarm",
        0x0216: "String 3 reverse connection alarm",
        0x0217: "String 4 reverse connection alarm",
        0x0218: "String 5 reverse connection alarm",
        0x0219: "String 6 reverse connection alarm",
        0x021A: "String 7 reverse connection alarm",
        0x021B: "String 8 reverse connection alarm",
        0x021C: "String 9 reverse connection alarm",
        0x021D: "String 10 reverse connection alarm",
        0x021E: "String 11 reverse connection alarm",
        0x021F: "String 12 reverse connection alarm",
        0x0220: "String 13 reverse connection alarm",
        0x0221: "String 14 reverse connection alarm",
        0x0222: "String 15 reverse connection alarm",
        0x0223: "String 16 reverse connection alarm",
        0x0234: "String 17 reverse connection alarm",
        0x0235: "String 18 reverse connection alarm",
        0x0236: "String 19 reverse connection alarm",
        0x0237: "String 20 reverse connection alarm",
        0x0238: "String 21 reverse connection alarm",
        0x0239: "String 22 reverse connection alarm",
        0x023A: "String 23 reverse connection alarm",
        0x023B: "String 24 reverse connection alarm",
        0x0224: "String 1 abnormal alarm",
        0x0225: "String 2 abnormal alarm",
        0x0226: "String 3 abnormal alarm",
        0x0227: "String 4 abnormal alarm",
        0x0228: "String 5 abnormal alarm",
        0x0229: "String 6 abnormal alarm",
        0x022A: "String 7 abnormal alarm",
        0x022B: "String 8 abnormal alarm",
        0x022C: "String 9 abnormal alarm",
        0x022D: "String 10 abnormal alarm",
        0x022E: "String 11 abnormal alarm",
        0x022F: "String 12 abnormal alarm",
        0x0230: "String 13 abnormal alarm",
        0x0231: "String 14 abnormal alarm",
        0x0232: "String 15 abnormal alarm",
        0x0233: "String 16 abnormal alarm",
        0x0244: "String 17 abnormal alarm",
        0x0245: "String 18 abnormal alarm",
        0x0246: "String 19 abnormal alarm",
        0x0247: "String 20 abnormal alarm",
        0x0248: "String 21 abnormal alarm",
        0x0249: "String 22 abnormal alarm",
        0x024A: "String 23 abnormal alarm",
        0x024B: "String 24 abnormal alarm",
        0x01C0: "String 1 reverse connection fault",
        0x01C1: "String 2 reverse connection fault",
        0x01C2: "String 3 reverse connection fault",
        0x01C3: "String 4 reverse connection fault",
        0x01C4: "String 5 reverse connection fault",
        0x01C5: "String 6 reverse connection fault",
        0x01C6: "String 7 reverse connection fault",
        0x01C7: "String 8 reverse connection fault",
        0x01C8: "String 9 reverse connection fault",
        0x01C9: "String 10 reverse connection fault",
        0x01CA: "String 11 reverse connection fault",
        0x01CB: "String 12 reverse connection fault",
        0x01CC: "String 13 reverse connection fault",
        0x01CD: "String 14 reverse connection fault",
        0x01CE: "String 15 reverse connection fault",
        0x01CF: "String 16 reverse connection fault",
        0x01D0: "String 17 reverse connection fault",
        0x01D1: "String 18 reverse connection fault",
        0x01D2: "String 19 reverse connection fault",
        0x01D3: "String 20 reverse connection fault",
        0x01D4: "String 21 reverse connection fault",
        0x01D5: "String 22 reverse connection fault",
        0x01D6: "String 23 reverse connection fault",
        0x01D7: "String 24 reverse connection fault",
        0x05DC: "PV1 overvoltage",
        0x05DD: "PV2 overvoltage",
        0x05DE: "PV3 overvoltage",
        0x05DF: "PV4 overvoltage",
        0x05E0: "PV5 overvoltage",
        0x05E1: "PV6 overvoltage",
        0x05E2: "PV7 overvoltage",
        0x05E3: "PV8 overvoltage",
        0x05E4: "PV9 overvoltage",
        0x05E5: "PV10 overvoltage",
        0x05E6: "PV11 overvoltage",
        0x05E7: "PV12 overvoltage",
        0x05E8: "PV13 overvoltage",
        0x05E9: "PV14 overvoltage",
        0x05EA: "PV15 overvoltage",
        0x05EB: "PV16 overvoltage",
        0x05EC: "PV17 overvoltage",
        0x05ED: "PV18 overvoltage",
        0x05EE: "PV19 overvoltage",
        0x05EF: "PV20 overvoltage",
        0x05F0: "PV21 overvoltage",
        0x05F1: "PV22 overvoltage",
        0x05F2: "PV23 overvoltage",
        0x05F3: "PV24 overvoltage",
        0x05F4: "PV25 overvoltage",
        0x05F5: "PV26 overvoltage",
        0x05F6: "PV27 overvoltage",
        0x05F7: "PV28 overvoltage",
        0x05F8: "PV29 overvoltage",
        0x05F9: "PV30 overvoltage",
        0x05FA: "PV31 overvoltage",
        0x05FB: "PV32 overvoltage"
    }
    # Country Info (Appendix 4)
    country_info = {
        0: "Great Britain",
        1: "Germany",
        2: "France",
        3: "Italy",
        4: "Spain",
        5: "Austria",
        6: "Australia",
        7: "Czech",
        8: "Belgium",
        9: "Denmark",
        10: "Greece Land",
        11: "Greece Island",
        12: "Netherlands",
        13: "Portugal",
        14: "China",
        15: "Sweden",
        16: "Other 50Hz",
        17: "Romania",
        18: "Thailand",
        19: "Turkey",
        20: "Australia(west)",
        21: "Reserved",
        25: "Vorarlberg District",
        26: "India",
        27: "Arab Emirates",
        28: "Israel",
        29: "Hungary",
        30: "Malaysia",
        31: "Philippines",
        32: "Poland",
        33: "Reserved",
        34: "Poland",
        35: "Thailand-MEA",
        36: "Vietnam",
        37: "Reserved",
        38: "Oman",
        39: "Sandi Arabia",
        40: "Finland",
        41: "Ireland",
        59: "America(Hawaii) District",
        60: "Canada",
        61: "America",
        62: "Other 60Hz",
        63: "Korea",
        64: "South Africa",
        65: "Chile",
        66: "Brazil",
        67: "Chinese Taipei District",
        69: "Japan",
        76: "Europe",
        77: "Europe",
        97: "America(ISO-NE) District",
        98: "America(1741-SA) District",
        170: "Mexico"
    }
    # PID Alarm COdes (Appendix 5)
    # pid_alarm_code = {}
    # Device Information (Appendix 6)
    device_info = {
        # TODO what are power limited ranges in appendix 6
        # verified from doc
        'SG33CX': {'type_code': '0x2C00', 'mppt': 3, 'string_per_mppt': 2},
        'SG110CX': {'type_code': '0x2C06', 'mppt': 9, 'string_per_mppt': 2},
        'SG80KTL-20': {'type_code': '0x0138', 'mppt': 1, 'string_per_mppt': 18},
        # not verified yet
        'SG30KTL': {'type_code': '0x27', 'mppt': 2, 'string_per_mppt': 4},
        'SG10KTL': {'type_code': '0x26', 'mppt': 2, 'string_per_mppt': 3},
        'SG12KTL': {'type_code': '0x29', 'mppt': 2, 'string_per_mppt': 3},
        'SG15KTL': {'type_code': '0x28', 'mppt': 2, 'string_per_mppt': 3},
        'SG20KTL': {'type_code': '0x2A', 'mppt': 2, 'string_per_mppt': 3},
        'SG30KU': {'type_code': '0x2C', 'mppt': 2, 'string_per_mppt': 5},
        'SG36KTL': {'type_code': '0x2D', 'mppt': 2, 'string_per_mppt': 5},
        'SG36KU': {'type_code': '0x2E', 'mppt': 2, 'string_per_mppt': 5},
        'SG40KTL': {'type_code': '0x2F', 'mppt': 2, 'string_per_mppt': 4},
        'SG40KTL-M': {'type_code': '0x0135', 'mppt': 3, 'string_per_mppt': 3},
        'SG50KTL-M': {'type_code': '0x011B', 'mppt': 4, 'string_per_mppt': 3},
        'SG60KTL-M': {'type_code': '0x0131', 'mppt': 4, 'string_per_mppt': 4},
        'SG60KU': {'type_code': '0x0136', 'mppt': 1, 'string_per_mppt': 8},
        'SG30KTL-M': {'type_code': '0x0141', 'mppt': 3, 'string_per_mppt': '3;3;2'},
        'SG30KTL-M-V31': {'type_code': '0x70', 'mppt': 3, 'string_per_mppt': '3;3;2'},
        'SG33KTL-M': {'type_code': '0x0134', 'mppt': 3, 'string_per_mppt': '3;3;2'},
        'SG36KTL-M': {'type_code': '0x74', 'mppt': 3, 'string_per_mppt': '3;3;2'},
        'SG33K3J': {'type_code': '0x013D', 'mppt': 3, 'string_per_mppt': 3},
        'SG49K5J': {'type_code': '0x0137', 'mppt': 4, 'string_per_mppt': 3},
        'SG34KJ': {'type_code': '0x72', 'mppt': 2, 'string_per_mppt': 4},
        'LP_P34KSG': {'type_code': '0x73', 'mppt': 1, 'string_per_mppt': 4},
        'SG50KTL-M-20': {'type_code': '0x011B', 'mppt': 4, 'string_per_mppt': 3},
        'SG60KTL': {'type_code': '0x010F', 'mppt': 1, 'string_per_mppt': 14},
        'SG80KTL': {'type_code': '0x0138', 'mppt': 1, 'string_per_mppt': 18},
        'SG60KU-M': {'type_code': '0x0132', 'mppt': 4, 'string_per_mppt': 4},
        'SG5KTL-MT': {'type_code': '0x0147', 'mppt': 2, 'string_per_mppt': 1},
        'SG6KTL-MT': {'type_code': '0x0148', 'mppt': 2, 'string_per_mppt': 1},
        'SG8KTL-M': {'type_code': '0x013F', 'mppt': 2, 'string_per_mppt': 1},
        'SG10KTL-M': {'type_code': '0x013E', 'mppt': 2, 'string_per_mppt': 1},
        'SG10KTL-MT': {'type_code': '0x2C0F', 'mppt': 2, 'string_per_mppt': 2},
        'SG12KTL-M': {'type_code': '0x013C', 'mppt': 2, 'string_per_mppt': 2},
        'SG15KTL-M': {'type_code': '0x0142', 'mppt': 2, 'string_per_mppt': 2},
        'SG17KTL-M': {'type_code': '0x0149', 'mppt': 2, 'string_per_mppt': 2},
        'SG20KTL-M': {'type_code': '0x0143', 'mppt': 2, 'string_per_mppt': 2},
        'SG80KTL-M': {'type_code': '0x0139', 'mppt': 4, 'string_per_mppt': 4},
        'SG111HV': {'type_code': '0x014C', 'mppt': 1, 'string_per_mppt': 1},
        'SG125HV': {'type_code': '0x013B', 'mppt': 1, 'string_per_mppt': 1},
        'SG125HV-20': {'type_code': '0x2C03', 'mppt': 1, 'string_per_mppt': 1},
        'SG30CX': {'type_code': '0x2C10', 'mppt': 3, 'string_per_mppt': 2},
        'SG36CX-US': {'type_code': '0x2C0A', 'mppt': 3, 'string_per_mppt': 2},
        'SG40CX': {'type_code': '0x2C01', 'mppt': 4, 'string_per_mppt': 2},
        'SG50CX': {'type_code': '0x2C02', 'mppt': 5, 'string_per_mppt': 2},
        'SG60CX-US': {'type_code': '0x2C0B', 'mppt': 5, 'string_per_mppt': 2},
        'SG250HX': {'type_code': '0x2C0C', 'mppt': 12, 'string_per_mppt': 2},
        'SG250HX-US': {'type_code': '0x2C11', 'mppt': 12, 'string_per_mppt': 2},
        'SG100CX': {'type_code': '0x2C12', 'mppt': 12, 'string_per_mppt': 2},
        'SG100CX-JP': {'type_code': '0x2C12', 'mppt': 12, 'string_per_mppt': 2},
        'SG250HX-IN': {'type_code': '0x2C13', 'mppt': 12, 'string_per_mppt': 2},
        'SG25CX-SA': {'type_code': '0x2C15', 'mppt': 3, 'string_per_mppt': 2},
        'SG75CX': {'type_code': '0x2C22', 'mppt': 9, 'string_per_mppt': 2},
        'SG3.0RT': {'type_code': '0x243D', 'mppt': 2, 'string_per_mppt': 1},
        'SG4.0RT': {'type_code': '0x243E', 'mppt': 2, 'string_per_mppt': 1},
        'SG5.0RT': {'type_code': '0x2430', 'mppt': 2, 'string_per_mppt': 1},
        'SG6.0RT': {'type_code': '0x2431', 'mppt': 2, 'string_per_mppt': 1},
        'SG7.0RT': {'type_code': '0x243C', 'mppt': 2, 'string_per_mppt': '2;1'},
        'SG8.0RT': {'type_code': '0x2432', 'mppt': 2, 'string_per_mppt': '2;1'},
        'SG10RT': {'type_code': '0x2433', 'mppt': 2, 'string_per_mppt': '2;1'},
        'SG12RT': {'type_code': '0x2434', 'mppt': 2, 'string_per_mppt': '2;1'},
        'SG15RT': {'type_code': '0x2435', 'mppt': 2, 'string_per_mppt': 2},
        'SG17RT': {'type_code': '0x2436', 'mppt': 2, 'string_per_mppt': 2},
        'SG20RT': {'type_code': '0x2437', 'mppt': 2, 'string_per_mppt': 2}
    }

    output_types = ["Two Phase", "3P4L", "3P3L"] # register 3x  5002

    # Appendix 7, 8, 9?

    def __init__(self):
        super.__init__()
        self.model = "unknown"

    def _decoded(content, dtype):
        #TODO see convert from registers
        if dtype == "UTF-8": return _decode_utf8(content)
        elif dtype == "U16": return _decode_u16(content)
        elif dtype == "U32": return _decode_u32(content)
        elif dtype == "S16": return _decode_s16(content)
        elif dtype == "S32": return _decode_s32(content)
        else: raise NotImplementedError(f"Data type {dtype} decoding not implemented")

    def _decode_u16(registers):
        """ Unsigned 16-bit big-endian to int """
        return registers[0]
    
    def _decode_s16(registers):
        """ Signed 16-bit big-endian to int """
        sign = 0xFFFF if registers[0] & 0x1000 else 0
        packed = struct.pack('>HH', sign, registers[0])
        return struct.unpack('>i', packed)[0]

    def _decode_u32(registers):
        """ Unsigned 32-bit mixed-endian word"""
        packed = struct.pack('>HH', registers[1], registers[0])
        return struct.unpack('>I', packed)[0]
    
    def _decode_s32(registers):
        """ Signed 32-bit mixed-endian word"""
        packed = struct.pack('>HH', registers[1], registers[0])
        return struct.unpack('>i', packed)[0]

    def _decode_utf8(registers):
        return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.STRING)
    

    def _encoded(value):
        """ Convert a float or integer to big-endian register.
            Supports U16 only.
        """

        if value > U16_MAX: raise ValueError(f"Cannot write {value=} to U16 register.")
        elif value < 0:     raise ValueError(f"Cannot write negative {value=} to U16 register.")

        if isinstance(value, float):
            # Convert the float value to 4 bytes using IEEE 754 format TODO
            # value_bytes = list(struct.pack('>f', value))
            raise NotImplemented(f"Writing floats to registers is not yet supported.")

        value_bytes = list(value.to_bytes(4, byteorder='big', signed=False))
            
        return value_bytes
   
    def _validate_write_val(register_name:str, val):
        raise NotImplementedError()

if __name__ == "__main__":
    print(SungrowInverter._encoded(2**16-1, False))
    print(SungrowInverter._encoded(-1, False))
