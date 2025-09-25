#!/usr/bin/env python3
"""
Fix endianness and try different UR packet parsing approaches
"""

with open('src/communication/websocket_receiver.py', 'r') as f:
    content = f.read()

# Replace the parsing with corrected endianness and debugging
old_parsing = '''            # Actual joint positions offset: base + (5 * 48) = 252
            joint_positions_offset = base_offset + (5 * 48)  # Skip 5 sections of 6 doubles each
            if len(data) >= joint_positions_offset + 48:
                joint_angles = list(struct.unpack('>6d', data[joint_positions_offset:joint_positions_offset + 48]))
                self.robot_state['joint_angles'] = joint_angles
                # DEBUG: Log joint angles
                self.logger.info(f"Joint Angles: J1={joint_angles[0]*57.3:.1f}°, J2={joint_angles[1]*57.3:.1f}°, J3={joint_angles[2]*57.3:.1f}°")
            
            # Actual TCP pose offset: base + (9 * 48) = 444  
            tcp_pose_offset = base_offset + (9 * 48)  # Skip 9 sections of 6 doubles each
            if len(data) >= tcp_pose_offset + 48:
                tcp_pose = list(struct.unpack('>6d', data[tcp_pose_offset:tcp_pose_offset + 48]))
                self.robot_state['tcp_pose'] = tcp_pose
                # DEBUG: Log TCP position
                self.logger.info(f"TCP Position: X={tcp_pose[0]*1000:.1f}mm, Y={tcp_pose[1]*1000:.1f}mm, Z={tcp_pose[2]*1000:.1f}mm")'''

new_parsing = '''            # Try different parsing approaches for UR real-time data
            # Let's try multiple offset positions and endiannesses
            
            # Method 1: Try little-endian at standard UR offsets
            try:
                # Joint angles at offset 252 (little-endian)
                joint_positions_offset = 252
                if len(data) >= joint_positions_offset + 48:
                    joint_angles = list(struct.unpack('<6d', data[joint_positions_offset:joint_positions_offset + 48]))
                    # Check if values are reasonable (joint angles should be roughly -pi to +pi)
                    if all(abs(angle) < 10 for angle in joint_angles):  # 10 radians = ~570 degrees (reasonable max)
                        self.robot_state['joint_angles'] = joint_angles
                        self.logger.info(f"Joint Angles (LE): J1={joint_angles[0]*57.3:.1f}°, J2={joint_angles[1]*57.3:.1f}°, J3={joint_angles[2]*57.3:.1f}°")
                
                # TCP pose at offset 444 (little-endian)  
                tcp_pose_offset = 444
                if len(data) >= tcp_pose_offset + 48:
                    tcp_pose = list(struct.unpack('<6d', data[tcp_pose_offset:tcp_pose_offset + 48]))
                    # Check if values are reasonable (position should be roughly -5m to +5m)
                    if all(abs(pos) < 5.0 for pos in tcp_pose[:3]):  # First 3 are positions
                        self.robot_state['tcp_pose'] = tcp_pose
                        self.logger.info(f"TCP Position (LE): X={tcp_pose[0]*1000:.1f}mm, Y={tcp_pose[1]*1000:.1f}mm, Z={tcp_pose[2]*1000:.1f}mm")
            except:
                pass
                
            # Method 2: If little-endian failed, try big-endian at different offsets
            if 'joint_angles' not in self.robot_state or 'tcp_pose' not in self.robot_state:
                try:
                    # Try different offsets - maybe packet structure is different
                    for test_offset in [12, 60, 108, 156, 204, 252, 300, 348, 396, 444]:
                        if len(data) >= test_offset + 48:
                            test_joints = list(struct.unpack('>6d', data[test_offset:test_offset + 48]))
                            if all(abs(angle) < 10 for angle in test_joints):
                                self.robot_state['joint_angles'] = test_joints
                                self.logger.info(f"Joint Angles (BE@{test_offset}): J1={test_joints[0]*57.3:.1f}°")
                                break
                                
                    for test_offset in [400, 444, 500, 550, 600, 650]:
                        if len(data) >= test_offset + 48:
                            test_tcp = list(struct.unpack('>6d', data[test_offset:test_offset + 48]))
                            if all(abs(pos) < 5.0 for pos in test_tcp[:3]):
                                self.robot_state['tcp_pose'] = test_tcp
                                self.logger.info(f"TCP Position (BE@{test_offset}): X={test_tcp[0]*1000:.1f}mm")
                                break
                except:
                    pass'''

content = content.replace(old_parsing, new_parsing)

with open('src/communication/websocket_receiver.py', 'w') as f:
    f.write(content)

print("✅ Fixed endianness and added adaptive parsing")
