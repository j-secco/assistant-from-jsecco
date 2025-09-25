"""
Safety Panel Widget
Emergency stop and safety status display for UR10 robot

Author: jsecco ®
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont


class SafetyPanel(QWidget):
    """
    Safety control panel with emergency stop and status indicators.
    """
    
    def __init__(self, config: Dict[str, Any], parent: Optional[QWidget] = None):
        """
        Initialize the safety panel.
        
        Args:
            config: Application configuration dictionary
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.jog_controller = None
        
        # Safety state
        self.safety_status = {
            "robot_mode": "Unknown",
            "safety_mode": "Unknown",
            "emergency_stopped": False,
            "protective_stopped": False,
            "in_remote_control": False
        }
        
        # UI components
        self.emergency_button = None
        self.status_labels = {}
        
        self._setup_ui()
        self._setup_styling()
        
    def _setup_ui(self):
        """Set up the safety panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Emergency stop button
        self._create_emergency_controls(layout)
        
        # Safety status display
        self._create_status_display(layout)
        
        # Control buttons
        self._create_control_buttons(layout)
        
    def _create_emergency_controls(self, layout: QVBoxLayout):
        """Create emergency stop button."""
        emergency_group = QGroupBox("Emergency Control")
        layout.addWidget(emergency_group)
        
        emergency_layout = QVBoxLayout(emergency_group)
        
        # Large emergency stop button
        self.emergency_button = QPushButton("EMERGENCY\nSTOP")
        self.emergency_button.setFixedHeight(120)
        self.emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border: 4px solid #D32F2F;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
            }
            
            QPushButton:hover {
                background-color: #E53935;
            }
            
            QPushButton:pressed {
                background-color: #C62828;
            }
        """)
        self.emergency_button.clicked.connect(self._emergency_stop)
        emergency_layout.addWidget(self.emergency_button)
        
        # Emergency stop status
        self.emergency_status_label = QLabel("System Normal")
        self.emergency_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emergency_status_label.setStyleSheet("""
            QLabel {
                background-color: #E8F5E8;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 5px;
                font-weight: bold;
                color: #2E7D32;
            }
        """)
        emergency_layout.addWidget(self.emergency_status_label)
        
    def _create_status_display(self, layout: QVBoxLayout):
        """Create safety status indicators."""
        status_group = QGroupBox("Safety Status")
        layout.addWidget(status_group)
        
        status_layout = QVBoxLayout(status_group)
        
        # Status indicators
        status_items = [
            ("robot_mode", "Robot Mode:", "Unknown"),
            ("safety_mode", "Safety Mode:", "Unknown"),
            ("protective_stopped", "Protective Stop:", "No"),
            ("in_remote_control", "Remote Control:", "No")
        ]
        
        for key, label_text, default_value in status_items:
            status_row = QHBoxLayout()
            status_layout.addLayout(status_row)
            
            # Label
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            status_row.addWidget(label)
            
            # Status value
            value_label = QLabel(default_value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            value_label.setStyleSheet("""
                QLabel {
                    background-color: #F5F5F5;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    padding: 3px 8px;
                    min-width: 100px;
                }
            """)
            status_row.addWidget(value_label)
            
            # Store reference
            self.status_labels[key] = value_label
            
    def _create_control_buttons(self, layout: QVBoxLayout):
        """Create safety control buttons."""
        control_group = QGroupBox("Robot Control")
        layout.addWidget(control_group)
        
        control_layout = QVBoxLayout(control_group)
        
        # Reset button
        self.reset_button = QPushButton("Reset Safety")
        self.reset_button.setFixedHeight(70)
        self.reset_button.clicked.connect(self._reset_safety)
        control_layout.addWidget(self.reset_button)
        
        # Power control buttons
        power_layout = QHBoxLayout()
        control_layout.addLayout(power_layout)
        
        self.power_on_button = QPushButton("Power On")
        self.power_on_button.setFixedHeight(65)
        self.power_on_button.clicked.connect(self._power_on)
        power_layout.addWidget(self.power_on_button)
        
        self.power_off_button = QPushButton("Power Off")
        self.power_off_button.setFixedHeight(65)
        self.power_off_button.clicked.connect(self._power_off)
        power_layout.addWidget(self.power_off_button)
        
        # Brake release button
        self.brake_release_button = QPushButton("Release Brakes")
        self.brake_release_button.setFixedHeight(65)
        self.brake_release_button.clicked.connect(self._release_brakes)
        control_layout.addWidget(self.brake_release_button)
        
        # Connect/disconnect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedHeight(70)
        self.connect_button.clicked.connect(self._toggle_connection)
        control_layout.addWidget(self.connect_button)
        
    def _setup_styling(self):
        """Set up widget styling."""
        colors = self.config.get('ui', {}).get('colors', {})
        
        # Style control buttons
        button_style = f"""
            QPushButton {{
                background-color: {colors.get('primary', '#2196F3')};
                border: none;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            
            QPushButton:pressed {{
                background-color: #0D47A1;
            }}
            
            QPushButton:disabled {{
                background-color: #BDBDBD;
                color: #757575;
            }}
        """
        
        for button in [self.reset_button, self.power_on_button, self.power_off_button, 
                      self.brake_release_button, self.connect_button]:
            if button:
                button.setStyleSheet(button_style)
                
    def set_jog_controller(self, controller):
        """
        Set the jog controller for this panel.
        
        Args:
            controller: JogController instance
        """
        self.jog_controller = controller
        self.logger.info("Jog controller connected to safety panel")
        
    @pyqtSlot(dict)
    def update_safety_status(self, safety_data: Dict[str, Any]):
        """
        Update safety status display.
        
        Args:
            safety_data: Dictionary containing safety status information
        """
        try:
            # Update safety status
            if 'robot_mode' in safety_data:
                self.status_labels['robot_mode'].setText(str(safety_data['robot_mode']))
                
            if 'safety_mode' in safety_data:
                self.status_labels['safety_mode'].setText(str(safety_data['safety_mode']))
                
            if 'protective_stopped' in safety_data:
                status = "Yes" if safety_data['protective_stopped'] else "No"
                self.status_labels['protective_stopped'].setText(status)
                
                # Update styling based on protective stop status
                if safety_data['protective_stopped']:
                    self.status_labels['protective_stopped'].setStyleSheet("""
                        QLabel {
                            background-color: #FFEBEE;
                            border: 1px solid #F44336;
                            border-radius: 4px;
                            padding: 3px 8px;
                            min-width: 100px;
                            color: #C62828;
                            font-weight: bold;
                        }
                    """)
                else:
                    self.status_labels['protective_stopped'].setStyleSheet("""
                        QLabel {
                            background-color: #F5F5F5;
                            border: 1px solid #BDBDBD;
                            border-radius: 4px;
                            padding: 3px 8px;
                            min-width: 100px;
                        }
                    """)
                    
            if 'in_remote_control' in safety_data:
                status = "Yes" if safety_data['in_remote_control'] else "No"
                self.status_labels['in_remote_control'].setText(status)
                
            if 'emergency_stopped' in safety_data:
                self._update_emergency_status(safety_data['emergency_stopped'])
                
            # Update stored status
            self.safety_status.update(safety_data)
            
        except Exception as e:
            self.logger.error(f"Error updating safety status: {e}")
            
    def _update_emergency_status(self, emergency_stopped: bool):
        """Update emergency stop status display."""
        if emergency_stopped:
            self.emergency_status_label.setText("EMERGENCY STOP ACTIVE")
            self.emergency_status_label.setStyleSheet("""
                QLabel {
                    background-color: #FFEBEE;
                    border: 2px solid #F44336;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                    color: #C62828;
                }
            """)
        else:
            self.emergency_status_label.setText("System Normal")
            self.emergency_status_label.setStyleSheet("""
                QLabel {
                    background-color: #E8F5E8;
                    border: 2px solid #4CAF50;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                    color: #2E7D32;
                }
            """)
            
    def _emergency_stop(self):
        """Handle emergency stop button press."""
        if not self.jog_controller:
            self.logger.warning("No jog controller available for emergency stop")
            return
            
        try:
            self.jog_controller.emergency_stop()
            self.logger.warning("Emergency stop activated by user")
            
            # Update UI immediately
            self._update_emergency_status(True)
            
        except Exception as e:
            self.logger.error(f"Error triggering emergency stop: {e}")
            
    def _reset_safety(self):
        """Handle safety reset button press."""
        if not self.jog_controller:
            self.logger.warning("No jog controller available for safety reset")
            return
            
        try:
            self.jog_controller.reset_safety()
            self.logger.info("Safety reset requested by user")
            
        except Exception as e:
            self.logger.error(f"Error resetting safety: {e}")
            
    def _power_on(self):
        """Handle power on button press."""
        if not self.jog_controller:
            self.logger.warning("No jog controller available for power on")
            return
            
        try:
            self.jog_controller.power_on_robot()
            self.logger.info("Robot power on requested by user")
            
        except Exception as e:
            self.logger.error(f"Error powering on robot: {e}")
            
    def _power_off(self):
        """Handle power off button press."""
        if not self.jog_controller:
            self.logger.warning("No jog controller available for power off")
            return
            
        try:
            self.jog_controller.power_off_robot()
            self.logger.info("Robot power off requested by user")
            
        except Exception as e:
            self.logger.error(f"Error powering off robot: {e}")
            
    def _release_brakes(self):
        """Handle brake release button press."""
        if not self.jog_controller:
            self.logger.warning("No jog controller available for brake release")
            return
            
        try:
            self.jog_controller.release_brakes()
            self.logger.info("Brake release requested by user")
            
        except Exception as e:
            self.logger.error(f"Error releasing brakes: {e}")
            
    def _toggle_connection(self):
        """Handle connect/disconnect button press."""
        if not self.jog_controller:
            self.logger.warning("No jog controller available")
            return
            
        try:
            if self.jog_controller.is_connected():
                self.jog_controller.disconnect_all()
                self.connect_button.setText("Connect")
                self.logger.info("Disconnected from robot")
            else:
                self.jog_controller.connect_all()
                self.connect_button.setText("Disconnect")
                self.logger.info("Connecting to robot...")
                
        except Exception as e:
            self.logger.error(f"Error toggling connection: {e}")
            
    def update_connection_status(self, connected: bool):
        """
        Update UI based on connection status.
        
        Args:
            connected: True if connected to robot
        """
        if connected:
            self.connect_button.setText("Disconnect")
            # Enable control buttons
            for button in [self.power_on_button, self.power_off_button, 
                          self.brake_release_button, self.reset_button]:
                button.setEnabled(True)
        else:
            self.connect_button.setText("Connect")
            # Disable control buttons
            for button in [self.power_on_button, self.power_off_button, 
                          self.brake_release_button, self.reset_button]:
                button.setEnabled(False)
                
            # Reset status displays
            for label in self.status_labels.values():
                label.setText("Unknown")
                
    def get_safety_status(self) -> Dict[str, Any]:
        """
        Get current safety status.
        
        Returns:
            Dictionary with current safety status
        """
        return self.safety_status.copy()
