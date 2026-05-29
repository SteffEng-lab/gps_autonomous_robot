import pyvesc
from pyvesc.messages.base import VESCMessage
import serial
import struct
import time


class SetServoPosition(metaclass=VESCMessage):
    """Set servo position (0.0 = full left, 1.0 = full right)."""
    id = 58
    fields = [('servo_pos', 'h', 1000)]  # int16 / 1000, VESC erwartet kein float32


def parse_packet(buf):
    """Find and extract first complete VESC packet from buffer.
    Returns (payload_bytes, consumed_bytes) or (None, 0).
    """
    for i in range(len(buf)):
        if buf[i] != 0x02 or i + 3 >= len(buf):
            continue
        payload_len = buf[i + 1]
        end = i + 2 + payload_len + 3  # 2 header + payload + 2 crc + 1 terminator
        if end > len(buf):
            continue
        if buf[end - 1] == 0x03:
            return bytes(buf[i + 2: i + 2 + payload_len]), end
    return None, 0


def parse_get_values(payload):
    """Decode COMM_GET_VALUES response (VESC firmware 5.x/6.x format)."""
    if not payload or payload[0] != 4:
        return None
    d = payload[1:]
    if len(d) < 62:
        return None
    o = 0
    v = {}
    v['temp_fet']           = struct.unpack_from('>h', d, o)[0] / 10.0;     o += 2
    v['temp_motor']         = struct.unpack_from('>h', d, o)[0] / 10.0;     o += 2
    v['avg_motor_current']  = struct.unpack_from('>i', d, o)[0] / 100.0;    o += 4
    v['avg_input_current']  = struct.unpack_from('>i', d, o)[0] / 100.0;    o += 4
    v['avg_id']             = struct.unpack_from('>i', d, o)[0] / 100.0;    o += 4
    v['avg_iq']             = struct.unpack_from('>i', d, o)[0] / 100.0;    o += 4
    v['duty_cycle_now']     = struct.unpack_from('>h', d, o)[0] / 1000.0;   o += 2
    v['rpm']                = struct.unpack_from('>i', d, o)[0];             o += 4
    v['v_in']               = struct.unpack_from('>h', d, o)[0] / 10.0;     o += 2
    v['amp_hours']          = struct.unpack_from('>i', d, o)[0] / 10000.0;  o += 4
    v['amp_hours_charged']  = struct.unpack_from('>i', d, o)[0] / 10000.0;  o += 4
    v['watt_hours']         = struct.unpack_from('>i', d, o)[0] / 10000.0;  o += 4
    v['watt_hours_charged'] = struct.unpack_from('>i', d, o)[0] / 10000.0;  o += 4
    v['tachometer']         = struct.unpack_from('>i', d, o)[0];             o += 4
    v['tachometer_abs']     = struct.unpack_from('>i', d, o)[0];             o += 4
    v['fault_code']         = d[o];                                           o += 1
    return v


serial_port = serial.Serial('/dev/ttyS2', 115200, timeout=0.1)
rx_buffer = bytearray()

try:
    while True:
        # Senden
        duty_cycle = 5
        serial_port.write(pyvesc.encode(pyvesc.messages.SetDutyCycle(duty_cycle*1000)))   # 10000 = 10 %
        #serial_port.write(pyvesc.encode(SetServoPosition(0.9)))                 # 0.0 = links, 0.5 = Mitte, 1.0 = rechts
        serial_port.write(pyvesc.encode_request(pyvesc.messages.GetValues()))

        # Empfangen
        data = serial_port.read(512)
        if data:
            rx_buffer.extend(data)

        payload, consumed = parse_packet(rx_buffer)
        if consumed:
            rx_buffer = rx_buffer[consumed:]
            v = parse_get_values(payload)
            if v:
                print(f"\nRPM:        {v['rpm']}")
                print(f"Ubat:       {v['v_in']:.2f} V")
                print(f"I_motor:    {v['avg_motor_current']:.2f} A")
                print(f"I_input:    {v['avg_input_current']:.2f} A")
                print(f"Duty Cycle: {v['duty_cycle_now']:.3f}")
                print(f"Temp FET:   {v['temp_fet']:.1f} °C")
                print(f"Temp Motor: {v['temp_motor']:.1f} °C")
                print(f"Fault Code: {v['fault_code']}")

        if len(rx_buffer) > 1024:
            rx_buffer.clear()

        time.sleep(0.1)

except:
    print("Stop")
    duty_cycle = 0
    serial_port.write(pyvesc.encode(pyvesc.messages.SetDutyCycle(duty_cycle*1000)))   # 10000 = 10 %
    serial_port.close()
