#!/usr/bin/env python3

# Read the file
with open('src/ui/main_window.py', 'r') as f:
    lines = f.readlines()

# Find the _create_center_panel method
start_line = None
end_line = None
for i, line in enumerate(lines):
    if '_create_center_panel(self, layout: QHBoxLayout):' in line:
        start_line = i
    elif start_line is not None and line.strip().startswith('def ') and 'create_center_panel' not in line:
        end_line = i
        break

if start_line and end_line:
    # Replace the method with our simplified version
    new_method = [
        '    def _create_center_panel(self, layout: QHBoxLayout):\n',
        '        """Create the center panel with position display widget."""\n',
        '        center_panel = QFrame()\n',
        '        center_panel.setFrameStyle(QFrame.Shape.Box)\n',
        '        center_panel.setMinimumWidth(400)\n',
        '        layout.addWidget(center_panel)\n',
        '        \n',
        '        center_layout = QVBoxLayout(center_panel)\n',
        '        \n',
        '        # Use the PositionDisplay widget\n',
        '        self.position_display = PositionDisplay(self.config)\n',
        '        center_layout.addWidget(self.position_display)\n',
        '        \n',
        '        # Connect position updates signal to position display widget\n',
        '        self.position_updated.connect(self.position_display.update_position)\n',
        '        \n',
        '        # Add some spacing\n',
        '        center_layout.addStretch()\n',
        '        \n',
    ]
    
    # Replace the lines
    new_lines = lines[:start_line] + new_method + lines[end_line:]
    
    # Write back
    with open('src/ui/main_window.py', 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Replaced _create_center_panel method (lines {start_line+1}-{end_line})")
else:
    print("❌ Could not find _create_center_panel method boundaries")
