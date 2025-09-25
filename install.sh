#!/bin/bash
# UR10 WebSocket Jog Control Interface Installation Script
# Author: jsecco ®

set -e

echo "=========================================="
echo "UR10 WebSocket Jog Control Interface"
echo "Installation Script v1.0.0"
echo "Author: jsecco ®"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Ubuntu
if [ ! -f /etc/lsb-release ]; then
    log_warning "This script is designed for Ubuntu. Continuing anyway..."
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

log_info "Installing UR10 WebSocket Jog Control Interface..."
log_info "Project directory: $PROJECT_DIR"

# Check Python version
log_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
log_success "Found Python $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
    log_success "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
log_info "Installing Python dependencies..."
source "$PROJECT_DIR/venv/bin/activate"

pip install --upgrade pip
pip install websockets websocket-client PyQt6 pyyaml

log_success "Python dependencies installed"

# Create necessary directories
log_info "Creating application directories..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/config"

# Copy template configuration if not exists
if [ ! -f "$PROJECT_DIR/config/robot_config.yaml" ] && [ -f "$PROJECT_DIR/config/robot_config.yaml.template" ]; then
    log_info "Creating configuration file from template..."
    cp "$PROJECT_DIR/config/robot_config.yaml.template" "$PROJECT_DIR/config/robot_config.yaml"
    log_success "Configuration file created from template"
fi

# Check configuration file
if [ ! -f "$PROJECT_DIR/config/robot_config.yaml" ]; then
    log_warning "Robot configuration file not found!"
    log_info "Please edit config/robot_config.yaml with your UR10 IP address"
else
    log_success "Configuration file exists"
fi

# Make main script executable
chmod +x "$PROJECT_DIR/src/main.py"

# Create desktop launcher for GUI environments (optional)
if command -v desktop-file-install &> /dev/null; then
    log_info "Creating desktop launcher..."
    
    cat > "$PROJECT_DIR/ur10-jog-control.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=UR10 Jog Control
Comment=WebSocket-based jog control for Universal Robots UR10
Exec=/home/ur10/Documents/assistant-from-jsecco/run.sh
Icon=/home/ur10/Documents/assistant-from-jsecco/docs/icon.png
Terminal=false
Categories=Development;Engineering;
Keywords=robot;UR10;jogging;control;
DESKTOP_EOF
    
    log_success "Desktop launcher created"
fi

# Create run script
log_info "Creating run script..."
cat > "$PROJECT_DIR/run.sh" << 'RUN_EOF'
#!/bin/bash
# UR10 Jog Control Runner
# Author: jsecco ®

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Set display for GUI (if available)
export DISPLAY=${DISPLAY:-:0}

# Run the application
exec python src/main.py "$@"
RUN_EOF

chmod +x "$PROJECT_DIR/run.sh"

# Create systemd service file (optional)
log_info "Creating systemd service file..."
cat > "$PROJECT_DIR/ur10-jog-control.service" << SERVICE_EOF
[Unit]
Description=UR10 WebSocket Jog Control Interface
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/run.sh
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Display installation summary
echo ""
log_success "Installation completed successfully!"
echo ""
echo "=========================================="
echo "INSTALLATION SUMMARY"
echo "=========================================="
echo ""
log_info "📁 Project Location: $PROJECT_DIR"
log_info "🐍 Python Environment: $PROJECT_DIR/venv"
log_info "⚙️  Configuration: $PROJECT_DIR/config/robot_config.yaml"
log_info "📋 Logs Directory: $PROJECT_DIR/logs"
echo ""
echo "🔧 WebSocket Components Installed:"
echo "  ✅ WebSocketController (Primary interface - port 30001)"
echo "  ✅ WebSocketReceiver (Real-time data - port 30003)"  
echo "  ✅ DashboardClient (Robot control - port 29999)"
echo ""
echo "📱 Features Available:"
echo "  • Cartesian jogging (X, Y, Z, Rx, Ry, Rz)"
echo "  • Joint jogging (J1-J6)"
echo "  • Step and continuous modes"
echo "  • Real-time position feedback"
echo "  • Safety monitoring & emergency stop"
echo "  • Touch-optimized PyQt6 interface"
echo ""
echo "🚀 Quick Start:"
echo "  1. Edit config/robot_config.yaml with your UR10 IP"
echo "  2. Ensure UR10 is powered and network accessible"
echo "  3. Run: $PROJECT_DIR/run.sh"
echo ""
echo "🔧 Manual Run:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  python src/main.py"
echo ""
echo "📖 Documentation: $PROJECT_DIR/README.md"
echo "🐛 Logs: $PROJECT_DIR/logs/"
echo ""
log_warning "⚠️  IMPORTANT: Configure your UR10 IP address in config/robot_config.yaml"
log_warning "⚠️  SAFETY: Always ensure proper safety measures when operating the robot"
echo ""
echo "=========================================="
log_success "Ready to control your UR10 with WebSockets!"
echo "=========================================="
