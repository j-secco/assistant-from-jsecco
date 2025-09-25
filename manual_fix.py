#!/usr/bin/env python3

# Read the current broken file
with open('src/communication/websocket_receiver.py', 'r') as f:
    lines = f.readlines()

# Find the _parse_robot_state_message method and replace it
new_lines = []
in_method = False
method_indent = 0

for line in lines:
    if 'def _parse_robot_state_message(' in line:
        in_method = True
        method_indent = len(line) - len(line.lstrip())
        # Add the new method
        new_lines.append(line)  # def line
        new_lines.append(' ' * 8 + '"""\n')
        new_lines.append(' ' * 8 + 'Parse robot state message from UR binary data format.\n')
        new_lines.append(' ' * 8 + '"""\n')
        new_lines.append(' ' * 8 + 'try:\n')
        new_lines.append(' ' * 12 + 'if len(data) < 500:\n')
        new_lines.append(' ' * 16 + 'return\n')
        new_lines.append(' ' * 12 + '\n')
        new_lines.append(' ' * 12 + '# Joint angles at offset 8 (from packet analysis)\n')
        new_lines.append(' ' * 12 + 'if len(data) >= 56:\n')
        new_lines.append(' ' * 16 + 'joint_angles = list(struct.unpack(\'>6d\', data[8:56]))\n')
        new_lines.append(' ' * 16 + 'self.robot_state[\'joint_angles\'] = joint_angles\n')
        new_lines.append(' ' * 12 + '\n')  
        new_lines.append(' ' * 12 + '# TCP pose at offset 440 (from packet analysis)\n')
        new_lines.append(' ' * 12 + 'if len(data) >= 488:\n')
        new_lines.append(' ' * 16 + 'tcp_pose = list(struct.unpack(\'>6d\', data[440:488]))\n')
        new_lines.append(' ' * 16 + 'self.robot_state[\'tcp_pose\'] = tcp_pose\n')
        new_lines.append(' ' * 12 + '\n')
        new_lines.append(' ' * 8 + 'except Exception as e:\n')
        new_lines.append(' ' * 12 + 'self.logger.debug(f"Error parsing robot state: {e}")\n')
        continue
    elif in_method:
        # Skip lines until we find the next method
        current_indent = len(line) - len(line.lstrip()) if line.strip() else 999
        if line.strip() and current_indent <= method_indent and 'def ' in line:
            in_method = False
            new_lines.append(line)
        # Skip all lines in the old method
        continue
    else:
        new_lines.append(line)

with open('src/communication/websocket_receiver.py', 'w') as f:
    f.writelines(new_lines)
    
print("✅ Manually fixed _parse_robot_state_message method")
