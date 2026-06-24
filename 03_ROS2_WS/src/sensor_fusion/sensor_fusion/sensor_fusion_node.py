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
        cov_Q_process = np.diag([0, 0, 0.5**2, 0.5**2])        # Velocity process noise [m/s per step]
        cov_Q_imu = np.array([[0.02087**2, 0], [0, 0.02382**2]])
        cov_Q = cov_Q_process + sys_B @ cov_Q_imu @ sys_B.T

        self.kalman_filter = Linear_Kalman_Filter(sys_A, sys_B, sys_H, cov_Q, cov_R)

        # Initial gps position, initialized when first gps fix arrives
        self.lat_0 = None
        self.long_0 = None

        self.is_imu_calibrated = False
        self.imu_calibration_counter = 0
        self.IMU_CALIBRATION_MAX_STEPS = 500
        self.imu_acc_sum = np.zeros(2)
        self.imu_bias = np.zeros(2)

        self.gps_average_counter = 0
        self.GPS_AVERAGE_MAX_STEPS = 10
        self.gps_average_readings = np.zeros((self.GPS_AVERAGE_MAX_STEPS, 2))
    

    def gps_callback(self, msg):
        self.get_logger().info("GPS data received")

        if msg.status.status >= 0:      # GPS fix available
            lat = msg.latitude
            long = msg.longitude

            if self.lat_0 is None:
                # Collect readings to average initial position
                if self.gps_average_counter < self.GPS_AVERAGE_MAX_STEPS:
                    self.gps_average_readings[self.gps_average_counter] = [lat, long]
                    self.gps_average_counter += 1
                    return
                else:
                    avg_lat  = np.mean(self.gps_average_readings[:, 0])
                    avg_long = np.mean(self.gps_average_readings[:, 1])
                    self.set_initial_pos(avg_lat, avg_long)
                    self.kalman_filter.est_state     = np.zeros((4, 1))
                    self.kalman_filter.est_error_cov = np.eye(4) * 100
                    self.get_logger().info(f"Initial position set: lat={avg_lat:.6f}, long={avg_long:.6f}")
                    return

            dx, dy = self.latlong_to_pos(lat, long, self.lat_0, self.long_0)

            # Run correction step
            self.kalman_filter.current_z = np.array([[dx], [dy]])
            self.kalman_filter.correct()
            self.get_logger().info(f"GPS corrected: x={self.kalman_filter.est_state[0,0]:.3f} y={self.kalman_filter.est_state[1,0]:.3f} vx={self.kalman_filter.est_state[2,0]:.4f} vy={self.kalman_filter.est_state[3,0]:.4f}")
        else:
            self.get_logger().info("No GPS fix available")

    def imu_callback(self, msg):
        #self.get_logger().info("IMU data received")
        acc_x = msg.linear_acceleration.x
        acc_y = msg.linear_acceleration.y

        # Check if IMU has been calibrated already or not
        if not self.is_imu_calibrated:
            if self.imu_calibration_counter >= self.IMU_CALIBRATION_MAX_STEPS:
                self.imu_bias = self.imu_acc_sum / self.IMU_CALIBRATION_MAX_STEPS
                self.is_imu_calibrated = True
                self.get_logger().info(f"IMU calibrated. Bias: ax={self.imu_bias[0]:.5f}, ay={self.imu_bias[1]:.5f}")
            else:
                self.imu_acc_sum += np.array([acc_x, acc_y])
                self.imu_calibration_counter += 1
                return

        # Run prediction step (only after first GPS fix has initialized est_state)
        if self.kalman_filter.est_state is None:
            return

        self.kalman_filter.current_u = np.array([[acc_x - self.imu_bias[0]], [acc_y - self.imu_bias[1]]])
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
