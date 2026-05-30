import pyvesc
from pyvesc.messages.base import VESCMessage
import serial
import struct
import time
import select


class SetServoPosition(metaclass=VESCMessage):
    """Set servo position (0.0 = full left, 1.0 = full right)."""
    id = 12  # COMM_SET_SERVO_POS (datatypes.h), verified for VESC fw 7.0 / HW 410
    fields = [('servo_pos', 'h', 1000)]  # int16 / 1000


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


# --- DualShock 4 via /dev/hidraw0 (hid-generic, no hid-sony driver needed) ---
# USB input report layout (report ID = 0x01 is byte 0):
#   [0]  report ID (0x01)
#   [1]  LX  — L3 horizontal, 0-255, center=128
#   [2]  LY  — L3 vertical,   0-255, center=128
#   [3]  RX  — R3 horizontal
#   [4]  RY  — R3 vertical
#   [5]  dpad (bits 0-3) | square(4) | cross(5) | circle(6) | triangle(7)
#   [6]  L1(0) | R1(1) | L2(2) | R2(3) | share(4) | options(5) | L3(6) | R3(7)
#   [7]  PS(0) | touchpad(1)
#   [8]  L2 analog  0-255
#   [9]  R2 analog  0-255  ← throttle

HIDRAW_DEV   = '/dev/hidraw0'
REPORT_LEN   = 64

BTN_OPTIONS  = 0x20   # byte [6], bit 5
BTN_L1       = 0x01   # byte [6], bit 0
BTN_R1       = 0x02   # byte [6], bit 1

hidraw = open(HIDRAW_DEV, 'rb', buffering=0)
print("DualShock 4 connected via hidraw.")

# Safety enable: press OPTIONS button before the car responds to any input
print("Press OPTIONS button to enable...")
while True:
    report = hidraw.read(REPORT_LEN)
    if len(report) >= 10 and (report[6] & BTN_OPTIONS):
        break
print("Enabled!  R2 = throttle (0-100%)  |  L3 left/right = steering  |  Ctrl+C = stop")

# --- Init UART ---
serial_port = serial.Serial('/dev/ttyS2', 115200, timeout=0)
rx_buffer = bytearray()

duty_cycle = 0    # 0-100 (%)
servo_pos  = 0.5  # 0.0 (full left) - 1.0 (full right), 0.5 = center

try:
    while True:
        # Drain ALL queued HID reports, keep only the latest one to avoid lag
        latest = None
        while True:
            r, _, _ = select.select([hidraw], [], [], 0)
            if not r:
                break
            data = hidraw.read(REPORT_LEN)
            if len(data) >= 10:
                latest = data
        if latest is not None:
            # R2 analog [9]: 0-255 → duty_cycle 0-100
            duty_cycle = int(latest[9] / 255 * 100)
            # L3 horizontal [1]: 0-255, center=128 → servo_pos 0.0-1.0
            servo_pos = latest[1] / 255

        # Send VESC commands
        serial_port.write(pyvesc.encode(pyvesc.messages.SetDutyCycle(duty_cycle * 1000)))
        serial_port.write(pyvesc.encode(SetServoPosition(servo_pos)))
        serial_port.write(pyvesc.encode_request(pyvesc.messages.GetValues()))

        # Receive telemetry
        data = serial_port.read(512)
        if data:
            rx_buffer.extend(data)

        payload, consumed = parse_packet(rx_buffer)
        if consumed:
            rx_buffer = rx_buffer[consumed:]
            v = parse_get_values(payload)
            if v:
                print(
                    f"Duty: {duty_cycle:3d}%  "
                    f"Servo: {servo_pos:.2f}  "
                    f"RPM: {v['rpm']:6d}  "
                    f"Ubat: {v['v_in']:.2f} V  "
                    f"I_motor: {v['avg_motor_current']:.2f} A  "
                    f"Fault: {v['fault_code']}"
                )

        if len(rx_buffer) > 1024:
            rx_buffer.clear()

        time.sleep(0.01)  # 20 Hz control loop

except KeyboardInterrupt:
    pass
finally:
    print("\nStopping — duty=0, servo=center...")
    serial_port.write(pyvesc.encode(pyvesc.messages.SetDutyCycle(0)))
    serial_port.write(pyvesc.encode(SetServoPosition(0.5)))
    serial_port.close()
    hidraw.close()
    print("Done.")
