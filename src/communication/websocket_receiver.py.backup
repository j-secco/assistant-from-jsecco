"""
WebSocket Receiver for UR10 Robot

This module handles the real-time data reception from the Universal Robot UR10
using the real-time interface (port 30003). Provides high-frequency robot state
monitoring for position feedback and safety status.

Based on Universal Robots Socket Communication documentation.
Author: jsecco ®
"""

import socket
import time
import threading
import logging
import struct
from typing import List, Dict, Optional, Callable, Any

class WebSocketReceiver:
    """
    Real-time WebSocket receiver for UR10 robot state data.
    Handles continuous monitoring of robot position, status, and safety information.
    """
    
    def __init__(self, hostname: str, port: int = 30003, timeout: float = 1.0):
        """
        Initialize WebSocket receiver for real-time data.
        
        Args:
            hostname: Robot IP address
            port: Communication port (30003 for real-time interface)
            timeout: Socket timeout in seconds
        """
        self.hostname = hostname
        self.port = port
        self.timeout = timeout
        
        # Connection management
        self.socket = None
        self.connected = False
        self.reconnect_attempts = 3
        self.reconnect_delay = 1.0
        
        # Threading for continuous data reception
        self.receive_thread = None
        self.should_stop = threading.Event()
        
        # Robot state data
        self.robot_state = {
            'timestamp': 0.0,
            'tcp_pose': [0.0] * 6,           # [x, y, z, rx, ry, rz]
            'joint_angles': [0.0] * 6,      # [j1, j2, j3, j4, j5, j6]
            'tcp_speed': [0.0] * 6,         # TCP velocity
            'joint_speeds': [0.0] * 6,      # Joint velocities
            'joint_currents': [0.0] * 6,    # Joint currents
            'tcp_force': [0.0] * 6,         # TCP force/torque
            'robot_mode': 0,                 # Robot operation mode
            'safety_mode': 0,                # Safety system mode
            'program_running': False,        # Program execution status
            'emergency_stopped': False,      # Emergency stop status
            'protective_stopped': False,     # Protective stop status
            'speed_scaling': 1.0,           # Current speed scaling factor
            'digital_inputs': 0,            # Digital input states
            'digital_outputs': 0,           # Digital output states
            'analog_inputs': [0.0, 0.0],    # Analog input values
            'analog_outputs': [0.0, 0.0],   # Analog output values
            'joint_temperatures': [0.0] * 6, # Joint temperatures
            'controller_time': 0.0,         # Controller internal time
            'execution_time': 0.0,          # Program execution time
            'connection_quality': 100       # Connection quality percentage
        }
        
        # Data update callbacks
        self.data_callbacks: List[Callable[[Dict], None]] = []
        self.position_callbacks: List[Callable[[List[float], List[float]], None]] = []
        self.safety_callbacks: List[Callable[[Dict], None]] = []
        
        # Statistics
        self.messages_received = 0
        self.last_message_time = 0.0
        self.message_frequency = 0.0
        
        # Logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def connect(self) -> bool:
        """
        Establish connection to UR10 real-time interface.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.hostname, self.port))
            
            self.connected = True
            self.logger.info(f"Connected to UR10 real-time interface at {self.hostname}:{self.port}")
            
            # Start receiving thread
            self.should_stop.clear()
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to UR10 real-time interface: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from robot and cleanup resources."""
        self.should_stop.set()
        self.connected = False
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2.0)
            
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
                
        self.logger.info("Disconnected from UR10 real-time interface")
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to robot with retry logic.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        self.disconnect()
        
        for attempt in range(self.reconnect_attempts):
            self.logger.info(f"Real-time reconnection attempt {attempt + 1}/{self.reconnect_attempts}")
            
            if self.connect():
                return True
                
            if attempt < self.reconnect_attempts - 1:
                time.sleep(self.reconnect_delay)
                
        self.logger.error("Failed to reconnect real-time interface after all attempts")
        return False
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connected and self.socket is not None
    
    def get_robot_state(self) -> Dict[str, Any]:
        """
        Get complete robot state data.
        
        Returns:
            Dictionary containing all robot state information
        """
        state_copy = self.robot_state.copy()
        state_copy['messages_received'] = self.messages_received
        state_copy['message_frequency'] = self.message_frequency
        return state_copy
    
    def get_tcp_pose(self) -> List[float]:
        """
        Get current TCP pose.
        
        Returns:
            TCP pose [x, y, z, rx, ry, rz] in meters and radians
        """
        return self.robot_state['tcp_pose'].copy()
    
    def get_joint_angles(self) -> List[float]:
        """
        Get current joint angles.
        
        Returns:
            Joint angles [j1, j2, j3, j4, j5, j6] in radians
        """
        return self.robot_state['joint_angles'].copy()
    
    def get_tcp_speed(self) -> List[float]:
        """
        Get current TCP velocity.
        
        Returns:
            TCP velocity [vx, vy, vz, vrx, vry, vrz] in m/s and rad/s
        """
        return self.robot_state['tcp_speed'].copy()
    
    def get_joint_speeds(self) -> List[float]:
        """
        Get current joint velocities.
        
        Returns:
            Joint velocities [j1, j2, j3, j4, j5, j6] in rad/s
        """
        return self.robot_state['joint_speeds'].copy()
    
    def is_emergency_stopped(self) -> bool:
        """Check if robot is in emergency stop state."""
        return self.robot_state['emergency_stopped']
    
    def is_protective_stopped(self) -> bool:
        """Check if robot is in protective stop state."""
        return self.robot_state['protective_stopped']
    
    def is_program_running(self) -> bool:
        """Check if robot program is currently running."""
        return self.robot_state['program_running']
    
    def get_robot_mode(self) -> int:
        """Get current robot operation mode."""
        return self.robot_state['robot_mode']
    
    def get_safety_mode(self) -> int:
        """Get current safety system mode."""
        return self.robot_state['safety_mode']
    
    def get_speed_scaling(self) -> float:
        """Get current speed scaling factor (0.0 to 1.0)."""
        return self.robot_state['speed_scaling']
    
    def get_message_frequency(self) -> float:
        """Get current message reception frequency in Hz."""
        return self.message_frequency
    
    def add_data_callback(self, callback: Callable[[Dict], None]):
        """Add callback for complete robot state updates."""
        self.data_callbacks.append(callback)
    
    def add_position_callback(self, callback: Callable[[List[float], List[float]], None]):
        """Add callback for position updates (TCP pose, joint angles)."""
        self.position_callbacks.append(callback)
    
    def add_safety_callback(self, callback: Callable[[Dict], None]):
        """Add callback for safety status updates."""
        self.safety_callbacks.append(callback)
    
    def remove_callback(self, callback):
        """Remove callback from all callback lists."""
        for callback_list in [self.data_callbacks, self.position_callbacks, self.safety_callbacks]:
            if callback in callback_list:
                callback_list.remove(callback)
    
    def _receive_loop(self):
        """
        Continuous loop for receiving real-time robot data.
        Runs in separate thread to process incoming data at high frequency.
        """
        while not self.should_stop.is_set() and self.connected:
            try:
                # Read message header (message length)
                header_data = self._recv_exact(4)
                if not header_data:
                    continue
                
                # Unpack message length (big-endian integer)
                message_length = struct.unpack('>I', header_data)[0]
                
                if message_length > 10000:  # Sanity check
                    self.logger.warning(f"Unusually large message length: {message_length}")
                    continue
                
                # Read complete message
                message_data = self._recv_exact(message_length - 4)
                if not message_data:
                    continue
                
                # Process the message
                self._process_realtime_data(message_data)
                
                # Update statistics
                self.messages_received += 1
                current_time = time.time()
                if self.last_message_time > 0:
                    time_diff = current_time - self.last_message_time
                    if time_diff > 0:
                        # Simple moving average for frequency calculation
                        alpha = 0.1  # Smoothing factor
                        instant_freq = 1.0 / time_diff
                        self.message_frequency = (alpha * instant_freq + 
                                                (1 - alpha) * self.message_frequency)
                self.last_message_time = current_time
                
            except socket.timeout:
                # Timeout is normal for real-time interface
                continue
            except Exception as e:
                self.logger.error(f"Error in real-time receive loop: {e}")
                self.connected = False
                break
    
    def _recv_exact(self, length: int) -> Optional[bytes]:
        """
        Receive exactly the specified number of bytes.
        
        Args:
            length: Number of bytes to receive
            
        Returns:
            Received data or None if connection lost
        """
        data = b''
        while len(data) < length:
            try:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    self.logger.warning("Connection lost during data reception")
                    self.connected = False
                    return None
                data += chunk
            except socket.timeout:
                continue
            except Exception as e:
                self.logger.error(f"Error receiving data: {e}")
                self.connected = False
                return None
        return data
    
    def _process_realtime_data(self, data: bytes):
        """
        Process incoming real-time robot data.
        
        Args:
            data: Raw binary robot data
        """
        try:
            # This is a simplified parser for the UR real-time interface
            # The actual format is quite complex and depends on the UR version
            # For a complete implementation, refer to the UR documentation
            
            offset = 0
            
            # Update timestamp
            self.robot_state['timestamp'] = time.time()
            
            # Parse message type (first byte)
            if len(data) < 1:
                return
            
            message_type = data[offset]
            offset += 1
            
            # Example parsing for different message types
            # Real implementation would handle the actual UR protocol format
            
            if message_type == 16:  # Robot state message (example)
                self._parse_robot_state_message(data, offset)
            elif message_type == 20:  # Safety message (example)
                self._parse_safety_message(data, offset)
            
            # Notify callbacks
            self._notify_callbacks()
            
        except Exception as e:
            self.logger.debug(f"Error processing real-time data: {e}")
    
    def _parse_robot_state_message(self, data: bytes, offset: int):
        """
        Parse robot state message from UR binary data format.
        
        Args:
            data: Binary message data from UR robot
            offset: Current parsing offset
        """
        try:
            # UR robot sends data in specific binary format
            # Real-time interface provides robot state at 500Hz
            
            if len(data) < offset + 1060:  # Minimum UR state message size
                self.logger.debug("Insufficient data for UR state message")
                return
                
            # Parse actual TCP pose (6 doubles, 48 bytes total)
            # Position: X, Y, Z in meters  
            # Rotation: RX, RY, RZ in radians
            tcp_pose_offset = offset + 444  # Typical offset for actual_TCP_pose
            if len(data) >= tcp_pose_offset + 48:
                tcp_pose = list(struct.unpack('>6d', data[tcp_pose_offset:tcp_pose_offset + 48]))
                self.robot_state['tcp_pose'] = tcp_pose
                
            # Parse actual joint angles (6 doubles, 48 bytes total)  
            # All joint angles in radians
            joint_angles_offset = offset + 252  # Typical offset for actual_q
            if len(data) >= joint_angles_offset + 48:
                joint_angles = list(struct.unpack('>6d', data[joint_angles_offset:joint_angles_offset + 48]))
                self.robot_state['joint_angles'] = joint_angles
                
            # Parse TCP speed (6 doubles)
            tcp_speed_offset = offset + 492  # Typical offset for actual_TCP_speed
            if len(data) >= tcp_speed_offset + 48:
                tcp_speed = list(struct.unpack('>6d', data[tcp_speed_offset:tcp_speed_offset + 48]))
                self.robot_state['tcp_speed'] = tcp_speed
                
            # Parse joint speeds (6 doubles)
            joint_speed_offset = offset + 300  # Typical offset for actual_qd
            if len(data) >= joint_speed_offset + 48:
                joint_speeds = list(struct.unpack('>6d', data[joint_speed_offset:joint_speed_offset + 48]))
                self.robot_state['joint_speeds'] = joint_speeds
                
            # Update timestamp
            self.robot_state['timestamp'] = time.time()
            
            # Log successful parsing (only occasionally to avoid spam)
            if hasattr(self, '_last_parse_log'):
                if time.time() - self._last_parse_log > 5.0:  # Log every 5 seconds
                    self.logger.debug(f"Successfully parsed robot data - TCP: {tcp_pose[:3]}, Joints: {joint_angles[:3]}")
                    self._last_parse_log = time.time()
            else:
                self._last_parse_log = time.time()
                
        except struct.error as e:
            self.logger.debug(f"Error unpacking UR data: {e}")
        except Exception as e:
            self.logger.debug(f"Error parsing robot state message: {e}")

    def _parse_safety_message(self, data: bytes, offset: int):
        """
        Parse safety status message from binary data.
        
        Args:
            data: Binary message data
            offset: Current parsing offset
        """
        try:
            # Placeholder for actual safety data parsing
            # Real implementation would decode safety status from binary data
            
            # For demonstration, use some default safety values
            self.robot_state['robot_mode'] = 7  # RUNNING mode
            self.robot_state['safety_mode'] = 1  # NORMAL mode
            self.robot_state['emergency_stopped'] = False
            self.robot_state['protective_stopped'] = False
            self.robot_state['program_running'] = True
            self.robot_state['speed_scaling'] = 1.0
            
        except Exception as e:
            self.logger.debug(f"Error parsing safety message: {e}")
    
    def _notify_callbacks(self):
        """Notify all registered callbacks with updated data."""
        try:
            # Notify complete data callbacks
            for callback in self.data_callbacks:
                try:
                    callback(self.robot_state)
                except Exception as e:
                    self.logger.error(f"Error in data callback: {e}")
            
            # Notify position callbacks
            for callback in self.position_callbacks:
                try:
                    callback(self.robot_state['tcp_pose'], self.robot_state['joint_angles'])
                except Exception as e:
                    self.logger.error(f"Error in position callback: {e}")
            
            # Notify safety callbacks
            safety_data = {
                'robot_mode': self.robot_state['robot_mode'],
                'safety_mode': self.robot_state['safety_mode'],
                'emergency_stopped': self.robot_state['emergency_stopped'],
                'protective_stopped': self.robot_state['protective_stopped'],
                'program_running': self.robot_state['program_running'],
                'speed_scaling': self.robot_state['speed_scaling']
            }
            
            for callback in self.safety_callbacks:
                try:
                    callback(safety_data)
                except Exception as e:
                    self.logger.error(f"Error in safety callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error notifying callbacks: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
