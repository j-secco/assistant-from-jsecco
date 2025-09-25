#!/usr/bin/env python3
"""
Apply the final fix with correct UR10 packet offsets
"""

with open('src/communication/websocket_receiver.py', 'r') as f:
    content = f.read()

# Find and replace the parsing section with correct offsets
import re

# Replace the entire parsing section
pattern = r'(def _parse_robot_state_message.*?)(\n    def _parse_safety_message|$)'

new_method = '''    def _parse_robot_state_message(self, data: bytes, offset: int):
        """
        Parse robot state message from UR binary data format.
        
        Args:
            data: Binary message data from UR robot
            offset: Current parsing offset
        """
        try:
            if len(data) < 500:  # Ensure we have enough data
                return
                
            # Based on packet analysis, the actual robot data is at specific offsets:
            # Joint angles at offset 8 (big-endian, 6 doubles)
            joint_offset = 8
            if len(data) >= joint_offset + 48:
                joint_angles = list(struct.unpack('>6d', data[joint_offset:joint_offset + 48]))
                self.robot_state['joint_angles'] = joint_angles
                self.logger.info(f"✅ Joint Angles: J1={joint_angles[0]*57.3:.1f}° J2={joint_angles[1]*57.3:.1f}° J3={joint_angles[2]*57.3:.1f}°")
            
            # TCP pose at offset 440 (big-endian, 6 doubles)
            tcp_offset = 440
            if len(data) >= tcp_offset + 48:
                tcp_pose = list(struct.unpack('>6d', data[tcp_offset:tcp_offset + 48]))
                self.robot_state['tcp_pose'] = tcp_pose
                self.logger.info(f"✅ TCP Position: X={tcp_pose[0]*1000:.1f}mm Y={tcp_pose[1]*1000:.1f}mm Z={tcp_pose[2]*1000:.1f}mm")
                
        except Exception as e:
            self.logger.debug(f"Error parsing robot state: {e}")
'''

content = re.sub(pattern, new_method + '\n    def _parse_safety_message', content, flags=re.DOTALL)

with open('src/communication/websocket_receiver.py', 'w') as f:
    f.write(content)

print("✅ Applied final fix with correct UR10 offsets!")
