#!/bin/bash
# Run UR10 application using Wayland (WORKING CONFIGURATION)
# Author: jsecco ®

echo "🤖 UR10 Jog Control - Wayland Mode"
echo "=================================="

# Change to application directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up WORKING Wayland environment (confirmed working from tests)
export WAYLAND_DISPLAY=wayland-0
export XDG_SESSION_TYPE=wayland
export XDG_RUNTIME_DIR=/run/user/1000
# Unset DISPLAY to prevent X11 conflicts
unset DISPLAY

echo "🌊 Using Wayland display configuration:"
echo "   WAYLAND_DISPLAY=wayland-0"
echo "   XDG_SESSION_TYPE=wayland"
echo "   XDG_RUNTIME_DIR=/run/user/1000"
echo "   DISPLAY=unset"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Verify no simulation
echo "🔍 Verifying real robot configuration..."
if python verify_no_simulation.py >/dev/null 2>&1; then
    echo "✅ Configuration verified - REAL ROBOT MODE"
else
    echo "❌ Configuration verification failed!"
    python verify_no_simulation.py
    exit 1
fi

echo ""
echo "🎯 Robot IP: 192.168.10.24 (REAL ROBOT)"
echo "🌊 Display: Wayland (confirmed working)"
echo "⚠️  This will control the physical UR10 robot"
echo ""

# Run the application
echo "🚀 Starting UR10 application..."
python src/main.py "$@"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ Application exited normally"
else
    echo "❌ Application exited with code: $exit_code"
    echo "📋 Check logs: ./view_commandline_logs.sh"
fi

exit $exit_code
