"""
Status Panel Widget
System status and information display

Author: jsecco ®
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QGroupBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont


class StatusPanel(QWidget):
    """
    Status panel for displaying system information and connection status.
    """
    
    def __init__(self, config: Dict[str, Any], parent: Optional[QWidget] = None):
        """
        Initialize the status panel.
        
        Args:
            config: Application configuration dictionary
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Status data
        self.system_status = {
            "robot_connected": False,
            "websocket_primary": False,
            "websocket_realtime": False,
            "dashboard_connected": False,
            "last_update": "Never",
            "message_count": 0
        }
        
        # UI components
        self.status_labels = {}
        self.connection_indicators = {}
        
        self._setup_ui()
        self._setup_styling()
        
    def _setup_ui(self):
        """Set up the status panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Connection status
        self._create_connection_status(layout)
        
        # System information
        self._create_system_info(layout)
        
    def _create_connection_status(self, layout: QVBoxLayout):
        """Create connection status indicators."""
        conn_group = QGroupBox("Connection Status")
        layout.addWidget(conn_group)
        
        conn_layout = QVBoxLayout(conn_group)
        
        # Connection indicators
        connections = [
            ("websocket_primary", "Primary WebSocket (30001)"),
            ("websocket_realtime", "Real-time Data (30003)"),
            ("dashboard_connected", "Dashboard Client (29999)")
        ]
        
        for key, label_text in connections:
            conn_row = QHBoxLayout()
            conn_layout.addLayout(conn_row)
            
            # Label
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            conn_row.addWidget(label)
            
            # Status indicator
            status_indicator = QLabel("●")
            status_indicator.setAlignment(Qt.AlignmentFlag.AlignRight)
            status_indicator.setStyleSheet("""
                QLabel {
                    color: #F44336;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            conn_row.addWidget(status_indicator)
            
            # Store reference
            self.connection_indicators[key] = status_indicator
            
    def _create_system_info(self, layout: QVBoxLayout):
        """Create system information display."""
        info_group = QGroupBox("System Information")
        layout.addWidget(info_group)
        
        info_layout = QVBoxLayout(info_group)
        
        # Information items
        info_items = [
            ("last_update", "Last Update:", "Never"),
            ("message_count", "Messages:", "0"),
            ("robot_ip", "Robot IP:", self.config.get('robot', {}).get('ip_address', 'Not Set'))
        ]
        
        for key, label_text, default_value in info_items:
            info_row = QHBoxLayout()
            info_layout.addLayout(info_row)
            
            # Label
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            info_row.addWidget(label)
            
            # Value
            value_label = QLabel(default_value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            value_label.setStyleSheet("""
                QLabel {
                    background-color: #F5F5F5;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-family: monospace;
                    min-width: 120px;
                }
            """)
            info_row.addWidget(value_label)
            
            # Store reference
            self.status_labels[key] = value_label
            
        # Communication health bar
        health_layout = QVBoxLayout()
        info_layout.addLayout(health_layout)
        
        health_label = QLabel("Communication Health:")
        health_label.setStyleSheet("font-weight: bold;")
        health_layout.addWidget(health_label)
        
        self.health_bar = QProgressBar()
        self.health_bar.setMinimum(0)
        self.health_bar.setMaximum(100)
        self.health_bar.setValue(0)
        self.health_bar.setTextVisible(True)
        health_layout.addWidget(self.health_bar)
        
    def _setup_styling(self):
        """Set up widget styling."""
        colors = self.config.get('ui', {}).get('colors', {})
        
        # Style progress bar
        self.health_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }}
            
            QProgressBar::chunk {{
                background-color: {colors.get('success', '#4CAF50')};
                border-radius: 4px;
            }}
        """)
        
    @pyqtSlot(dict)
    def update_status(self, status_data: Dict[str, Any]):
        """
        Update status display with new data.
        
        Args:
            status_data: Dictionary containing status information
        """
        try:
            # Update connection status
            for key, indicator in self.connection_indicators.items():
                if key in status_data:
                    connected = status_data[key]
                    if connected:
                        indicator.setStyleSheet("""
                            QLabel {
                                color: #4CAF50;
                                font-size: 16px;
                                font-weight: bold;
                            }
                        """)
                    else:
                        indicator.setStyleSheet("""
                            QLabel {
                                color: #F44336;
                                font-size: 16px;
                                font-weight: bold;
                            }
                        """)
                        
            # Update system information
            if 'last_update' in status_data:
                self.status_labels['last_update'].setText(str(status_data['last_update']))
                
            if 'message_count' in status_data:
                self.status_labels['message_count'].setText(str(status_data['message_count']))
                
            # Update communication health
            if 'communication_health' in status_data:
                health_value = int(status_data['communication_health'])
                self.health_bar.setValue(health_value)
                
                # Update health bar color based on value
                if health_value >= 80:
                    color = "#4CAF50"  # Green
                elif health_value >= 60:
                    color = "#FF9800"  # Orange
                else:
                    color = "#F44336"  # Red
                    
                self.health_bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 2px solid #BDBDBD;
                        border-radius: 6px;
                        text-align: center;
                        font-weight: bold;
                    }}
                    
                    QProgressBar::chunk {{
                        background-color: {color};
                        border-radius: 4px;
                    }}
                """)
                
            # Update stored status
            self.system_status.update(status_data)
            
        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")
            
    def update_connection_indicators(self, primary: bool, realtime: bool, dashboard: bool):
        """
        Update connection indicators.
        
        Args:
            primary: Primary WebSocket connection status
            realtime: Real-time WebSocket connection status  
            dashboard: Dashboard client connection status
        """
        connections = {
            'websocket_primary': primary,
            'websocket_realtime': realtime,
            'dashboard_connected': dashboard
        }
        
        for key, connected in connections.items():
            indicator = self.connection_indicators.get(key)
            if indicator:
                if connected:
                    indicator.setStyleSheet("""
                        QLabel {
                            color: #4CAF50;
                            font-size: 16px;
                            font-weight: bold;
                        }
                    """)
                else:
                    indicator.setStyleSheet("""
                        QLabel {
                            color: #F44336;
                            font-size: 16px;
                            font-weight: bold;
                        }
                    """)
                    
        # Update overall health based on connections
        connected_count = sum([primary, realtime, dashboard])
        health_percentage = int((connected_count / 3.0) * 100)
        self.health_bar.setValue(health_percentage)
        
    def increment_message_count(self):
        """Increment the message counter."""
        try:
            current_count = int(self.status_labels['message_count'].text())
            new_count = current_count + 1
            self.status_labels['message_count'].setText(str(new_count))
            self.system_status['message_count'] = new_count
        except ValueError:
            self.status_labels['message_count'].setText("1")
            self.system_status['message_count'] = 1
            
    def update_last_update_time(self, timestamp: str):
        """
        Update the last update timestamp.
        
        Args:
            timestamp: Formatted timestamp string
        """
        self.status_labels['last_update'].setText(timestamp)
        self.system_status['last_update'] = timestamp
        
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            Dictionary with current system status
        """
        return self.system_status.copy()
