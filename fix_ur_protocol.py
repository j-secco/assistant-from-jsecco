#!/usr/bin/env python3
"""
Fix the UR protocol handling to properly parse continuous real-time data
"""

with open('src/communication/websocket_receiver.py', 'r') as f:
    content = f.read()

# Replace the message type filtering with direct parsing
old_section = """            # Parse message type (first byte)
            if len(data) < 1:
                return
            
            message_type = data[offset]
            offset += 1
            
            # Example parsing for different message types
            # Real implementation would handle the actual UR protocol format
            
            if message_type == 16:  # Robot state message (example)
                self._parse_robot_state_message(data, offset)
            elif message_type == 20:  # Safety message (example)
                self._parse_safety_message(data, offset)"""

new_section = """            # UR real-time interface sends continuous robot state data
            # No message type filtering needed - all packets are robot state
            self._parse_robot_state_message(data, 0)  # Parse from beginning"""

content = content.replace(old_section, new_section)

with open('src/communication/websocket_receiver.py', 'w') as f:
    f.write(content)

print("✅ Fixed UR protocol to parse continuous real-time data directly")
