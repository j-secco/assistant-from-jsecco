#!/usr/bin/env python3
"""
Quick test of the working Wayland configuration.
"""

import os
import sys
from pathlib import Path

# Set up working Wayland environment
os.environ['WAYLAND_DISPLAY'] = 'wayland-0'
os.environ['XDG_SESSION_TYPE'] = 'wayland'
os.environ['XDG_RUNTIME_DIR'] = '/run/user/1000'
if 'DISPLAY' in os.environ:
    del os.environ['DISPLAY']

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt6.QtCore import QTimer
    
    print("✅ Qt imports successful with Wayland")
    
    app = QApplication.instance() or QApplication(sys.argv)
    print("✅ QApplication created")
    
    # Create a simple window
    window = QMainWindow()
    window.setWindowTitle("Wayland Test - SUCCESS!")
    window.resize(300, 100)
    window.setCentralWidget(QLabel("Wayland is working! Closing in 3 seconds..."))
    window.show()
    print("✅ Window created and shown")
    
    # Auto-close timer
    def close_app():
        print("✅ Test successful - Wayland Qt is working!")
        app.quit()
    
    timer = QTimer()
    timer.timeout.connect(close_app)
    timer.start(3000)
    
    print("🚀 Starting 3-second Qt event loop test...")
    result = app.exec()
    print(f"✅ Event loop completed with code: {result}")
    
    print("🎉 SUCCESS: Qt with Wayland is fully functional!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
