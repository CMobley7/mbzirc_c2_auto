# mbzirc_c2_auto

1. Install ubuntu 14.04 LTS with auto-install updates enables.
2. sudo apt-get update
3. sudo apt-get upgrade
4. Install ros indigo (instructions from: http://wiki.ros.org/indigo/Installation/Ubuntu)
    * sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
    * sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net --recv-key 0xB01FA116
    * sudo apt-get update
    * sudo apt-get install ros-indigo-desktop-full
    * echo "source /opt/ros/indigo/setup.bash" >> ~/.bashrc
    * source ~/.bashrc
    * type "roscore" in terminal to confirm ros installation is working properly, ctl+c to kill it
5. Setup a catkin workspace (instructions from http://wiki.ros.org/catkin/Tutorials/create_a_workspace)
    * mkdir -p ~/catkin_ws/src
    * cd ~/catkin_ws/src
    * catkin_init_workspace
    * cd ~/catkin_ws
    * catkin_make
    * source devel/setup.bash
    * echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
6. Install ROS packages we use
    * sudo apt-get install ros-indigo-husky-*
    * sudo apt-get install ros-indigo-urg-*
    * sudo apt-get install ros-indigo-teleop-*
    * sudo apt-get install ros-indigo-rospy-*

7. Install our packages
    * Copy mbzirc_c2 into ~/catkin_ws/src/
    * cd ~/catkin_ws/src/mbzirc_c2/mbzirc_c2_auto/bin
    * sudo chmod +x *.py
    * sudo cp ~/catkin_ws/src/mbzirc_c2/mbzirc_c2_auto/sick_lms1xx.urdf.xacro /opt/ros/indigo/share/lms1xx/urdf
    * cd ~/catkin_ws
    * catkin_make
    * source devel/setup.bash
    * roslaunch mbzirc_ch2_auto ch2-sim.launch
