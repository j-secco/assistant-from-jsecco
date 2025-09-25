#!/usr/bin/env python3
"""
Fix script to replace main window position display with PositionDisplay widget
"""

import re

def fix_main_window():
    # Read the main window file
    with open('src/ui/main_window.py', 'r') as f:
        content = f.read()
    
    # Find the _create_center_panel method and replace it
    pattern = r'(def _create_center_panel.*?)(?=def\s|\Z)'
    
    new_center_panel = '''    def _create_center_panel(self, layout: QHBoxLayout):
        """Create the center panel with position display widget."""
        center_panel = QFrame()
        center_panel.setFrameStyle(QFrame.Shape.Box)
        center_panel.setMinimumWidth(400)
        layout.addWidget(center_panel)
        
        center_layout = QVBoxLayout(center_panel)
        
        # Use the PositionDisplay widget
        self.position_display = PositionDisplay(self.config)
        center_layout.addWidget(self.position_display)
        
        # Add some spacing
        center_layout.addStretch()
        
    '''
    
    content = re.sub(pattern, new_center_panel, content, flags=re.DOTALL)
    
    # Also need to update the position update method to use the widget
    position_update_pattern = r'def _on_position_display_update.*?(?=def\s|\Z)'
    
    new_position_update = '''    def _on_position_display_update(self, status_data):
        """Update position display widget with new data."""
        if hasattr(self, 'position_display'):
            self.position_display.update_position(status_data)
            
    '''
    
    content = re.sub(position_update_pattern, new_position_update, content, flags=re.DOTALL)
    
    # Write the fixed file
    with open('src/ui/main_window.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated main_window.py to use PositionDisplay widget")

if __name__ == "__main__":
    fix_main_window()
