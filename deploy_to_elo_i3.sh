#!/bin/bash
# Deploy and run UR10 Jog Control Interface on Elo i3 local display
# Author: jsecco ®

echo "🚀 Deploying UR10 Jog Control Interface to Elo i3..."
echo ""

# Set environment variables for local display
export DISPLAY=:0.0
export QT_QPA_PLATFORM=xcb

# Check if we can access the display
if xset q &>/dev/null; then
    echo "✅ Display :0 is accessible"
else
    echo "❌ Cannot access display :0"
    echo "Please run this script directly on the Elo i3 device, not via SSH"
    exit 1
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run ./install.sh first"
    exit 1
fi

# Check if all modules are available
echo "🔧 Checking application modules..."
python -c "
import sys
sys.path.insert(0, 'src')
from main import main
from ui.main_window import MainWindow
from ui.widgets.config_dialog import ConfigDialog
print('✅ All modules loaded successfully')
"

if [ $? -ne 0 ]; then
    echo "❌ Module import failed"
    exit 1
fi

echo ""
echo "🎉 Starting UR10 Jog Control Interface on Elo i3..."
echo "📱 The interface will open in fullscreen kiosk mode"
echo "⚙️  Click the Settings button to configure your robot IP"
echo ""

# Run the application in fullscreen mode
python run_local.py --fullscreen --simulate --debug

