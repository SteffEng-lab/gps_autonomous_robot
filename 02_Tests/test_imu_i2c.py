from periphery import I2C
import time

I2C_ADDR = 0x68
I2C_BUS = "/dev/i2c-8"

i2c = I2C(I2C_BUS)

mpu_cmds = {
    "PWR_MGMT_1": 0x6B,
    "WHO_AM_I": 0x75,
    "TEMP_L": 0x42,
    "TEMP_H": 0x41
}

# Turn MPU on from Sleep Mode
i2c.transfer(I2C_ADDR, [I2C.Message([mpu_cmds["PWR_MGMT_1"], 0x00])])       # Write 0x00 into register
time.sleep(0.2)      # Wait for turn on

# Read
msgs = [I2C.Message([mpu_cmds["PWR_MGMT_1"]]), I2C.Message(bytearray(1), read=True)]    # Second msg to read answer
i2c.transfer(I2C_ADDR, msgs)
print(f"PWR_MGMT_1: {hex(msgs[1].data[0])}")

msgs = [I2C.Message([mpu_cmds["WHO_AM_I"]]), I2C.Message(bytearray(1), read=True)]
i2c.transfer(I2C_ADDR, msgs)
print(f"WHO_AM_I: {hex(msgs[1].data[0])}")

while True:
    msgs = [I2C.Message([mpu_cmds["TEMP_H"]]), I2C.Message(bytearray(2), read=True)]    # Only give TEMP_H, reads following second byte automatically from following register
    i2c.transfer(I2C_ADDR, msgs)
    #print(f"TEMP: {hex(msgs[1].data[1])}, {hex(msgs[1].data[0])}")          # data[0] = High-Byte, data[1] = Low-Byte ; msgs[0] is writeMsg, msgs[1] is readMsg

    temp_val = ( (msgs[1].data[0] & 0xFF) << 8 | (msgs[1].data[1] & 0xFF) ) / 340 + 36.53

    print(f"Temp: {temp_val}")

    time.sleep(0.01)

i2c.close()