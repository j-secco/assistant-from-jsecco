#!/usr/bin/env python3
"""
Local launcher for UR10 WebSocket Jog Control Interface
This script runs the application directly on the Elo i3 display

Author: jsecco ®
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

# Set environment for local display
os.environ['DISPLAY'] = ':0'
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Import and run main
from main import main

if __name__ == "__main__":
    sys.exit(main())
