#!/bin/bash
# Launch UR10 Kiosk Interface - Run this directly on the Elo i3 device
# Author: jsecco ®

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 UR10 WebSocket Jog Control Interface - Kiosk Mode"
echo "📱 Touch-Optimized for Elo i3"
echo "Author: jsecco ®"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're running on the local display
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "⚠️  WARNING: You appear to be connected via SSH!"
    echo ""
    echo "📱 To run the kiosk interface, please:"
    echo "   1. Go to the Elo i3 device directly"
    echo "   2. Open a terminal on the touchscreen"
    echo "   3. Run: cd $(pwd)"
    echo "   4. Run: ./launch_kiosk.sh"
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 0
    fi
fi

# Set up environment for local display
export DISPLAY=:0
export QT_QPA_PLATFORM=xcb

# Navigate to project directory
cd "$(dirname "$0")"

echo "📍 Current directory: $(pwd)"
echo ""

# Check virtual environment
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: ./install.sh"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Check display access
echo "🖥️  Checking display access..."
if command -v xset >/dev/null 2>&1; then
    if xset q >/dev/null 2>&1; then
        echo "✅ Display accessible"
    else
        echo "⚠️  Display may not be accessible"
        echo "If the application doesn't start, ensure you're running on the Elo i3 directly"
    fi
else
    echo "⚠️  xset not found, continuing anyway..."
fi

echo ""
echo "🚀 Starting UR10 Kiosk Interface..."
echo "📱 Interface will open in fullscreen mode"
echo "⚙️  Use the Settings button to configure robot IP"
echo ""
echo "Press Ctrl+C to exit"
echo ""

# Start the application
python run_local.py --fullscreen --simulate

