#!/usr/bin/env python3   

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
import logging

logging.getLogger("ultralytics").setLevel(logging.CRITICAL)

model = YOLO("yolov8n.pt")

CONFIDENCE_THRESHOLD = 0.8


class PersonFollower(Node):
    def __init__(self):
        super().__init__('person_follower')

        self.object_detector = cv2.createBackgroundSubtractorMOG2()

        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',  
            self.image_callback,
            10)
        
        self.depth_sub = self.create_subscription(
            Image,
            '/depth_camera', 
            self.depth_callback,
            10)
        
        self.last_depth_image = None

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            height, width = frame.shape[:2]

            results = model.track(frame, persist=True)
            res_frame = results[0].plot()

            if self.last_depth_image is not None and results[0].boxes is not None:
                boxes = results[0].boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    if model.names[cls_id] == "person":
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2

                        if 0 <= center_y < self.last_depth_image.shape[0] and 0 <= center_x < self.last_depth_image.shape[1]:
                            depth = self.last_depth_image[center_y, center_x]

                            if not (depth == 0.0 or depth is None or depth != depth):
                                cv2.putText(res_frame,
                                            f"Depth: {depth:.2f} m",
                                            (x1, y1 - 20),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.8, (0, 255, 0), 2)

        except Exception as e:
            self.get_logger().error(f'CV Bridge error: {e}')
            return

        cv2.imshow("Frame", res_frame)

        cv2.waitKey(1)

    def depth_callback(self, msg):
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, "32FC1")
            self.last_depth_image = self.depth_image

        except Exception as e:
            self.get_logger().error(f"Error converting depth image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = PersonFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
