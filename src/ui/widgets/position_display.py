"""
Position Display Widget
Real-time robot position and joint angle display

Author: jsecco ®
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont


class PositionDisplay(QWidget):
    """
    Widget for displaying current robot position and joint angles.
    """
    
    def __init__(self, config: Dict[str, Any], parent: Optional[QWidget] = None):
        """
        Initialize the position display.
        
        Args:
            config: Application configuration dictionary
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Position data
        self.tcp_position = {"X": 0.0, "Y": 0.0, "Z": 0.0, "Rx": 0.0, "Ry": 0.0, "Rz": 0.0}
        self.joint_angles = {"J1": 0.0, "J2": 0.0, "J3": 0.0, "J4": 0.0, "J5": 0.0, "J6": 0.0}
        
        # UI components
        self.tcp_labels = {}
        self.joint_labels = {}
        
        self._setup_ui()
        self._setup_styling()
        
    def _setup_ui(self):
        """Set up the position display UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # TCP Position display
        self._create_tcp_display(layout)
        
        # Joint angles display
        self._create_joint_display(layout)
        
    def _create_tcp_display(self, layout: QVBoxLayout):
        """Create TCP position display."""
        tcp_group = QGroupBox("TCP Position")
        layout.addWidget(tcp_group)
        
        tcp_layout = QGridLayout(tcp_group)
        tcp_layout.setSpacing(10)
        
        # Position labels
        positions = [
            ("X", "mm", 0, 0), ("Y", "mm", 0, 2), ("Z", "mm", 0, 4),
            ("Rx", "°", 1, 0), ("Ry", "°", 1, 2), ("Rz", "°", 1, 4)
        ]
        
        for axis, unit, row, col in positions:
            # Axis label
            axis_label = QLabel(f"{axis}:")
            axis_label.setStyleSheet("font-weight: bold;")
            tcp_layout.addWidget(axis_label, row, col)
            
            # Value label
            value_label = QLabel("0.00")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            value_label.setStyleSheet("""
                QLabel {
                    background-color: #F5F5F5;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    padding: 5px;
                    font-family: monospace;
                    font-size: 14px;
                    min-width: 80px;
                }
            """)
            tcp_layout.addWidget(value_label, row, col + 1)
            
            # Store reference
            self.tcp_labels[axis] = value_label
            
    def _create_joint_display(self, layout: QVBoxLayout):
        """Create joint angles display."""
        joint_group = QGroupBox("Joint Angles")
        layout.addWidget(joint_group)
        
        joint_layout = QGridLayout(joint_group)
        joint_layout.setSpacing(10)
        
        # Joint labels
        joints = [
            ("J1", 0, 0), ("J2", 0, 2), ("J3", 0, 4),
            ("J4", 1, 0), ("J5", 1, 2), ("J6", 1, 4)
        ]
        
        for joint, row, col in joints:
            # Joint label
            joint_label = QLabel(f"{joint}:")
            joint_label.setStyleSheet("font-weight: bold;")
            joint_layout.addWidget(joint_label, row, col)
            
            # Angle label
            angle_label = QLabel("0.00°")
            angle_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            angle_label.setStyleSheet("""
                QLabel {
                    background-color: #F5F5F5;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    padding: 5px;
                    font-family: monospace;
                    font-size: 14px;
                    min-width: 80px;
                }
            """)
            joint_layout.addWidget(angle_label, row, col + 1)
            
            # Store reference
            self.joint_labels[joint] = angle_label
            
    def _setup_styling(self):
        """Set up widget styling."""
        colors = self.config.get('ui', {}).get('colors', {})
        
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors.get('primary', '#2196F3')};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
                color: {colors.get('primary', '#2196F3')};
            }}
        """)
        
    @pyqtSlot(dict)
    def update_position(self, position_data: Dict[str, Any]):
        """
        Update the position display with new data.
        
        Args:
            position_data: Dictionary containing position and joint angle data
        """
        try:
            # Update TCP position
            if 'tcp_pose' in position_data:
                tcp_pose = position_data['tcp_pose']
                if isinstance(tcp_pose, (list, tuple)) and len(tcp_pose) >= 6:
                    # Convert from meters to millimeters for position, radians to degrees for rotation
                    self.tcp_labels['X'].setText(f"{tcp_pose[0] * 1000:.1f}")
                    self.tcp_labels['Y'].setText(f"{tcp_pose[1] * 1000:.1f}")
                    self.tcp_labels['Z'].setText(f"{tcp_pose[2] * 1000:.1f}")
                    self.tcp_labels['Rx'].setText(f"{tcp_pose[3] * 180 / 3.14159:.1f}")
                    self.tcp_labels['Ry'].setText(f"{tcp_pose[4] * 180 / 3.14159:.1f}")
                    self.tcp_labels['Rz'].setText(f"{tcp_pose[5] * 180 / 3.14159:.1f}")
                    
            # Update joint angles
            if 'joint_angles' in position_data:
                joint_angles = position_data['joint_angles']
                if isinstance(joint_angles, (list, tuple)) and len(joint_angles) >= 6:
                    # Convert from radians to degrees
                    for i, joint in enumerate(['J1', 'J2', 'J3', 'J4', 'J5', 'J6']):
                        if i < len(joint_angles):
                            self.joint_labels[joint].setText(f"{joint_angles[i] * 180 / 3.14159:.1f}°")
                            
        except Exception as e:
            self.logger.error(f"Error updating position display: {e}")
            
    def set_connection_status(self, connected: bool):
        """
        Update display based on connection status.
        
        Args:
            connected: True if connected to robot
        """
        if not connected:
            # Show disconnected state
            for label in self.tcp_labels.values():
                label.setText("---")
                label.setStyleSheet(label.styleSheet() + "color: #BDBDBD;")
                
            for label in self.joint_labels.values():
                label.setText("---°")
                label.setStyleSheet(label.styleSheet() + "color: #BDBDBD;")
        else:
            # Restore normal styling
            for label in self.tcp_labels.values():
                label.setStyleSheet(label.styleSheet().replace("color: #BDBDBD;", ""))
                
            for label in self.joint_labels.values():
                label.setStyleSheet(label.styleSheet().replace("color: #BDBDBD;", ""))
                
    def get_current_position(self) -> Dict[str, Any]:
        """
        Get current displayed position data.
        
        Returns:
            Dictionary containing current position and joint angle data
        """
        return {
            "tcp_position": self.tcp_position.copy(),
            "joint_angles": self.joint_angles.copy()
        }
