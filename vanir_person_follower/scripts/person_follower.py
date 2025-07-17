#!/usr/bin/env python3   

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

CONFIDENCE_THRESHOLD = 0.8


class PersonFollower(Node):
    def __init__(self):
        super().__init__('aruco_detector')

        self.object_detector = cv2.createBackgroundSubtractorMOG2()

        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',  
            self.image_callback,
            10)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # # edges = cv2.Canny(gray, 80, 240)

            # mask = self.object_detector.apply(gray)
            # contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # for cnt in contours: 
            #     cv2.drawContours(gray, [cnt], -1, (0,255,0), 2) # -1 to draw all contours

            results = model.track(frame, persist=True)
            res_frame = results[0].plot()

        except Exception as e:
            self.get_logger().error(f'CV Bridge error: {e}')
            return

        cv2.imshow("Frame", res_frame)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = PersonFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
