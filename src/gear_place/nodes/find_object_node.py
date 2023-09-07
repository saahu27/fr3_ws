#!/usr/bin/env python3
import cv2
import rclpy
from gear_place.find_object import FindObject
from gear_place.object_depth import ObjectDepth

def dist_between_points(points : list):
    return __import__("math").sqrt(sum([(points[0][i]-points[1][i])**2 for i in range(2)]))

def main(args=None):
    rclpy.init(args=args)

    gear_center_values = [[0 for i in range(3)],[0 for i in range(3)]]
    c=1
    while sum([1 for i in range(6) if gear_center_values[i//3][i%3] not in [0.0, None]])!=6:
        find_object = FindObject()
        rclpy.spin_once(find_object)
        while find_object.ret_cent_gear().count(None) != 0:
            find_object.destroy_node()
            find_object = FindObject()
            rclpy.spin_once(find_object)
            c+=1
        object_depth = ObjectDepth([find_object.ret_cent_gear(), find_object.ret_edge_gear()])
        rclpy.spin_once(object_depth)

        object_depth.destroy_node()
        find_object.destroy_node()
        gear_center_values = object_depth.coordinates
    coord_str = "xyz"
    print("Gear center: "+",".join([coord_str[i]+": "+object_depth.coordinates[0][i] for i in range(3)]))
    print("Gear edge: "+",".join([coord_str[i]+": "+object_depth.coordinates[1][i] for i in range(3)]))
    distance_to_center_of_gear = dist_between_points(object_depth.coordinates)
    print("Distance between the edge and the center of the gear:",distance_to_center_of_gear)
    thresholds = sorted([0.03,0.07,distance_to_center_of_gear])
    print("The gear is "+["yellow","orange","green"][thresholds.index(distance_to_center_of_gear)])
    print(f"{c} tries to find the gear")
    cv2.imshow("Threshold image", find_object.thresh_image)
    cv2.imshow("Depth image", find_object.cv_image)
    cv2.waitKey(0)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
