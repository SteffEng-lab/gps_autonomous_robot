from robot_sensors.settings import I2C_BUS
from periphery import I2C
import time

i2c = I2C(I2C_BUS)

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

# Read given number of bytes starting at given register address
def read_register(i2c_address, reg_address, num_bytes):
    msgs = [I2C.Message([reg_address]), I2C.Message(bytearray(num_bytes), read=True)]    # Second msg to read answer
    i2c.transfer(i2c_address, msgs)
    return msgs

# Write one byte into given register address
def write_byte_register(i2c_address, reg_address, value):
    i2c.transfer(i2c_address, [I2C.Message([reg_address, value])])       # Write one byte into given register

# Read temperature data
def read_temp_data(i2c_address):
    msgs = read_register(i2c_address, mpu_cmds["TEMP_H"], 2)
    return conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / 340 + 36.53        # data[0] = High-Byte, data[1] = Low-Byte ; msgs[0] is writeMsg, msgs[1] is readMsg

# Read all acceleration values in one burst
def read_acc_data(i2c_address, acc_scale):
    msgs = read_register(i2c_address, mpu_cmds["ACCEL_XOUT_H"], 6)   # # Only give ACCEL_XOUT_H, reads following six byte automatically from following registers (registers all next to each other)
    acc_x = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / mpu_acc_conv[acc_scale]
    acc_y = conv_to_two_compl(msgs[1].data[2], msgs[1].data[3]) / mpu_acc_conv[acc_scale]
    acc_z = conv_to_two_compl(msgs[1].data[4], msgs[1].data[5]) / mpu_acc_conv[acc_scale]

    return [acc_x, acc_y, acc_z]

# Read all gyroscope values in one burst
def read_gyro_data(i2c_address, gyro_scale):
    msgs = read_register(i2c_address, mpu_cmds["GYRO_XOUT_H"], 6)    # Only give GYRO_XOUT_H, reads following six byte automatically from following registers (registers all next to each other)
    gyro_x = conv_to_two_compl(msgs[1].data[0], msgs[1].data[1]) / mpu_gyro_conv[gyro_scale]
    gyro_y = conv_to_two_compl(msgs[1].data[2], msgs[1].data[3]) / mpu_gyro_conv[gyro_scale]
    gyro_z = conv_to_two_compl(msgs[1].data[4], msgs[1].data[5]) / mpu_gyro_conv[gyro_scale]

    return [gyro_x, gyro_y, gyro_z]

# Close I2C
def close_i2c():
    i2c.close()

def init_imu(i2c_addr, acc_scale, gyro_scale):
    # Turn MPU on from Sleep Mode
    i2c.transfer(i2c_addr, [I2C.Message([mpu_cmds["PWR_MGMT_1"], 0x00])])       # Write 0x00 into register
    time.sleep(0.2)      # Wait for turn on

    #== Set accelerometer scale ==#
    # Write
    acc_reg_val = mpu_acc_msg[acc_scale] << 3
    write_byte_register(i2c_addr, mpu_cmds["ACCEL_CONFIG"], acc_reg_val)     # Write acc_reg_val into register
    time.sleep(0.2)      # Wait

    # Read: Confirm accelerometer scale
    msgs = read_register(i2c_addr, mpu_cmds["ACCEL_CONFIG"], 1)
    res = msgs[1].data[0]
    if res == acc_reg_val:
        print("Set acc scale successful!")
    else:
        print("Set acc scale not successful")
        raise ValueError()
    time.sleep(0.2)      # Wait

    #== Set gyro scale ==#
    # Write
    gyr_reg_val = mpu_gyro_msg[gyro_scale] << 3
    write_byte_register(i2c_addr, mpu_cmds["GYRO_CONFIG"], gyr_reg_val)     # Write gyr_reg_val into register
    time.sleep(0.2)      # Wait

    # Read: Confirm gyro scale
    msgs = read_register(i2c_addr, mpu_cmds["GYRO_CONFIG"], 1)
    res = msgs[1].data[0]
    if res == gyr_reg_val:
        print("Set gyro scale successful!")
    else:
        print("Set gyro scale not successful")
        raise ValueError()
    time.sleep(0.2)      # Wait