"""
Jog Control Panel Widget
Touch-optimized jogging controls for UR10 robot

Author: jsecco ®
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSlider, QButtonGroup, QGroupBox,
    QComboBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont


class JogPanel(QWidget):
    """
    Jog control panel with touch-optimized buttons for Cartesian and Joint jogging.
    """
    
    # Signals
    jog_requested = pyqtSignal(str, str, float)  # axis, direction, speed
    
    def __init__(self, config: Dict[str, Any], parent: Optional[QWidget] = None):
        """
        Initialize the jog panel.
        
        Args:
            config: Application configuration dictionary
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.jog_controller = None
        
        # Jog state
        self.current_mode = "cartesian"  # cartesian or joint
        self.current_speed = 0.1
        self.is_jogging = False
        
        # UI components
        self.jog_buttons = {}
        self.speed_slider = None
        self.mode_buttons = None
        
        self._setup_ui()
        self._setup_styling()
        
    def _setup_ui(self):
        """Set up the jog panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Mode selection
        self._create_mode_selection(layout)
        
        # Speed control
        self._create_speed_control(layout)
        
        # Jog buttons
        self._create_jog_buttons(layout)
        
        # Additional controls
        self._create_additional_controls(layout)
        
    def _create_mode_selection(self, layout: QVBoxLayout):
        """Create mode selection buttons (Cartesian/Joint)."""
        mode_group = QGroupBox("Jog Mode")
        layout.addWidget(mode_group)
        
        mode_layout = QHBoxLayout(mode_group)
        
        # Mode buttons
        self.mode_buttons = QButtonGroup(self)
        
        self.cartesian_button = QPushButton("Cartesian")
        self.cartesian_button.setCheckable(True)
        self.cartesian_button.setChecked(True)
        self.cartesian_button.setMinimumHeight(100)
        self.mode_buttons.addButton(self.cartesian_button, 0)
        mode_layout.addWidget(self.cartesian_button)
        
        self.joint_button = QPushButton("Joint")
        self.joint_button.setCheckable(True)
        self.joint_button.setMinimumHeight(100)
        self.mode_buttons.addButton(self.joint_button, 1)
        mode_layout.addWidget(self.joint_button)
        
        # Connect mode change
        self.mode_buttons.buttonClicked.connect(self._on_mode_changed)
        
    def _create_speed_control(self, layout: QVBoxLayout):
        """Create speed control slider and display."""
        speed_group = QGroupBox("Jog Speed")
        layout.addWidget(speed_group)
        
        speed_layout = QVBoxLayout(speed_group)
        
        # Speed slider
        slider_layout = QHBoxLayout()
        speed_layout.addLayout(slider_layout)
        
        # Min speed label
        min_label = QLabel("0.01")
        slider_layout.addWidget(min_label)
        
        # Slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)  # 0.01 m/s
        self.speed_slider.setMaximum(50)  # 0.50 m/s
        self.speed_slider.setValue(10)  # 0.10 m/s default
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        slider_layout.addWidget(self.speed_slider)
        
        # Max speed label
        max_label = QLabel("0.50")
        slider_layout.addWidget(max_label)
        
        # Current speed display
        self.speed_label = QLabel(f"Current Speed: {self.current_speed:.2f} m/s")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        speed_layout.addWidget(self.speed_label)
        
    def _create_jog_buttons(self, layout: QVBoxLayout):
        """Create jog control buttons."""
        jog_group = QGroupBox("Jog Controls")
        layout.addWidget(jog_group)
        
        jog_layout = QVBoxLayout(jog_group)
        
        # Create button grids for both modes
        self._create_cartesian_buttons(jog_layout)
        self._create_joint_buttons(jog_layout)
        
        # Initially show cartesian buttons
        self.joint_buttons_widget.hide()
        
    def _create_cartesian_buttons(self, layout: QVBoxLayout):
        """Create Cartesian jog buttons (X, Y, Z, Rx, Ry, Rz)."""
        self.cartesian_buttons_widget = QWidget()
        layout.addWidget(self.cartesian_buttons_widget)
        
        grid_layout = QGridLayout(self.cartesian_buttons_widget)
        grid_layout.setSpacing(10)
        
        # Define button configuration
        cartesian_axes = [
            ("X", "X-axis (left/right)", 0, 0, 0, 2),
            ("Y", "Y-axis (forward/backward)", 1, 0, 1, 2),
            ("Z", "Z-axis (up/down)", 2, 0, 2, 2),
            ("Rx", "Rotation around X", 3, 0, 3, 2),
            ("Ry", "Rotation around Y", 4, 0, 4, 2), 
            ("Rz", "Rotation around Z", 5, 0, 5, 2)
        ]
        
        for axis, tooltip, row, col_neg, col_pos, span in cartesian_axes:
            # Negative direction button
            neg_button = QPushButton(f"{axis} -")
            neg_button.setFixedSize(120, 80)
            neg_button.setToolTip(f"Jog {tooltip} in negative direction")
            neg_button.pressed.connect(lambda a=axis, d="negative": self._start_jog(a, d))
            neg_button.released.connect(self._stop_jog)
            grid_layout.addWidget(neg_button, row, 0)
            
            # Axis label
            axis_label = QLabel(axis)
            axis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            axis_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            grid_layout.addWidget(axis_label, row, 1)
            
            # Positive direction button
            pos_button = QPushButton(f"{axis} +")
            pos_button.setFixedSize(120, 80)
            pos_button.setToolTip(f"Jog {tooltip} in positive direction")
            pos_button.pressed.connect(lambda a=axis, d="positive": self._start_jog(a, d))
            pos_button.released.connect(self._stop_jog)
            grid_layout.addWidget(pos_button, row, 2)
            
            # Store buttons for styling
            self.jog_buttons[f"{axis}_neg"] = neg_button
            self.jog_buttons[f"{axis}_pos"] = pos_button
            
    def _create_joint_buttons(self, layout: QVBoxLayout):
        """Create Joint jog buttons (J1-J6)."""
        self.joint_buttons_widget = QWidget()
        layout.addWidget(self.joint_buttons_widget)
        
        grid_layout = QGridLayout(self.joint_buttons_widget)
        grid_layout.setSpacing(10)
        
        # Define joint button configuration
        joints = [
            ("J1", "Base joint", 0),
            ("J2", "Shoulder joint", 1),
            ("J3", "Elbow joint", 2),
            ("J4", "Wrist 1 joint", 3),
            ("J5", "Wrist 2 joint", 4),
            ("J6", "Wrist 3 joint", 5)
        ]
        
        for joint, tooltip, row in joints:
            # Negative direction button
            neg_button = QPushButton(f"{joint} -")
            neg_button.setFixedSize(120, 80)
            neg_button.setToolTip(f"Rotate {tooltip} in negative direction")
            neg_button.pressed.connect(lambda j=joint, d="negative": self._start_jog(j, d))
            neg_button.released.connect(self._stop_jog)
            grid_layout.addWidget(neg_button, row, 0)
            
            # Joint label
            joint_label = QLabel(joint)
            joint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            joint_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            grid_layout.addWidget(joint_label, row, 1)
            
            # Positive direction button
            pos_button = QPushButton(f"{joint} +")
            pos_button.setFixedSize(120, 80)
            pos_button.setToolTip(f"Rotate {joint} in positive direction")
            pos_button.pressed.connect(lambda j=joint, d="positive": self._start_jog(j, d))
            pos_button.released.connect(self._stop_jog)
            grid_layout.addWidget(pos_button, row, 2)
            
            # Store buttons for styling
            self.jog_buttons[f"{joint}_neg"] = neg_button
            self.jog_buttons[f"{joint}_pos"] = pos_button
            
    def _create_additional_controls(self, layout: QVBoxLayout):
        """Create additional control options."""
        controls_group = QGroupBox("Options")
        layout.addWidget(controls_group)
        
        controls_layout = QVBoxLayout(controls_group)
        
        # Step mode checkbox
        self.step_mode_checkbox = QCheckBox("Step Mode")
        self.step_mode_checkbox.setToolTip("Enable step-by-step jogging instead of continuous")
        controls_layout.addWidget(self.step_mode_checkbox)
        
        # Step size control (only visible in step mode)
        step_layout = QHBoxLayout()
        controls_layout.addLayout(step_layout)
        
        step_label = QLabel("Step Size:")
        step_layout.addWidget(step_label)
        
        self.step_size_spinbox = QSpinBox()
        self.step_size_spinbox.setMinimum(1)
        self.step_size_spinbox.setMaximum(100)
        self.step_size_spinbox.setValue(10)  # 10mm or 10° default
        self.step_size_spinbox.setSuffix(" mm/°")
        self.step_size_spinbox.setEnabled(False)
        step_layout.addWidget(self.step_size_spinbox)
        
        step_layout.addStretch()
        
        # Connect step mode change
        self.step_mode_checkbox.toggled.connect(self._on_step_mode_changed)
        
    def _setup_styling(self):
        """Set up styling for jog buttons."""
        # Get colors from config
        colors = self.config.get('ui', {}).get('colors', {})
        
        # Style jog buttons
        for button in self.jog_buttons.values():
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors.get('primary', '#2196F3')};
                    border: 2px solid {colors.get('primary', '#2196F3')};
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    border-radius: 8px;
                }}
                
                QPushButton:hover {{
                    background-color: #1976D2;
                }}
                
                QPushButton:pressed {{
                    background-color: {colors.get('secondary', '#FFC107')};
                    border-color: {colors.get('secondary', '#FFC107')};
                }}
                
                QPushButton:disabled {{
                    background-color: #BDBDBD;
                    border-color: #BDBDBD;
                    color: #757575;
                }}
            """)
            
    def set_jog_controller(self, controller):
        """
        Set the jog controller for this panel.
        
        Args:
            controller: JogController instance
        """
        self.jog_controller = controller
        self.logger.info("Jog controller connected to jog panel")
        
    def _on_mode_changed(self, button: QPushButton):
        """Handle mode change (Cartesian/Joint)."""
        if button == self.cartesian_button:
            self.current_mode = "cartesian"
            self.cartesian_buttons_widget.show()
            self.joint_buttons_widget.hide()
            self.speed_label.setText(f"Current Speed: {self.current_speed:.2f} m/s")
        else:
            self.current_mode = "joint"
            self.cartesian_buttons_widget.hide()
            self.joint_buttons_widget.show()
            self.speed_label.setText(f"Current Speed: {self.current_speed:.2f} rad/s")
            
        self.logger.info(f"Jog mode changed to: {self.current_mode}")
        
    def _on_speed_changed(self, value: int):
        """Handle speed slider change."""
        self.current_speed = value / 100.0  # Convert to 0.01-0.50 range
        
        if self.current_mode == "cartesian":
            self.speed_label.setText(f"Current Speed: {self.current_speed:.2f} m/s")
        else:
            self.speed_label.setText(f"Current Speed: {self.current_speed:.2f} rad/s")
            
    def _on_step_mode_changed(self, enabled: bool):
        """Handle step mode checkbox change."""
        self.step_size_spinbox.setEnabled(enabled)
        self.logger.info(f"Step mode {'enabled' if enabled else 'disabled'}")
        
    def _start_jog(self, axis: str, direction: str):
        """
        Start jogging in the specified axis and direction.
        
        Args:
            axis: Axis to jog (X, Y, Z, Rx, Ry, Rz, J1-J6)
            direction: Direction to jog (positive/negative)
        """
        if not self.jog_controller:
            self.logger.warning("No jog controller available")
            return
            
        if self.is_jogging:
            self.logger.warning("Already jogging - ignoring new jog request")
            return
            
        try:
            self.is_jogging = True
            
            # Determine jog parameters
            speed = self.current_speed
            step_mode = self.step_mode_checkbox.isChecked()
            step_size = self.step_size_spinbox.value() / 1000.0  # Convert mm to m
            
            if step_mode:
                # Step jog
                self.jog_controller.step_jog(
                    axis=axis,
                    direction=direction,
                    step_size=step_size,
                    speed=speed,
                    mode=self.current_mode
                )
                self.is_jogging = False  # Step jog completes immediately
            else:
                # Continuous jog
                self.jog_controller.start_continuous_jog(
                    axis=axis,
                    direction=direction,
                    speed=speed,
                    mode=self.current_mode
                )
                
            self.logger.info(f"Started {'step' if step_mode else 'continuous'} jog: {axis} {direction} at {speed}")
            
        except Exception as e:
            self.logger.error(f"Error starting jog: {e}")
            self.is_jogging = False
            
    def _stop_jog(self):
        """Stop current jogging motion."""
        if not self.jog_controller or not self.is_jogging:
            return
            
        try:
            self.jog_controller.stop_jog()
            self.is_jogging = False
            self.logger.info("Stopped jogging")
            
        except Exception as e:
            self.logger.error(f"Error stopping jog: {e}")
            
    def enable_controls(self, enabled: bool):
        """
        Enable or disable all jog controls.
        
        Args:
            enabled: True to enable controls, False to disable
        """
        for button in self.jog_buttons.values():
            button.setEnabled(enabled)
            
        self.speed_slider.setEnabled(enabled)
        self.cartesian_button.setEnabled(enabled)
        self.joint_button.setEnabled(enabled)
        self.step_mode_checkbox.setEnabled(enabled)
        self.step_size_spinbox.setEnabled(enabled and self.step_mode_checkbox.isChecked())
        
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current jog settings.
        
        Returns:
            Dictionary with current jog settings
        """
        return {
            "mode": self.current_mode,
            "speed": self.current_speed,
            "step_mode": self.step_mode_checkbox.isChecked(),
            "step_size": self.step_size_spinbox.value() / 1000.0,
            "is_jogging": self.is_jogging
        }
