import serial
import pynmea2

ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)

while True:
    line = ser.readline().decode("utf-8")
    #msg = pynmea2.parse(line)

    #print(msg.latitude)

    if line.startswith('$GNGGA') or line.startswith('$GPGGA'):
        msg = pynmea2.parse(line)
        print(f"Lat: {msg.latitude}, Lon: {msg.longitude}, Alt: {msg.altitude}m")
