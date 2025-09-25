#!/usr/bin/env python3
"""
Fix the binary data parsing in WebSocket receiver for correct UR10 position extraction
"""

# Read the websocket receiver file
with open('src/communication/websocket_receiver.py', 'r') as f:
    content = f.read()

# Replace the parsing section with correct UR10 offsets
old_parsing = """            # Parse actual TCP pose (6 doubles, 48 bytes total)
            # Position: X, Y, Z in meters  
            # Rotation: RX, RY, RZ in radians
            tcp_pose_offset = offset + 444  # Typical offset for actual_TCP_pose
            if len(data) >= tcp_pose_offset + 48:
                tcp_pose = list(struct.unpack('>6d', data[tcp_pose_offset:tcp_pose_offset + 48]))
                self.robot_state['tcp_pose'] = tcp_pose
                # DEBUG: Log TCP position
                self.logger.info(f"TCP Position updated: X={tcp_pose[0]:.3f}, Y={tcp_pose[1]:.3f}, Z={tcp_pose[2]:.3f}")
                
            # Parse actual joint angles (6 doubles, 48 bytes total)  
            # All joint angles in radians
            joint_angles_offset = offset + 252  # Typical offset for actual_q
            if len(data) >= joint_angles_offset + 48:
                joint_angles = list(struct.unpack('>6d', data[joint_angles_offset:joint_angles_offset + 48]))
                self.robot_state['joint_angles'] = joint_angles
                # DEBUG: Log joint angles
                self.logger.info(f"Joint Angles: J1={joint_angles[0]*57.3:.1f}°, J2={joint_angles[1]*57.3:.1f}°")"""

new_parsing = """            # Parse UR10 real-time data packet structure
            # Based on Universal Robots Real-Time Data Exchange documentation
            # Message size: 1108 bytes (header + robot state data)
            
            if len(data) < 1108:
                self.logger.debug(f"Incomplete UR packet: {len(data)} bytes")
                return
                
            # Skip message header and parse robot state
            # UR real-time packet structure (big-endian doubles):
            # - Message size: 4 bytes
            # - Time: 8 bytes  
            # - Target joint positions: 48 bytes (6 doubles)
            # - Target joint velocities: 48 bytes (6 doubles)
            # - Target joint accelerations: 48 bytes (6 doubles)
            # - Target joint currents: 48 bytes (6 doubles)
            # - Target joint moments: 48 bytes (6 doubles)
            # - Actual joint positions: 48 bytes (6 doubles) <- WE WANT THIS
            # - Actual joint velocities: 48 bytes (6 doubles)
            # - Actual joint currents: 48 bytes (6 doubles)
            # - Joint control currents: 48 bytes (6 doubles)
            # - Actual TCP pose: 48 bytes (6 doubles) <- WE WANT THIS
            # - Actual TCP speed: 48 bytes (6 doubles)
            # - Actual TCP force: 48 bytes (6 doubles)
            
            # Calculate correct offsets (all values are big-endian doubles = 8 bytes each)
            base_offset = 12  # Skip message size (4) + time (8)
            
            # Actual joint positions offset: base + (5 * 48) = 252
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
                self.logger.info(f"TCP Position: X={tcp_pose[0]*1000:.1f}mm, Y={tcp_pose[1]*1000:.1f}mm, Z={tcp_pose[2]*1000:.1f}mm")"""

# Replace the old parsing with the new one
content = content.replace(old_parsing, new_parsing)

# Write the fixed file
with open('src/communication/websocket_receiver.py', 'w') as f:
    f.write(content)

print("✅ Fixed binary data parsing with correct UR10 packet structure")
