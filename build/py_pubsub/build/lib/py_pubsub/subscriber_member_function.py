import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu, Image
from cv_bridge import CvBridge
import cv2

angle = None
imgName = 1

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
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

    def listener_callback1(self, msg):
        global angle
        if angle == None:
            angle = msg.orientation.w
        elif abs(angle + msg.orientation.w) < 0.01:
            self.get_logger().info('Robot has finished a full circle rotation!')
            exit()
        self.get_logger().info('I heard: "%s"' % msg.orientation.w)
        print(angle)

    def listener_callback2(self, data):
        self.get_logger().info('Receiving video frame')

        current_frame = self.br.imgmsg_to_cv2(data)

        cv2.imshow("camera", current_frame)
        global imgName
        # cv2.imwrite('/home/sheldon/ros_images/' + str(imgName) + '.jpg', current_frame)
        imgName += 1
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()