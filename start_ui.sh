#!/bin/bash
# Start UR10 Jog Control Interface on local display
# Author: jsecco ®

echo "Starting UR10 Jog Control Interface on Elo i3..."
echo "Please ensure you are running this directly on the Elo i3 device, not via SSH"

# Check if we're in an SSH session
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "WARNING: You appear to be in an SSH session!"
    echo "This application needs to run directly on the Elo i3 device to display the GUI."
    echo ""
    echo "Please:"
    echo "1. Go to the Elo i3 device directly"
    echo "2. Open a terminal"
    echo "3. Navigate to: $(pwd)"
    echo "4. Run: ./start_ui.sh"
    echo ""
    echo "Alternatively, you can test in simulation mode by running:"
    echo "source venv/bin/activate && python run_local.py --simulate --debug"
    exit 1
fi

# Check display
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
fi

# Activate virtual environment
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment not found. Please run ./install.sh first"
    exit 1
fi

source venv/bin/activate

# Set Qt platform
export QT_QPA_PLATFORM=xcb

# Check if we can connect to the display
if ! xhost > /dev/null 2>&1; then
    echo "Error: Cannot connect to display. Make sure you're running this on the Elo i3 device directly."
    exit 1
fi

echo "Starting application..."
python run_local.py "$@"
