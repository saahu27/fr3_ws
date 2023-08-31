import cv2
from rclpy.node import Node

import numpy as np

from sensor_msgs.msg import Image  # msg for recieving the image

from cv_bridge import (
    CvBridge,
)  # for converting the sensor_msgs.msg.image to opencv image


class MultipleGears(Node):
    def __init__(self):
        super().__init__("multiple_gears")
        self.bridge = CvBridge()
        self.cv_image = None
        self.ran = False
        self.g_centers = []
        self.thresh_image = None
        self.declare_parameter("thresh_value", 50)
        self.subscription = self.create_subscription(
            Image, "/camera/depth/image_rect_raw", self.listener_callback, 1
        )
        self.subscription  # prevent unused variable warning

    def closest_to_circle(self, contours):
        """
        Returns the contour which is closest to a circle
        """
        circle_areas = []
        areas = [cv2.contourArea(cnt) for cnt in contours]
        for cnt in contours:
            (_, _), radius = cv2.minEnclosingCircle(cnt)
            circle_areas.append(__import__("math").pi * radius**2)
        diffs = [areas[i] / circle_areas[i] for i in range(len(areas))]
        return [i for i in range(len(diffs)) if diffs[i] >= 0.9]

    def remove_bad_contours(self, contours: tuple):
        """
        Removes contours which are too small and ones with too few sides to be the gear
        """
        minimum_contour_area = 3000
        maximum_contour_area = 50000
        new_contours = [cnt for cnt in contours if not cv2.isContourConvex(cnt)]
        filtered_contours = []
        for cnt in new_contours:
            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if (
                len(approx) > 10
                and cv2.contourArea(cnt) > minimum_contour_area
                and maximum_contour_area > cv2.contourArea(cnt)
            ):
                filtered_contours.append(cnt)
        return filtered_contours

    def listener_callback(self, msg):
        """
        Gets the image from the contour, blurs it, applies a threshold, finds the contours.
        Then, the functions above are used to find the gear out of all the contours that are found.
        It then finds the center of the gear contour.
        """
        self.ran = True
        min_thresh, max_thresh = 0,150
        thresh_value = (
            self.get_parameter("thresh_value").get_parameter_value().integer_value
        )
        cv_image = self.bridge.imgmsg_to_cv2(msg, "32FC1")
        cv_image_array = np.array(cv_image, dtype=np.dtype("u1"))
        self.cv_image = cv_image_array
        alpha = 2.5  # Contrast control (1.0-3.0)
        beta = -65  # Brightness control (-100-100)
        self.cv_image = cv2.convertScaleAbs(self.cv_image, alpha=alpha, beta=beta)
        self.original_image = self.cv_image.copy()
        blurred_img = cv2.GaussianBlur(self.cv_image, (7, 7), 0)
        for _ in range(3):
            blurred_img = cv2.GaussianBlur(blurred_img, (7, 7), 0)
        contours_left = 0
        valid_contours = []
        self.get_logger().info("Starting scan")
        for i in range(min_thresh,max_thresh+1):
            thresh_value = i
            _, self.thresh_image = cv2.threshold(
                blurred_img, thresh_value, 255, cv2.THRESH_BINARY_INV
            )
            contours, _ = cv2.findContours(
                self.thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            before_remove = len(contours)
            contours = self.remove_bad_contours(contours)
            contours_left = len(contours)
            if contours_left >= 1:
                for ind in self.closest_to_circle(contours):
                    (x, y), self.radius = cv2.minEnclosingCircle(contours[ind])
                    if (int(x), int(y)) not in self.g_centers:
                        self.g_centers.append((int(x), int(y)))
        if len(valid_contours) == 0:
            return
        self.get_logger().info(
            f"{len(valid_contours)} gears found at thresh value {thresh_value}! {before_remove - len(contours)} contours were removed."
        )
