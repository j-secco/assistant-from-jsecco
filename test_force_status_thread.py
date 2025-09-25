#!/usr/bin/env python3
"""
Test script that forces status thread to start even when robot connection fails

Author: jsecco ®
"""

import sys
import time
import signal
import logging
import threading
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ui.main_window import MainWindow
from control.jog_controller import JogController

# Configure logging to see debug messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\nShutting down test...')
    QApplication.quit()

def test_forced_status_thread():
    """Test UI position updates by forcing status thread to run"""
    print("Testing Forced Status Thread Position Updates")
    print("=" * 50)
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    try:
        # Create basic config
        config = {
            'ui': {
                'window': {'title': 'Test Forced Status Thread', 'width': 800, 'height': 600},
                'feedback': {'position_update_rate': 10, 'status_update_rate': 5}
            },
            'robot': {'ip_address': '192.168.10.24'}
        }
        
        # Create main window
        main_window = MainWindow(config)
        
        # Create jog controller
        jog_controller = JogController("192.168.10.24")
        
        # Connect jog controller to main window
        main_window.set_jog_controller(jog_controller)
        
        print("UI and controller created")
        
        # Try normal connection (will fail)
        connected = jog_controller.connect()
        print(f"Normal connection result: {connected}")
        
        if not connected:
            print("Connection failed as expected. Manually starting status thread for testing...")
            
            # Force start the status thread manually
            jog_controller.should_stop.clear()
            jog_controller.status_thread = threading.Thread(target=jog_controller._status_loop, daemon=True)
            jog_controller.status_thread.start()
            jog_controller.connected = True  # Fake connection status for position simulation
            
            print("Status thread manually started")
            
            # Show the window 
            main_window.show()
            print("Window shown")
            
            # Set up timer to quit after 10 seconds
            quit_timer = QTimer()
            quit_timer.timeout.connect(lambda: (print("Test complete"), QApplication.quit()))
            quit_timer.setSingleShot(True)
            quit_timer.start(10000)  # 10 seconds
            
            print("Running for 10 seconds to observe position updates...")
            
            # Run the Qt event loop
            app.exec()
            
        # Clean up
        jog_controller.disconnect()
        print("Controller disconnected")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_forced_status_thread()
