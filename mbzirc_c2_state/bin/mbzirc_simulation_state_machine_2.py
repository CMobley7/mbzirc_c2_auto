#!/usr/bin/env python

""" mbzirc_simulation_state_machine.py - Version 1.0 2016-10-12

    This program node defines the state machine for Challenge 2

    Author: Alan Lattimer (alattimer at jensenhughes dot com)

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
import smach
import smach_ros
from navigate_states import *
from orient_states import *
from grasp_wrench_states import *
from operate_valve_states import *
from control_msgs.msg import *
from trajectory_msgs.msg import *

# *************************************************************************
# State classes are defined in files associated with the sub-state machine
#
# navigation_states.py
#   FindBoard
#
# orient_states.py
#   Orient
#
# grasp_wrench_states.py
#   MoveToReady
#   MoveToReadyWreanch
#   IDWrench
#   MoveToWrench
#   MoveToGrasp
#   GraspWrench
#
# operate_valve_states.py
#   MoveToValveReady
#   IDValve
#   MoveToValve
#   MoveToOperate
#   RotateValve
#
# *************************************************************************

def main():
    """Defines the state machines for Smach
    """

    rospy.init_node('mbzirc_simulation_state_machine', anonymous=True)

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['success', 'failure'])

    # Open the container
    with sm:

        # Create the sub SMACH state machine for navigation
        sm_nav = smach.StateMachine(outcomes=['readyToOrient',
                                              'moveArm'])

        # Create the sub SMACH state machine for orienting
        sm_orient = smach.StateMachine(outcomes=['readyToGrabWrench'])

        # Create the sub SMACH state machine for grabbing wrench
        sm_wrench = smach.StateMachine(outcomes=['readyToOperate',
                                                 'testingArm',
                                                 'failedToMove',
                                                 'droppedWrench',
                                                 'wrenchIDFailed'])

        # Create the sub SMACH state machine operating the valve
        sm_valve = smach.StateMachine(outcomes=['valveOperated',
                                                'failedToMove',
                                                'failedToStowArm',
                                                'valveIDFailed',
                                                'lostWrench',
                                                'valveStuck'])

        # Define userdata for the state machines
        sm_nav.userdata.test_arm = False

        sm_wrench.userdata.move_counter = 0
        sm_wrench.userdata.max_move_retries = 1
        sm_wrench.userdata.have_wrench = False

        sm_valve.userdata.move_counter = 0
        sm_valve.userdata.max_move_retries = 1
        sm_valve.userdata.valve_centered = False
        sm_valve.userdata.valve_turned = False

        # Define the NAVIGATE State Machine
        with sm_nav:
            smach.StateMachine.add('FINDBOARD', FindBoard(),
                                   transitions={'atBoard' : 'readyToOrient',
                                                'skipNav' : 'moveArm'},
                                   remapping={'test_arm_in' : 'test_arm'})

        # Define the ORIENT State Machine
        with sm_orient:
            smach.StateMachine.add('ORIENT_HUSKY', Orient(),
                                   transitions={'oriented' : 'readyToGrabWrench'})

        # Define the GRAB_WRENCH State Machine
        with sm_wrench:
            smach.StateMachine.add('MOVE_TO_READY', MoveToReady(),
                                   transitions={'atReady' : 'MOVE_WRENCH_READY',
                                                'moveStuck' : 'MOVE_TO_READY',
                                                'moveFailed' : 'failedToMove'},
                                   remapping={'move_counter_in' : 'move_counter',
                                              'max_retries' : 'max_move_retries',
                                              'move_counter_out' : 'move_counter'})

            smach.StateMachine.add('MOVE_WRENCH_READY', MoveToWrenchReady(),
                                   transitions={'atWrenchReady' : 'ID_WRENCH',
                                                'moveToOperate' : 'readyToOperate',
                                                'moveStuck' : 'MOVE_WRENCH_READY',
                                                'moveFailed' : 'failedToMove'},
                                   remapping={'got_wrench' : 'have_wrench',
                                              'move_counter_in' : 'move_counter',
                                              'max_retries' : 'max_move_retries',
                                              'move_counter_out' : 'move_counter'})

            smach.StateMachine.add('ID_WRENCH', IDWrench(),
                                   transitions={'wrenchFound' : 'MOVE_TO_WRENCH',
                                                'armTest' : 'testingArm',
                                                'wrenchNotFound' : 'wrenchIDFailed'})

            smach.StateMachine.add('MOVE_TO_WRENCH', MoveToWrench(),
                                   transitions={'atWrench' : 'MOVE_TO_GRASP',
                                                'moveStuck' : 'MOVE_TO_WRENCH',
                                                'moveFailed' : 'failedToMove'},
                                   remapping={'move_counter_in' : 'move_counter',
                                              'max_retries' : 'max_move_retries',
                                              'move_counter_out' : 'move_counter'})

            smach.StateMachine.add('MOVE_TO_GRASP', MoveToGrasp(),
                                   transitions={'readyToGrasp' : 'GRASP_WRENCH'})

            smach.StateMachine.add('GRASP_WRENCH', GraspWrench(),
                                   transitions={'wrenchGrasped' : 'MOVE_WRENCH_READY',
                                                'gripFailure' : 'droppedWrench'},
                                   remapping={'got_wrench' : 'have_wrench'})

        # Define the OPERATE_VALVE State Machine
        with sm_valve:
            smach.StateMachine.add('STOW_ARM', DriveToValve(),
                                   transitions={'armStowed' : 'DRIVE_TO_VALVE',
                                                'stowArmFailed' : 'failedToStowArm'})

            smach.StateMachine.add('DRIVE_TO_VALVE', DriveToValve(),
                                   transitions={'atValveDrive' : 'MOVE_VALVE_READY',
                                                'moveFailed' : 'failedToMove'})

            smach.StateMachine.add('MOVE_VALVE_READY', MoveToValveReady(),
                                   transitions={'atValveReady' : 'ID_VALVE',
                                                'moveStuck' : 'MOVE_VALVE_READY',
                                                'moveFailed' : 'failedToMove'},
                                   remapping={'move_counter_in' : 'move_counter',
                                              'max_retries' : 'max_move_retries',
                                              'move_counter_out' : 'move_counter'})

            smach.StateMachine.add('ID_VALVE', IDValve(),
                                   transitions={'valveLocated' : 'MOVE_TO_VALVE',
                                                'valveNotFound' : 'valveIDFailed'},
                                   remapping={'valve_centered_out' : 'valve_centered'})

            smach.StateMachine.add('MOVE_TO_VALVE', MoveToValve(),
                                   transitions={'servoArm' : 'SERVO_TO_VALVE',
                                                'moveForward' : 'MOVE_TO_OPERATE'},
                                   remapping={'valve_centered_in' : 'valve_centered'})

            smach.StateMachine.add('SERVO_TO_VALVE', MoveToOperate(),
                                   transitions={'moveSuccess' : 'ID_VALVE',
                                                'moveFailed' : 'failedToMove'})


            smach.StateMachine.add('MOVE_TO_OPERATE', MoveToOperate(),
                                   transitions={'wrenchFell' : 'lostWrench',
                                                'wrenchOnValve' : 'ROTATE_VALVE'})

            smach.StateMachine.add('ROTATE_VALVE', RotateValve(),
                                   transitions={'wrenchFell' : 'lostWrench',
                                                'cantTurnValve' : 'valveStuck',
                                                'turnedValve' : 'valveOperated'})

        # Add containers to the state
        smach.StateMachine.add('NAVIGATE', sm_nav,
                               transitions={'readyToOrient' : 'ORIENT',
                                            'moveArm' : 'GRAB_WRENCH'})

        smach.StateMachine.add('ORIENT', sm_orient,
                               transitions={'readyToGrabWrench' : 'GRAB_WRENCH'})

        smach.StateMachine.add('GRAB_WRENCH', sm_wrench,
                               transitions={'readyToOperate' : 'OPERATE_VALVE',
                                            'testingArm' : 'success',
                                            'failedToMove' : 'failure',
                                            'droppedWrench' : 'failure',
                                            'wrenchIDFailed' : 'failure'})

        smach.StateMachine.add('OPERATE_VALVE', sm_valve,
                               transitions={'valveOperated' : 'success',
                                            'failedToMove' : 'failure',
                                            'failedToStowArm' : 'failure',
                                            'valveIDFailed' : 'failure',
                                            'lostWrench' : 'failure',
                                            'valveStuck' : 'failure'})


    # Create the introspection server
    sis = smach_ros.IntrospectionServer('mbzirc_server', sm, '/CHALLENGE_TWO')
    sis.start()
    # Execute SMACH plan
    outcome = sm.execute()

    rospy.spin()
    sis.stop()


if __name__ == '__main__':
    main()
