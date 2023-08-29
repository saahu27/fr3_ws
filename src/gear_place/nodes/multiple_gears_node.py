#!/usr/bin/env python3
import cv2
import rclpy
from gear_place.multiple_gears import MultipleGears
from gear_place.object_depth import ObjectDepth

def main(args=None):
    rclpy.init(args=args)

    gear_center_values = [[0 for i in range(3)]]
    while (
                [0, 0, 0] in gear_center_target
                or sum([cent.count(None) for cent in gear_center_target]) > 0
            ) and len(gear_center_target) > 0:
                gear_center_target = []
                multiple_gears = MultipleGears()
                rclpy.spin_once(multiple_gears)
                while sum([cent.count(None) for cent in multiple_gears.g_centers]) != 0:
                    multiple_gears.destroy_node()
                    multiple_gears = MultipleGears()
                    rclpy.spin_once(multiple_gears)
                for g_center in multiple_gears.g_centers:
                    object_depth = ObjectDepth(g_center)
                    rclpy.spin_once(object_depth)  # Gets the distance from the camera
                    object_depth.destroy_node()  # Destroys the node to avoid errors on next loop
                    gear_center_target.append(
                        [object_depth.dist_x, object_depth.dist_x, object_depth.dist_x]
                    )
                multiple_gears.destroy_node()
    print("x: " + str(object_depth.dist_x), end="\t")
    print("y: " + str(object_depth.dist_y), end="\t")
    print("z: " + str(object_depth.dist_z) + "\n")
    print(f"{c} tries to find the gear")
    cv2.imshow("Threshold image", multiple_gears.thresh_image)
    cv2.imshow("Depth image", multiple_gears.cv_image)
    cv2.waitKey(0)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
