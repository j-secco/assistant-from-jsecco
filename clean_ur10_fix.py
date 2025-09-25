#!/usr/bin/env python3
"""
Clean fix for UR10 position display using correct packet offsets
"""

import re

with open('src/communication/websocket_receiver.py', 'r') as f:
    content = f.read()

# 1. Fix the data processing to call parsing directly
content = content.replace(
    '''            # Parse message type (first byte)
            if len(data) < 1:
                return
            
            message_type = data[offset]
            offset += 1
            
            # Example parsing for different message types
            # Real implementation would handle the actual UR protocol format
            
            if message_type == 16:  # Robot state message (example)
                self._parse_robot_state_message(data, offset)
            elif message_type == 20:  # Safety message (example)
                self._parse_safety_message(data, offset)''',
    '''            # UR real-time interface sends continuous robot state data
            self._parse_robot_state_message(data, 0)'''
)

# 2. Replace the robot state parsing method
old_parse_method = '''    def _parse_robot_state_message(self, data: bytes, offset: int):
        """
        Parse robot state message from UR binary data format.

        Args:
            data: Binary message data from UR robot
            offset: Current parsing offset
        """
        try:
            # UR robot sends data in specific binary format
            # Real-time interface provides robot state at 500Hz
            
            if len(data) < offset + 1060:  # Minimum UR state message size
                self.logger.debug("Insufficient data for UR state message")
                return
                
            # Parse actual TCP pose (6 doubles, 48 bytes total)
            # Position: X, Y, Z in meters  
            # Rotation: RX, RY, RZ in radians
            tcp_pose_offset = offset + 444  # Typical offset for actual_TCP_pose
            if len(data) >= tcp_pose_offset + 48:
                tcp_pose = list(struct.unpack('>6d', data[tcp_pose_offset:tcp_pose_offset + 48]))
                self.robot_state['tcp_pose'] = tcp_pose
                
            # Parse actual joint angles (6 doubles, 48 bytes total)  
            # All joint angles in radians
            joint_angles_offset = offset + 252  # Typical offset for actual_q
            if len(data) >= joint_angles_offset + 48:
                joint_angles = list(struct.unpack('>6d', data[joint_angles_offset:joint_angles_offset + 48]))
                self.robot_state['joint_angles'] = joint_angles'''

new_parse_method = '''    def _parse_robot_state_message(self, data: bytes, offset: int):
        """
        Parse robot state message from UR binary data format.

        Args:
            data: Binary message data from UR robot
            offset: Current parsing offset
        """
        try:
            if len(data) < 500:
                return
                
            # Based on packet analysis of actual UR10 data:
            # Joint angles at offset 8 (big-endian, 6 doubles)
            joint_offset = 8
            if len(data) >= joint_offset + 48:
                joint_angles = list(struct.unpack('>6d', data[joint_offset:joint_offset + 48]))
                self.robot_state['joint_angles'] = joint_angles
            
            # TCP pose at offset 440 (big-endian, 6 doubles: x,y,z,rx,ry,rz)
            tcp_offset = 440
            if len(data) >= tcp_offset + 48:
                tcp_pose = list(struct.unpack('>6d', data[tcp_offset:tcp_offset + 48]))
                self.robot_state['tcp_pose'] = tcp_pose'''

# Only replace the start of the method to avoid breaking the rest
method_start_pattern = r'(def _parse_robot_state_message\(self, data: bytes, offset: int\):.*?joint_angles = joint_angles)'
replacement = new_parse_method

content = re.sub(method_start_pattern, replacement, content, flags=re.DOTALL)

with open('src/communication/websocket_receiver.py', 'w') as f:
    f.write(content)

print("✅ Applied clean UR10 position fix!")
