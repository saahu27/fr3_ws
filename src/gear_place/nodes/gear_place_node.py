#!/usr/bin/env python3

import rclpy
from gear_place.gear_place_classes import GearPlace, Error, ConveyorClass


def main(args=None):
    rclpy.init(args=args)
    gear_width = 0.0085
    try:
        supervisor = GearPlace()
        conveyor_supervisor = ConveyorClass("aprs_ros_conveyor")
        supervisor.wait(5)
        supervisor._call_open_gripper_service()
        supervisor._call_move_to_named_pose_service("home_2")
        supervisor._call_pick_up_multiple_gears(0.0095)

        # supervisor._call_move_to_named_pose_service("above_conveyor")
        # supervisor.wait(2) 
        # while True:
        #     supervisor._call_pick_up_moving_gear_service(gear_width, True)  # Moves to above the gear, opens the gripper to the maximum, then down to the gear, grabs the gear, then picks it up
        #     supervisor._call_move_to_named_pose_service("home")
        #     supervisor._call_put_gear_down_camera(-0.5)
        #     supervisor._call_move_to_named_pose_service("above_conveyor")


        # conveyor_supervisor._enable_conveyor_service(True)
        # conveyor_supervisor._set_conveyor_state_service(speed=50, direction=0)
        # conveyor_supervisor._enable_conveyor_service(False)

    except Error as e:
        print(e)


if __name__ == "__main__":
    main()
