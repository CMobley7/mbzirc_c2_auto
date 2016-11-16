#!/usr/bin/env python

""" move2grasp.py - Version 1.0 2016-10-12

    This software chooses the left most wrench in an RGB image and outputs an
    estimate of its 3D location in space relative to the camera [x,y,z]
    Made by Jonathan Hodges

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.5

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details at:

    http://www.gnu.org/licenses/gpl.html

"""

import rospy
import rospkg
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped, Point, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal, MoveBaseFeedback
from sensor_msgs.msg import Image
import cv2
import cv2.cv as cv
from cv_bridge import CvBridge, CvBridgeError
from rospy.numpy_msg import numpy_msg
from rospy_tutorials.msg import Floats
import numpy as np
from decimal import *
import tf
import math
import random

class move2op():
    def __init__(self):
        # Name this node, it must be unique
	rospy.init_node('idvalve', anonymous=True)
        
        # Enable shutdown in rospy (This is important so we cancel any move_base goals
        # when the node is killed)
        rospy.on_shutdown(self.shutdown) # Set rospy to execute a shutdown function when exiting

        # Store camera parameters
        self.camera_fov_h = 1.5708
        self.camera_fov_v = 1.5708
        self.camera_pix_h = 1920
        self.camera_pix_v = 1080

        # Set up ROS subscriber callback routines
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/mybot/camera1/image_raw",Image,self.callback)
        self.image_pub = rospy.Publisher("image_topic_3",Image, queue_size=1)
        rospy.Subscriber("/valve", numpy_msg(Floats), self.callback_v_c, queue_size=1)

    def shutdown(self):
        rospy.sleep(1)

    # callback_v_c is used to store the valve center topic into the class to be
    # referenced by the other callback routines.
    def callback_v_c(self, data):
        self.v_c = data.data

    # callback_wrench is used to store the wrench topic into the class to be
    # referenced by the other callback routines.
    def callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        cimg = cv2.medianBlur(cv_image,5)
        cimg = cv2.cvtColor(cimg, cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(cimg, cv.CV_HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=500)

        if circles is not None:
            mn = min(circles[0,:,0])
            idx = np.argwhere(circles[0,:,0] == mn)
            i = circles[0,:][idx][0][0]
            val_loc = np.array([i[0],i[1],i[2]], dtype=np.float32)
            ee_position = rospy.get_param('ee_position')
            valve = rospy.get_param('valve')
            xA = valve[0]-ee_position[0]
            print "Valve in pixels: ", val_loc
            camera_y_mx = xA*np.tan(self.camera_fov_h/2)
            camera_y_mn = -1*xA*np.tan(self.camera_fov_h/2)
            camera_z_mx = xA*np.tan(self.camera_fov_v/2)
            camera_z_mn = -1*xA*np.tan(self.camera_fov_v/2)
            print "Camera ymn/ymx: ", camera_y_mn, camera_y_mx
            valve_y = (1-val_loc[0]/1920)*(camera_y_mx-camera_y_mn)+camera_y_mn
            valve_z = (1-val_loc[1]/1080)*(camera_z_mx-camera_z_mn)+camera_z_mn
            self.valve_id = np.array([xA, valve_y, valve_z],dtype=np.float32)
            print "Valve in m: ", self.valve_id
            rospy.set_param('valve_ID',[float(self.valve_id[0]), float(self.valve_id[1]), float(self.valve_id[2])])
            if np.power(valve_y*valve_y+valve_z*valve_z,0.5) < 0.01:
                rospy.set_param('smach_state','valveCenter')
            else:
                rospy.set_param('smach_state','valveOffCenter')
                valve_ID_ready_pos = rospy.get_param('valve')
                ee_position = rospy.get_param('ee_position')
                valve_ID_ready_pos[0] = valve[0]
                valve_ID_ready_pos[1] = valve_ID_ready_pos[1]+0.5*self.valve_id[1]
                valve_ID_ready_pos[2] = valve_ID_ready_pos[2]+0.5*self.valve_id[2]

                rospy.set_param('ee_position', [float(valve_ID_ready_pos[0]-0.5),
                                                float(valve_ID_ready_pos[1]),
                                                float(valve_ID_ready_pos[2])])
                rospy.set_param('valve', [float(valve_ID_ready_pos[0]),
                                                float(valve_ID_ready_pos[1]),
                                                float(valve_ID_ready_pos[2])])
        else:
            rospy.set_param('smach_state','valveNotFound')

        rospy.signal_shutdown('Ending node.')

if __name__ == '__main__':
    try:
        move2op()
#        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("idvalve finished.")

