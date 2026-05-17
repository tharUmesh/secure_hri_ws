"""
baseline_demo.launch.py
=======================
Starts all HRI nodes with security DISABLED.
Used to demonstrate the vulnerability:
  - All traffic is plaintext
  - Any node can publish to any topic
  - The rogue_node can inject fake EMERGENCY signals
"""
import os
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, LogInfo
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        # ── Explicitly disable SROS2 for this demo ─────────────────
        SetEnvironmentVariable('ROS_SECURITY_ENABLE', 'false'),

        LogInfo(msg='\n' + '='*60 +
                '\n  BASELINE DEMO — Security DISABLED' +
                '\n  Traffic is PLAINTEXT. Rogue injection is POSSIBLE.' +
                '\n' + '='*60),

        # ── Start all five nodes without enclave arguments ──────────
        Node(
            package='hri_secure_nodes',
            executable='fusion_engine',
            name='fusion_engine_node',
            output='screen',
        ),
        Node(
            package='hri_secure_nodes',
            executable='emotion_node',
            name='emotion_node',
            output='screen',
        ),
        Node(
            package='hri_secure_nodes',
            executable='gesture_node',
            name='gesture_node',
            output='screen',
        ),
        Node(
            package='hri_secure_nodes',
            executable='motion_node',
            name='motion_node',
            output='screen',
        ),
        Node(
            package='hri_secure_nodes',
            executable='context_node',
            name='context_node',
            output='screen',
        ),
    ])