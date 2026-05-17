"""
secure_demo.launch.py
=====================
Starts all legitimate HRI nodes with SROS2 Enforce mode active.
Each node authenticates with its X.509 certificate before
joining the DDS domain. All traffic is AES-encrypted.

Security properties demonstrated:
  - Confidentiality : AES-128-GCM encryption on all topics
  - Authentication  : X.509 mutual certificate verification
  - Integrity       : DDS-Security signed message metadata
  - Non-repudiation : SHA-256 audit log in logs/audit_*.log
  - Access control  : Only cert-holding nodes admitted
"""
import os
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, LogInfo
from launch_ros.actions import Node


# Resolve keystore path at launch time
KEYSTORE = os.path.join(os.path.expanduser('~'), 'secure_hri_ws', 'keystore')


def generate_launch_description():
    return LaunchDescription([

        # ── Activate SROS2 Enforce mode ─────────────────────────────
        SetEnvironmentVariable('ROS_SECURITY_ENABLE',               'true'),
        SetEnvironmentVariable('ROS_SECURITY_STRATEGY',             'Enforce'),
        SetEnvironmentVariable('ROS_SECURITY_KEYSTORE',             KEYSTORE),
        SetEnvironmentVariable('ROS_SECURITY_ENCLAVE_SEARCH_METHOD','MATCH'),

        LogInfo(msg='\n' + '='*60 +
                '\n  SECURE DEMO — SROS2 Enforce mode ACTIVE' +
                '\n  Keystore : ' + KEYSTORE +
                '\n  All traffic encrypted. Rogue nodes will be REJECTED.' +
                '\n' + '='*60),

        # ── Fusion Engine (subscriber) ──────────────────────────────
        Node(
            package='hri_secure_nodes',
            executable='fusion_engine',
            name='fusion_engine_node',
            ros_arguments=['--enclave', '/fusion_engine_node'],
            output='screen',
        ),

        # ── Four perception nodes (publishers) ─────────────────────
        Node(
            package='hri_secure_nodes',
            executable='emotion_node',
            name='emotion_node',
            ros_arguments=['--enclave', '/emotion_node'],
            output='screen',
        ),
        Node(
            package='hri_secure_nodes',
            executable='gesture_node',
            name='gesture_node',
            ros_arguments=['--enclave', '/gesture_node'],
            output='screen',
        ),
        Node(
            package='hri_secure_nodes',
            executable='motion_node',
            name='motion_node',
            ros_arguments=['--enclave', '/motion_node'],
            output='screen',
        ),
        Node(
            package='hri_secure_nodes',
            executable='context_node',
            name='context_node',
            ros_arguments=['--enclave', '/context_node'],
            output='screen',
        ),
    ])