#!/bin/bash
# Simple script to run UR10 application from desktop environment
# This should be run directly from the Elo i3 desktop, not via SSH
# Author: jsecco ®

echo "🤖 UR10 Jog Control - Starting from Desktop"
echo "==========================================="

# Change to application directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Show current environment
echo "🖥️  Display environment:"
echo "   DISPLAY: ${DISPLAY:-Not set}"
echo "   WAYLAND_DISPLAY: ${WAYLAND_DISPLAY:-Not set}"
echo "   XDG_SESSION_TYPE: ${XDG_SESSION_TYPE:-Not set}"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found"
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
echo "🎯 Connecting to real robot at 192.168.10.24"
echo "⚠️  This will control the physical UR10 robot"
echo ""

# Run the application with proper error handling
echo "🚀 Starting UR10 application..."
python src/main.py "$@"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ Application exited normally"
else
    echo "❌ Application exited with error code: $exit_code"
    echo "📋 Check the logs for more information:"
    echo "   Session log: logs/commandline_session_$(date +%Y%m%d)_*.log"
    echo "   Error log: logs/commandline_errors_$(date +%Y%m%d)_*.log"
fi

exit $exit_code
