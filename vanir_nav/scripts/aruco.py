#!/usr/bin/env python3   

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class ArucoDetector(Node):
    def __init__(self):
        super().__init__('aruco_detector')

        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',  
            self.image_callback,
            10)

        # Load predefined dictionary
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
        self.parameters = cv2.aruco.DetectorParameters()

        self.get_logger().info('Aruco Detector Initialized')

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'CV Bridge error: {e}')
            return
        
        detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

        # Detect ArUco markers
        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            for i, corner in zip(ids, corners):
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                self.get_logger().info(f'Detected Marker ID: {i[0]}')

        # Optionally show the image (for debugging)
        cv2.imshow("Aruco Detection", frame)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ArucoDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
