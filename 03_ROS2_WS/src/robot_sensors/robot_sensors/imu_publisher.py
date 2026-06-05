# imu_publisher_node
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

import math
from robot_sensors.imu_helper import read_acc_data, read_gyro_data, read_temp_data, init_imu
from robot_sensors.settings import I2C_ADDR, ACC_SCALE, GYRO_SCALE, GRAVITY_CONSTANT


class Imu_publisher(Node):
    def __init__(self):
        super().__init__('imu_publisher_node')
        self.publisher_ = self.create_publisher(Imu, '/imu/data_raw', 10)
        
        timer_period = 0.01
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info("IMU publisher started")

        self.get_logger().info("Initializing IMU")
        init_imu(I2C_ADDR, ACC_SCALE, GYRO_SCALE)
        self.get_logger().info("IMU initialized successfully!")

    
    def timer_callback(self):
        msg = Imu()
        
        #== Read temperature values ==#
        temp_data = read_temp_data(I2C_ADDR)

        #== Read acceleration values ==#
        acc_data = read_acc_data(I2C_ADDR, ACC_SCALE)
        msg.linear_acceleration.x = acc_data[0] * GRAVITY_CONSTANT
        msg.linear_acceleration.y = acc_data[1] * GRAVITY_CONSTANT
        msg.linear_acceleration.z = acc_data[2] * GRAVITY_CONSTANT

        # Set covariance
        msg.linear_acceleration_covariance[0] = -1

        #== Read gyroscope values ==#
        gyro_data = read_gyro_data(I2C_ADDR, GYRO_SCALE)
        msg.angular_velocity.x = gyro_data[0] * math.pi/180     # conv deg/s to rad/s
        msg.angular_velocity.y = gyro_data[1] * math.pi/180
        msg.angular_velocity.z = gyro_data[2] * math.pi/180
        
        # Set covariance
        msg.angular_velocity_covariance[0] = -1

        msg.orientation_covariance[0] = -1.0            

        self.publisher_.publish(msg)
        #self.get_logger().info("Publishing IMU data")

def main(args=None):
    rclpy.init(args=args)

    imu_publisher = Imu_publisher()

    try:
        rclpy.spin(imu_publisher)
    except KeyboardInterrupt:
        imu_publisher.get_logger().info("Shutting IMU publisher down")
        imu_publisher.destroy_node()
        # rclpy.shutdown()

if __name__ == '__main__':
    main()