#!/usr/bin/env python
import time
import rospy
import actionlib
import math
from control_msgs.msg import *
from trajectory_msgs.msg import *
from sensor_msgs.msg import JointState

def main():
	pub = rospy.Publisher('whatevertellsthearmwheretogo', JointState, queue_size=10)
	rospy.init_node('gripper_coords', anonymous=True)
	rate = rospy.Rate(10) # 10hz

	coords = JointState()
	coords.position = [0.0, 0.3, 0.2, 1.0, 0.0, 0.0, 0.0]
	while not rospy.is_shutdown():
		rospy.loginfo(coords)
		pub.publish(coords)
		rate.sleep()

	rospy.spin()

if __name__ == '__main__': main()

