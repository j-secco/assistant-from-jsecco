"""
Main Window for UR10 WebSocket Jog Control Interface
Touch-optimized PyQt6 interface for Elo i3 touchscreen devices

Author: jsecco ®
"""

import sys
import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSlider, QTabWidget, QFrame, QGroupBox,
    QProgressBar, QTextEdit, QScrollArea, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
from datetime import datetime

# Import jog controller and UI widgets
from control.jog_controller import JogController
from ui.widgets.config_dialog import ConfigDialog
from ui.widgets.position_display import PositionDisplay


class MainWindow(QMainWindow):
    """
    Main application window for UR10 jog control interface.
    Optimized for Elo i3 touchscreen with large, touch-friendly controls.
    """
    
    # Signals for UI updates
    position_updated = pyqtSignal(dict)
    safety_status_changed = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(bool, str)
    
    def __init__(self, config: Dict[str, Any], parent: Optional[QWidget] = None):
        """
        Initialize the main window.
        
        Args:
            config: Application configuration dictionary
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize jog controller
        self.jog_controller: Optional[JogController] = None
        
        # UI update timers
        self.position_timer = QTimer()
        self.status_timer = QTimer()
        
        self._setup_ui()
        self._setup_styling()
        self._setup_timers()
        self._connect_signals()
        
        self.logger.info("Main window initialized")

    def _setup_ui(self):
        """Set up the main user interface layout."""
        self.setWindowTitle(self.config.get('ui', {}).get('window', {}).get('title', 'UR10 Jog Control Interface'))
        
        # Set window properties for Elo i3
        window_config = self.config.get('ui', {}).get('window', {})
        width = window_config.get('width', 1024)
        height = window_config.get('height', 768)
        fullscreen = window_config.get('fullscreen', False)
        
        if fullscreen:
            self.showFullScreen()
        else:
            self.resize(width, height)
        
        # Central widget with scroll area for better responsiveness
        scroll_area = QScrollArea()
        self.setCentralWidget(scroll_area)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Main content widget
        main_widget = QWidget()
        scroll_area.setWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self._create_header(main_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout, 1)
        
        # Left panel - Jog controls
        self._create_left_panel(content_layout)
        
        # Center panel - Position and status
        self._create_center_panel(content_layout)
        
        # Right panel - Safety and logs
        self._create_right_panel(content_layout)
        
        # Footer - make sure it's visible
        self._create_footer(main_layout)
        
    def _create_header(self, layout: QVBoxLayout):
        """Create the header section with title and connection status."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.Box)
        header_frame.setFixedHeight(80)
        layout.addWidget(header_frame)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("UR10 WebSocket Jog Control Interface")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()

        # Settings button (only one!)
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setFixedSize(140, 50)
        self.settings_button.clicked.connect(self._open_config_dialog)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                border: 2px solid #F57C00;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
            }
            
            QPushButton:hover {
                background-color: #FB8C00;
            }
            
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """)
        header_layout.addWidget(self.settings_button)
        
        # Connection status
        self.connection_label = QLabel("Disconnected")
        self.connection_label.setFixedSize(200, 40)
        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_label.setStyleSheet("""
            QLabel {
                border: 2px solid #F44336;
                border-radius: 8px;
                background-color: #FFEBEE;
                color: #F44336;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        header_layout.addWidget(self.connection_label)
        
    def _create_left_panel(self, layout: QHBoxLayout):
        """Create the left panel with jog controls."""
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.Box)
        left_panel.setMinimumWidth(350)
        layout.addWidget(left_panel)
        
        left_layout = QVBoxLayout(left_panel)
        
        # Jog Mode Selection
        mode_group = QGroupBox("Jog Mode")
        left_layout.addWidget(mode_group)
        mode_layout = QHBoxLayout(mode_group)
        
        self.cartesian_button = QPushButton("Cartesian")
        self.cartesian_button.setCheckable(True)
        self.cartesian_button.setChecked(True)
        self.cartesian_button.setFixedHeight(50)
        self.cartesian_button.clicked.connect(lambda: self._set_jog_mode("cartesian"))
        
        self.joint_button = QPushButton("Joint")
        self.joint_button.setCheckable(True)
        self.joint_button.setFixedHeight(50)
        self.joint_button.clicked.connect(lambda: self._set_jog_mode("joint"))
        
        mode_layout.addWidget(self.cartesian_button)
        mode_layout.addWidget(self.joint_button)
        
        # Jog Speed Control
        speed_group = QGroupBox("Jog Speed")
        left_layout.addWidget(speed_group)
        speed_layout = QVBoxLayout(speed_group)
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(10)
        self.speed_slider.valueChanged.connect(self._update_speed_display)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("Current Speed: 0.10 m/s")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        speed_layout.addWidget(self.speed_label)
        
        # Jog Controls
        controls_group = QGroupBox("Jog Controls")
        left_layout.addWidget(controls_group)
        controls_layout = QGridLayout(controls_group)
        
        # Create touch-friendly jog buttons
        button_size = self.config.get('ui', {}).get('touch', {}).get('button_size', 80)
        
        # Cartesian controls
        self.jog_buttons = {}
        cartesian_labels = ['X-', 'X', 'X+', 'Y-', 'Y', 'Y+', 'Z-', 'Z', 'Z+', 
                           'Rx-', 'Rx', 'Rx+', 'Ry-', 'Ry', 'Ry+', 'Rz-', 'Rz', 'Rz+']
        
        for i, label in enumerate(cartesian_labels):
            if label.endswith('-') or label.endswith('+'):
                button = QPushButton(label)
                button.setFixedSize(button_size, button_size)
                button.pressed.connect(lambda axis=i//3, direction=-1 if label.endswith('-') else 1: 
                                      self._start_jog(axis, direction))
                button.released.connect(self._stop_jog)
                self.jog_buttons[label] = button
                controls_layout.addWidget(button, i//3, i%3)
            else:
                # Center labels
                label_widget = QLabel(label)
                label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_widget.setStyleSheet("font-weight: bold; font-size: 16px;")
                controls_layout.addWidget(label_widget, i//3, i%3)
        
        left_layout.addStretch()
        
    def _create_center_panel(self, layout: QHBoxLayout):
        """Create the center panel with position display and connection controls."""
        center_panel = QFrame()
        center_panel.setFrameStyle(QFrame.Shape.Box)
        center_panel.setMinimumWidth(400)
        layout.addWidget(center_panel)
        
        center_layout = QVBoxLayout(center_panel)
        
        # Use the PositionDisplay widget for real-time position data
        self.position_display = PositionDisplay(self.config)
        center_layout.addWidget(self.position_display)
        
        # Connect position updates signal to position display widget
        self.position_updated.connect(self.position_display.update_position)
        
        # Connection Status Section
        connection_group = QGroupBox("Connection Status")
        center_layout.addWidget(connection_group)
        connection_layout = QVBoxLayout(connection_group)
        
        # Network configuration display
        self.robot_ip_label = QLabel("Robot IP: Not Set")
        self.robot_ip_label.setStyleSheet("font-size: 14px; color: #F44336; font-weight: bold;")
        connection_layout.addWidget(self.robot_ip_label)
        
        self.connection_status_label = QLabel("Status: Disconnected")
        self.connection_status_label.setStyleSheet("font-size: 14px; color: #F44336;")
        connection_layout.addWidget(self.connection_status_label)
        
        # Connect button
        self.connect_button = QPushButton("Connect to Robot")
        self.connect_button.setFixedHeight(50)
        self.connect_button.clicked.connect(self._toggle_connection)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-size: 16px;
                font-weight: bold;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        connection_layout.addWidget(self.connect_button)
        
        # Add some spacing
        center_layout.addStretch()
        
    def _create_right_panel(self, layout: QHBoxLayout):
        """Create the right panel with safety controls and logs."""
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Shape.Box)
        right_panel.setMinimumWidth(300)
        layout.addWidget(right_panel)
        
        right_layout = QVBoxLayout(right_panel)
        
        # Emergency Control
        emergency_group = QGroupBox("Emergency Control")
        right_layout.addWidget(emergency_group)
        emergency_layout = QVBoxLayout(emergency_group)
        
        self.emergency_button = QPushButton("EMERGENCY\nSTOP")
        self.emergency_button.setFixedHeight(100)
        self.emergency_button.clicked.connect(self._emergency_stop)
        self.emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                font-size: 20px;
                font-weight: bold;
                border: 4px solid #D32F2F;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #C62828;
            }
        """)
        emergency_layout.addWidget(self.emergency_button)
        
        self.system_status_label = QLabel("System Normal")
        self.system_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.system_status_label.setStyleSheet("font-size: 16px; color: #4CAF50; font-weight: bold;")
        emergency_layout.addWidget(self.system_status_label)
        
        # Safety Status
        safety_group = QGroupBox("Safety Status")
        right_layout.addWidget(safety_group)
        safety_layout = QVBoxLayout(safety_group)
        
        self.safety_labels = {
            "Robot Mode:": QLabel("Unknown"),
            "Safety Mode:": QLabel("Unknown"),
            "Protective Stop:": QLabel("No"),
            "Remote Control:": QLabel("No")
        }
        
        for label_text, value_label in self.safety_labels.items():
            row_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            value_label.setStyleSheet("color: #757575;")
            
            row_layout.addWidget(label)
            row_layout.addWidget(value_label)
            row_layout.addStretch()
            safety_layout.addLayout(row_layout)
        
        # Robot Control
        control_group = QGroupBox("Robot Control")
        right_layout.addWidget(control_group)
        control_layout = QVBoxLayout(control_group)
        
        self.reset_button = QPushButton("Reset Safety")
        self.reset_button.setFixedHeight(40)
        self.reset_button.clicked.connect(self._reset_safety)
        control_layout.addWidget(self.reset_button)
        
        self.power_on_button = QPushButton("Power On")
        self.power_on_button.setFixedHeight(40)
        self.power_on_button.clicked.connect(self._power_on)
        control_layout.addWidget(self.power_on_button)
        
        self.power_off_button = QPushButton("Power Off")
        self.power_off_button.setFixedHeight(40)
        self.power_off_button.clicked.connect(self._power_off)
        control_layout.addWidget(self.power_off_button)
        
        # System Logs
        self._create_log_display(right_layout)
        
    def _create_footer(self, layout: QVBoxLayout):
        """Create the footer with application info and ensure it's visible."""
        footer_frame = QFrame()
        footer_frame.setFrameStyle(QFrame.Shape.Box)
        footer_frame.setFixedHeight(50)
        layout.addWidget(footer_frame)
        
        footer_layout = QHBoxLayout(footer_frame)
        
        # Author info
        author_label = QLabel("© 2024 jsecco ® - UR10 WebSocket Control v1.0.0")
        author_label.setStyleSheet("font-size: 12px; color: #757575;")
        footer_layout.addWidget(author_label)
        
        footer_layout.addStretch()
        
        # Clear logs button
        self.clear_logs_button = QPushButton("Clear Logs")
        self.clear_logs_button.setFixedSize(100, 35)
        self.clear_logs_button.clicked.connect(self._clear_logs)
        footer_layout.addWidget(self.clear_logs_button)
        
        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFixedSize(80, 35)
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        footer_layout.addWidget(self.exit_button)
        
    def _create_log_display(self, layout: QVBoxLayout):
        """Create the log display area."""
        log_group = QGroupBox("System Logs")
        layout.addWidget(log_group)
        
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Courier", 9))
        log_layout.addWidget(self.log_text)
        
    def _setup_styling(self):
        """Set up the application styling for touch interface."""
        # Get color scheme from config
        colors = self.config.get('ui', {}).get('colors', {})
        
        # Base stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors.get('background', '#FAFAFA')};
            }}
            
            QFrame {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin: 2px;
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #BDBDBD;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }}
            
            QPushButton {{
                background-color: {colors.get('primary', '#2196F3')};
                border: none;
                color: white;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-height: 35px;
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
            
            QPushButton:checked {{
                background-color: #1976D2;
                border: 2px solid #0D47A1;
            }}
            
            QSlider::groove:horizontal {{
                border: 1px solid #BDBDBD;
                height: 8px;
                background: #E0E0E0;
                margin: 2px 0;
                border-radius: 4px;
            }}
            
            QSlider::handle:horizontal {{
                background: {colors.get('primary', '#2196F3')};
                border: 1px solid #1976D2;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }}
            
            QLabel {{
                color: #212121;
                font-size: 12px;
            }}
            
            QTextEdit {{
                background-color: #FAFAFA;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 5px;
                font-family: Courier;
                font-size: 10px;
            }}
        """)
        
    def _setup_timers(self):
        """Set up update timers for UI refresh."""
        # Position update timer
        self.position_timer.timeout.connect(self._update_position)
        
        # Status update timer  
        self.status_timer.timeout.connect(self._update_status)
        
        # Start timers based on config
        feedback_config = self.config.get('ui', {}).get('feedback', {})
        position_rate = feedback_config.get('position_update_rate', 10)  # Hz
        status_rate = feedback_config.get('status_update_rate', 5)  # Hz
        
        self.position_timer.start(1000 // position_rate)  # Convert Hz to ms
        self.status_timer.start(1000 // status_rate)        
        # Keep-alive timer to ensure app stays responsive when disconnected
        self.keep_alive_timer = QTimer(self)
        self.keep_alive_timer.timeout.connect(self._keep_alive_tick)
        self.keep_alive_timer.start(5000)  # Every 5 seconds
        
    def _connect_signals(self):
        """Connect signals between UI components."""
        # Connect position updates
        
        # Connect safety status updates
        self.safety_status_changed.connect(self._on_safety_display_update)
        
        # Connect connection status updates
        self.connection_status_changed.connect(self._update_connection_display)
        
    def set_jog_controller(self, controller: JogController):
        """
        Set the jog controller for this window.
        
        Args:
            controller: JogController instance
        """
        self.jog_controller = controller
        
        # Connect controller callbacks
        controller.add_position_callback(self._on_position_update)
        controller.add_safety_callback(self._on_safety_update)
        controller.add_connection_callback(self._on_connection_update)
        
        # Update robot IP display
        robot_ip = self.config.get('robot', {}).get('ip_address', 'Not Set')
        self.robot_ip_label.setText(f"Robot IP: {robot_ip}")
        if robot_ip != 'Not Set':
            self.robot_ip_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
        
        self.logger.info("Jog controller connected to main window")
        
    # UI Event Handlers
        
    def _set_jog_mode(self, mode: str):
        """Set jogging mode and update button states."""
        if mode == "cartesian":
            self.cartesian_button.setChecked(True)
            self.joint_button.setChecked(False)
        else:
            self.cartesian_button.setChecked(False)
            self.joint_button.setChecked(True)
            
        if self.jog_controller:
            self.jog_controller.set_jog_mode(mode)
            
        self.add_log_message(f"Jog mode set to: {mode.capitalize()}", "INFO")
        
    def _update_speed_display(self, value):
        """Update speed display from slider value."""
        speed = value / 100.0  # Convert to 0.0-1.0 range
        self.speed_label.setText(f"Current Speed: {speed:.2f} m/s")
        
    def _start_jog(self, axis: int, direction: int):
        """Start jogging in specified axis and direction."""
        if self.jog_controller:
            speed_scale = self.speed_slider.value() / 100.0
            success = self.jog_controller.start_jog(axis, direction, speed_scale)
            if success:
                self.add_log_message(f"Started jog: axis={axis}, direction={direction}, speed={speed_scale:.2f}", "INFO")
            else:
                self.add_log_message("Failed to start jog operation", "ERROR")
        
    def _stop_jog(self):
        """Stop current jogging operation."""
        if self.jog_controller:
            success = self.jog_controller.stop_jog()
            if success:
                self.add_log_message("Jogging stopped", "INFO")
        
    def _toggle_connection(self):
        """Toggle robot connection."""
        if self.jog_controller:
            if self.jog_controller.is_connected():
                try:
                    self.jog_controller.disconnect()
                    self.add_log_message("Disconnected from robot", "SUCCESS")
                except Exception as e:
                    self.logger.error(f"Error during disconnect: {e}")
                    self.add_log_message(f"Disconnect error: {e}", "ERROR")
            else:
                # Check if robot IP is configured
                robot_ip = self.config.get('robot', {}).get('ip_address', '')
                if not robot_ip or robot_ip == 'Not Set':
                    self.add_log_message("Please configure robot IP address first", "ERROR")
                    self._open_config_dialog()
                    return
                
                self.add_log_message("Connecting to robot...", "INFO")
                success = self.jog_controller.connect()
                if success:
                    self.add_log_message("Connected successfully", "SUCCESS")
                else:
                    self.add_log_message("Connection failed", "ERROR")
        
    def _emergency_stop(self):
        """Execute emergency stop."""
        if self.jog_controller:
            self.jog_controller.emergency_stop()
            self.add_log_message("EMERGENCY STOP EXECUTED", "WARNING")
            self.system_status_label.setText("Emergency Stop Active")
            self.system_status_label.setStyleSheet("font-size: 16px; color: #F44336; font-weight: bold;")
        
    def _reset_safety(self):
        """Reset safety systems."""
        if self.jog_controller:
            # This would reset emergency stop if available
            self.add_log_message("Safety reset requested", "INFO")
            self.system_status_label.setText("System Normal")
            self.system_status_label.setStyleSheet("font-size: 16px; color: #4CAF50; font-weight: bold;")
        
    def _power_on(self):
        """Power on robot."""
        self.add_log_message("Robot power on requested", "INFO")
        
    def _power_off(self):
        """Power off robot."""
        self.add_log_message("Robot power off requested", "INFO")
        
    def _clear_logs(self):
        """Clear the log display."""
        self.log_text.clear()
        self.add_log_message("Logs cleared", "INFO")
        
    def _open_config_dialog(self):
        """Open configuration dialog."""
        try:
            dialog = ConfigDialog(self.config, self)
            if hasattr(dialog, 'config_saved'):
                dialog.config_saved.connect(self._on_config_saved)
            result = dialog.exec()
            
            if result == dialog.DialogCode.Accepted:
                self.add_log_message("Configuration dialog completed", "INFO")
            
        except Exception as e:
            self.logger.error(f"Error opening configuration dialog: {e}")
            self.add_log_message(f"Error opening settings: {str(e)}", "ERROR")
            # Show message box as fallback
            msg = QMessageBox(self)
            msg.setWindowTitle("Settings Error")
            msg.setText(f"Could not open settings dialog:\n{str(e)}")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
            
    def _on_config_saved(self, new_config):
        """Handle configuration save."""
        self.config = new_config
        self.add_log_message("Configuration updated - restart to apply all changes", "SUCCESS")
        
        # Update robot IP display immediately
        robot_ip = new_config.get('robot', {}).get('ip_address', 'Not Set')
        self.robot_ip_label.setText(f"Robot IP: {robot_ip}")
        if robot_ip != 'Not Set':
            self.robot_ip_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
        else:
            self.robot_ip_label.setStyleSheet("font-size: 14px; color: #F44336; font-weight: bold;")
            
        self.add_log_message(f"Robot IP updated to: {robot_ip}", "INFO")
        
    # Update Methods
    
    def _update_position(self):
        """Update position display from controller."""
        if self.jog_controller and self.jog_controller.is_connected():
            try:
                # Get current robot status
                status = self.jog_controller.get_robot_status()
                if status:
                    self.position_updated.emit(status)
            except Exception as e:
                self.logger.error(f"Error updating position: {e}")
        else:
            # Keep timer active even when disconnected - this prevents Qt event loop from idling
            # Update connection status display periodically when disconnected
            if hasattr(self, 'position_display'):
                self.position_display.set_connection_status(False)
                
    def _update_status(self):
        """Update status display from controller.""" 
        if self.jog_controller and self.jog_controller.is_connected():
            try:
                # Get current robot status
                status = self.jog_controller.get_robot_status()
                if status:
                    self.safety_status_changed.emit(status)
            except Exception as e:
                self.logger.error(f"Error updating status: {e}")
        else:
            # Keep timer active - update UI to show disconnected state
            # This ensures Qt event loop remains active
            pass  # Timer keeps running, maintaining event loop activity
                
    def _on_position_update(self, tcp_pose, joint_angles):
        self.logger.info(f"Main window received position update: TCP={tcp_pose[:3]}, Joints={joint_angles[:3]}")
        """Handle position update from controller."""
        position_data = {'tcp_pose': tcp_pose, 'joint_angles': joint_angles}
        self.position_updated.emit(position_data)
        
    def _on_safety_update(self, safety_data):
        """Handle safety status update from controller."""
        self.safety_status_changed.emit(safety_data)
        
    def _on_connection_update(self, connected: bool):
        """Handle connection status update from controller."""
        status_msg = "Connected" if connected else "Disconnected"
        self.connection_status_changed.emit(connected, status_msg)
        
        
    def _on_safety_display_update(self, status_data):
        """Update safety status display with new data."""
        try:
            # Update safety status labels
            robot_mode = status_data.get('robot_mode', 'Unknown')
            safety_mode = status_data.get('safety_mode', 'Unknown')
            protective_stopped = status_data.get('protective_stopped', False)
            emergency_stopped = status_data.get('emergency_stopped', False)
            
            self.safety_labels["Robot Mode:"].setText(str(robot_mode))
            self.safety_labels["Safety Mode:"].setText(str(safety_mode))
            self.safety_labels["Protective Stop:"].setText("Yes" if protective_stopped else "No")
            self.safety_labels["Remote Control:"].setText("Yes" if status_data.get('program_running', False) else "No")
            
            # Update system status
            if emergency_stopped:
                self.system_status_label.setText("Emergency Stop Active")
                self.system_status_label.setStyleSheet("font-size: 16px; color: #F44336; font-weight: bold;")
            elif protective_stopped:
                self.system_status_label.setText("Protective Stop")
                self.system_status_label.setStyleSheet("font-size: 16px; color: #FF9800; font-weight: bold;")
            else:
                self.system_status_label.setText("System Normal")
                self.system_status_label.setStyleSheet("font-size: 16px; color: #4CAF50; font-weight: bold;")
                
        except Exception as e:
            self.logger.error(f"Error updating safety display: {e}")
        
    def _update_connection_display(self, connected: bool, message: str):
        """Update connection status display."""
        # Update status label with appropriate styling
        if connected:
            self.connection_status_label.setText(f"Status: Connected")
            self.connection_status_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
            
            # Update connect button to show disconnect
            self.connect_button.setText("Disconnect")
            self.connect_button.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #E53935;
                }
                QPushButton:pressed {
                    background-color: #D32F2F;
                }
            """)
            
            # Update robot IP label to show it's connected
            if hasattr(self, 'robot_ip_label'):
                robot_ip = self.config.get('robot', {}).get('ip_address', 'Unknown')
                self.robot_ip_label.setText(f"Robot IP: {robot_ip}")
                self.robot_ip_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
                
            # Update position display connection status
            if hasattr(self, 'position_display'):
                self.position_display.set_connection_status(True)
                
        else:
            self.connection_status_label.setText(f"Status: {message}")
            self.connection_status_label.setStyleSheet("font-size: 14px; color: #F44336;")
            
            # Update connect button to show connect
            self.connect_button.setText("Connect to Robot")
            self.connect_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
            
            # Update robot IP label 
            if hasattr(self, 'robot_ip_label'):
                robot_ip = self.config.get('robot', {}).get('ip_address', 'Not Set')
                self.robot_ip_label.setText(f"Robot IP: {robot_ip}")
                self.robot_ip_label.setStyleSheet("font-size: 14px; color: #F44336; font-weight: bold;")
                
            # Update position display connection status
            if hasattr(self, 'position_display'):
                self.position_display.set_connection_status(False)
            
    def add_log_message(self, message: str, level: str = "INFO"):
        """
        Add a message to the log display.
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "black",
            "WARNING": "orange", 
            "ERROR": "red",
            "SUCCESS": "green"
        }
        
        color = color_map.get(level, "black")
        formatted_message = f'<span style="color: {color};">[{timestamp}] [{level}] {message}</span>'
        
        self.log_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def _keep_alive_tick(self):
        """Keep-alive tick to ensure application stays responsive."""
        # This method runs every few seconds to ensure the Qt event loop stays active
        # It's especially important when disconnected from robot
        current_time = datetime.now().strftime("%H:%M:%S")
        self.logger.debug(f"Keep-alive tick at {current_time}")
        
        # Update window title to show current status
        if self.jog_controller and self.jog_controller.is_connected():
            self.setWindowTitle("UR10 Jog Control - Connected")
        else:
            self.setWindowTitle("UR10 Jog Control - Disconnected")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Main window closing")
        
        # Stop timers safely
        try:
            self.position_timer.stop()
            self.status_timer.stop()
            if hasattr(self, 'keep_alive_timer'):
                self.keep_alive_timer.stop()
        except Exception as e:
            self.logger.error(f"Error stopping timers: {e}")
        
        # Disconnect jog controller safely
        if self.jog_controller:
            try:
                self.jog_controller.disconnect()
            except Exception as e:
                self.logger.error(f"Error disconnecting jog controller: {e}")
            
        event.accept()
        
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Emergency stop on ESC key
        if event.key() == Qt.Key.Key_Escape:
            self._emergency_stop()
                
        # Exit on Ctrl+Q
        elif event.key() == Qt.Key.Key_Q and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.close()
            
        super().keyPressEvent(event)
