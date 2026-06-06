# gps_publisher_node
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix

from robot_sensors.settings import GPS_USB_BUS
import serial
import pynmea2

ser = serial.Serial(GPS_USB_BUS, baudrate=9600, timeout=1)

class Gps_publisher(Node):
    def __init__(self):
        super().__init__('gps_publisher_node')
        self.publisher_ = self.create_publisher(NavSatFix, '/gps/fix', 10)
        
        timer_period = 0.01     # TODO: optimize / remove polling
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info("GPS publisher started")

    
    def timer_callback(self):
        line = ser.readline().decode("utf-8")

        if line.startswith('$GNGGA') or line.startswith('$GPGGA'):      # Check if position message
            msg = pynmea2.parse(line)

            pub_msg = NavSatFix()
            pub_msg.status.service = 1  # GPS

            if msg.gps_qual == 0:
                self.get_logger().warn("No GPS fix")
                pub_msg.status.status = -1      # No fix
            else:
                print(f"Lat: {msg.latitude}, Lon: {msg.longitude}, Alt: {msg.altitude}m")

                pub_msg.status.status = 0   # GPS fix
            
                pub_msg.latitude = msg.latitude
                pub_msg.longitude = msg.longitude
                if msg.altitude is not None:
                    pub_msg.altitude = msg.altitude

                pub_msg.position_covariance[0] = -1.0   

            self.publisher_.publish(pub_msg)

            self.get_logger().info("Publishing GPS data")

def main(args=None):
    rclpy.init(args=args)

    gps_publisher = Gps_publisher()

    try:
        rclpy.spin(gps_publisher)
    except KeyboardInterrupt:
        gps_publisher.get_logger().info("Shutting GPS publisher down")
        gps_publisher.destroy_node()
        # rclpy.shutdown()

if __name__ == '__main__':
    main()