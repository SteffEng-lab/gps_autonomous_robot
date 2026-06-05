from periphery import I2C
import time
import math

I2C_ADDR = 0x68
I2C_BUS = "/dev/i2c-8"

i2c = I2C(I2C_BUS)

acc_scale = 4     # +- g
gyro_scale = 500   # +- deg/s

mpu_cmds = {
    "PWR_MGMT_1": 0x6B,
    "WHO_AM_I": 0x75,
    "TEMP_L": 0x42,
    "TEMP_H": 0x41,
    "ACCEL_XOUT_H": 0x3B,
    "ACCEL_YOUT_H": 0x3D,
    "ACCEL_ZOUT_H": 0x3F,
    "ACCEL_CONFIG": 0x1C,
    "GYRO_XOUT_H": 0x43,
    "GYRO_YOUT_H": 0x45,
    "GYRO_ZOUT_H": 0x47,
    "GYRO_CONFIG": 0x1B
}

mpu_acc_conv = {        # Scale --> LSB Sensitivity
    2: 16384,
    4: 8192,
    8: 4096,
    16: 2048
}

mpu_acc_msg = {           # Scale --> Bit for register
    2: 0b00,
    4: 0b01,
    8: 0b10,
    16: 0b11
}

mpu_gyro_conv = {       # Scale --> LSB Sensitivity
    250: 131,
    500: 65.5,
    1000: 32.8,
    2000: 16.4
}

mpu_gyro_msg = {         # Scale --> Bit for register
    250: 0b00,
    500: 0b01,
    1000: 0b10,
    2000: 0b11
}

# Conv 16 bit raw unsigned integer two signed 16 bit integer two complement
def conv_to_two_compl(byte_H, byte_L):
    raw_val = ( (byte_H & 0xFF) << 8 | (byte_L & 0xFF) )
    if raw_val >= 0x8000:
        return raw_val - 2*0x8000 
    return raw_val


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

#== Set accelerometer scale ==#
# Write
acc_reg_val = mpu_acc_msg[acc_scale] << 3
i2c.transfer(I2C_ADDR, [I2C.Message([mpu_cmds["ACCEL_CONFIG"], acc_reg_val])])       # Write acc_reg_val into register
time.sleep(0.2)      # Wait

# Read: Confirm accelerometer scale
msgs = [I2C.Message([mpu_cmds["ACCEL_CONFIG"]]), I2C.Message(bytearray(1), read=True)]    # Second msg to read answer
i2c.transfer(I2C_ADDR, msgs)
res = msgs[1].data[0]
if res == acc_reg_val:
    print("Set acc scale successful!")
time.sleep(0.2)      # Wait

#== Set gyro scale ==#
# Write
gyr_reg_val = mpu_gyro_msg[gyro_scale] << 3
i2c.transfer(I2C_ADDR, [I2C.Message([mpu_cmds["GYRO_CONFIG"], gyr_reg_val])])       # Write gyr_reg_val into register
time.sleep(0.2)      # Wait

# Read: Confirm gyro scale
msgs = [I2C.Message([mpu_cmds["GYRO_CONFIG"]]), I2C.Message(bytearray(1), read=True)]    # Second msg to read answer
i2c.transfer(I2C_ADDR, msgs)
res = msgs[1].data[0]
if res == gyr_reg_val:
    print("Set gyro scale successful!")
time.sleep(0.2)      # Wait


time.sleep(3)

while True:
    msgs = [I2C.Message([mpu_cmds["TEMP_H"]]), I2C.Message(bytearray(2), read=True)]    # Only give TEMP_H, reads following second byte automatically from following register
    i2c.transfer(I2C_ADDR, msgs)
    temp_val = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / 340 + 36.53        # data[0] = High-Byte, data[1] = Low-Byte ; msgs[0] is writeMsg, msgs[1] is readMsg

    #== Read acceleration values ==#
    msgs = [I2C.Message([mpu_cmds["ACCEL_XOUT_H"]]), I2C.Message(bytearray(2), read=True)]    # Only give ACCEL_XOUT_H, reads following second byte automatically from following register
    i2c.transfer(I2C_ADDR, msgs)
    acc_x = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / mpu_acc_conv[acc_scale]

    msgs = [I2C.Message([mpu_cmds["ACCEL_YOUT_H"]]), I2C.Message(bytearray(2), read=True)]    # Only give ACCEL_YOUT_H, reads following second byte automatically from following register
    i2c.transfer(I2C_ADDR, msgs)
    acc_y = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / mpu_acc_conv[acc_scale]
    
    msgs = [I2C.Message([mpu_cmds["ACCEL_ZOUT_H"]]), I2C.Message(bytearray(2), read=True)]    # Only give ACCEL_ZOUT_H, reads following second byte automatically from following register
    i2c.transfer(I2C_ADDR, msgs)
    acc_z = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / mpu_acc_conv[acc_scale]

    #== Read gyroscope values ==#
    msgs = [I2C.Message([mpu_cmds["GYRO_XOUT_H"]]), I2C.Message(bytearray(2), read=True)]    # Only give GYRO_XOUT_H, reads following second byte automatically from following register
    i2c.transfer(I2C_ADDR, msgs)
    gyro_x = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / mpu_gyro_conv[gyro_scale]

    msgs = [I2C.Message([mpu_cmds["GYRO_YOUT_H"]]), I2C.Message(bytearray(2), read=True)]    # Only give GYRO_YOUT_H, reads following second byte automatically from following register
    i2c.transfer(I2C_ADDR, msgs)
    gyro_y = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / mpu_gyro_conv[gyro_scale]

    msgs = [I2C.Message([mpu_cmds["GYRO_ZOUT_H"]]), I2C.Message(bytearray(2), read=True)]    # Only give GYRO_ZOUT_H, reads following second byte automatically from following register
    i2c.transfer(I2C_ADDR, msgs)
    gyro_z = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / mpu_gyro_conv[gyro_scale]

    acc_abs = math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)
    print(f"Acc_X: {acc_x:.3f} \t Acc_Y: {acc_y:.3f} \t Acc_Z: {acc_z:.3f} \t Acc_abs: {acc_abs:.3f} \t Gyro_X: {gyro_x:.3f} \t Gyro_Y: {gyro_y:.3f} \t Gyro_Z: {gyro_z:.3f} \t Temp: {temp_val:.3f}")


    time.sleep(0.01)

i2c.close()