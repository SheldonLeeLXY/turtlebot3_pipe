import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu, Image
from cv_bridge import CvBridge
import cv2

from pyquaternion import Quaternion
import math

init_angle = None
curr_angle = None
last_angle = None
imgName = 1

class TurtlebotNode(Node):

    def __init__(self):
        super().__init__('turtlebot_node')

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.subscription = self.create_subscription(
            Imu,
            '/imu',
            self.listener_callback1,
            10)
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback2,
            10)
        self.subscription

        self.br = CvBridge()

    def timer_callback(self):
        msg = Twist()
        msg.angular.z = -0.1
        self.publisher_.publish(msg)
        # self.get_logger().info('Publishing: "%s"' % msg)

    def listener_callback1(self, msg):
        global init_angle
        global curr_angle

        orientation_q = msg.orientation
        q = Quaternion(orientation_q.w, orientation_q.x, orientation_q.y, orientation_q.z)
        if q.degrees > 0:
            curr_angle = q.degrees
        else:
            curr_angle = q.degrees + 360
        # print(q.axis)
        # print(curr_angle)

        if init_angle == None:
            init_angle = curr_angle
            print(init_angle)
        elif curr_angle > 359:
            self.get_logger().info('Robot has finished a full circle rotation!')
            stop()
        # self.get_logger().info('I heard: "%s"' % msg.orientation.w)
        # print(init_angle)

    def listener_callback2(self, data):
        global curr_angle
        global imgName
        global last_angle

        if (last_angle == None) or (abs(curr_angle - last_angle) > 20):
            self.get_logger().info('I heard: "%s"' % curr_angle)
            last_angle = curr_angle
            self.get_logger().info('Receiving video frame')
            current_frame = self.br.imgmsg_to_cv2(data)
            cv2.imshow("camera", current_frame)
            cv2.imwrite('/home/sheldon/ros_images/' + str(imgName) + '.jpg', current_frame)
            imgName += 1
            cv2.waitKey(1)

class StopPublisher(Node):

    def __init__(self):
        super().__init__('stop_publisher')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

def stop(args=None):
    stop_node = StopPublisher()

    rclpy.spin(stop_node)

    stop_node.destroy_node()
    rclpy.shutdown()


def main(args=None):
    rclpy.init(args = args)

    turtlebot_node = TurtlebotNode()

    rclpy.spin(turtlebot_node)

    turtlebot_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()