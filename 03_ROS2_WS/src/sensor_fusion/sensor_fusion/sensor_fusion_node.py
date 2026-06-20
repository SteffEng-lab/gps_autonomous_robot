import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from sensor_msgs.msg import NavSatFix
from nav_msgs.msg import Odometry


import numpy as np

from sensor_fusion.linear_kalman_filter import Linear_Kalman_Filter
from sensor_fusion.settings import R_EARTH

class Sensor_Fusion(Node):
    def __init__(self):
        super().__init__('sensor_fusion')

        self.gps_subscriber = self.create_subscription(NavSatFix, '/gps/fix', self.gps_callback, 10)
        self.imu_subscriber = self.create_subscription(Imu, '/imu/data_raw', self.imu_callback, 10)

        self.odom_publisher = self.create_publisher(Odometry, '/odom', 10)

        dt = 0.01
        sys_A = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]])
        sys_B = np.array([[1/2*dt**2, 0], [0, 1/2*dt**2], [dt, 0], [0, dt]])
        sys_H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
        
        cov_R = np.array([[1.255**2, 0], [0, 1.599**2]])       # Values from noise analysis
        cov_Q_process = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        cov_Q_imu = np.array([[0.02087**2, 0], [0, 0.02382**2]])
        cov_Q = cov_Q_process + sys_B @ cov_Q_imu @ sys_B.T

        self.kalman_filter = Linear_Kalman_Filter(sys_A, sys_B, sys_H, cov_Q, cov_R)

        # Initial gps position, initialized when first gps fix arrives
        self.lat_0 = None
        self.long_0 = None

    def gps_callback(self, msg):
        self.get_logger().info("GPS data received")

        if msg.status.status >= 0:      # GPS fix available
            lat = msg.latitude
            long = msg.longitude

            if self.lat_0 is None or self.long_0 is None:       # Set initial position if not set yet
                self.set_initial_pos(lat, long)

            dx, dy = self.latlong_to_pos(lat, long, self.lat_0, self.long_0)

            # Run correction step
            self.kalman_filter.current_z = np.array([[dx], [dy]])
            self.kalman_filter.correct()
        else:
            self.get_logger().info("No GPS fix available")

    def imu_callback(self, msg):
        #self.get_logger().info("IMU data received")
        acc_x = msg.linear_acceleration.x
        acc_y = msg.linear_acceleration.y

        # Run prediction step
        self.kalman_filter.current_u = np.array([[acc_x], [acc_y]])
        self.kalman_filter.predict()

        # Publish prediction
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'

        msg.pose.pose.position.x = float(self.kalman_filter.pred_state[0, 0])
        msg.pose.pose.position.y = float(self.kalman_filter.pred_state[1, 0])

        msg.twist.twist.linear.x = float(self.kalman_filter.pred_state[2, 0])
        msg.twist.twist.linear.y = float(self.kalman_filter.pred_state[3, 0])

        self.odom_publisher.publish(msg)

    def latlong_to_pos(self, lat, long, lat_0, long_0):
        dx = (np.radians(long) - np.radians(long_0)) * np.cos(np.radians(lat_0)) * R_EARTH
        dy = (np.radians(lat) - np.radians(lat_0)) * R_EARTH

        return dx, dy

    def set_initial_pos(self, lat_0, long_0):
        self.lat_0 = lat_0
        self.long_0 = long_0

def main(args=None):
    rclpy.init(args=args)

    linear_kf = Sensor_Fusion()

    try:
        rclpy.spin(linear_kf)
    except KeyboardInterrupt:
        linear_kf.get_logger().info("Shutting Kalman Filter down")
        linear_kf.destroy_node()
        #rclpy.shutdown()

if __name__ == '__main__':
    main()
