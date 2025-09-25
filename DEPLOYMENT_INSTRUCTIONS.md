# UR10 WebSocket Jog Control Interface - Deployment on Elo i3

## 🚀 Quick Start Guide

### Step 1: Installation (Already Complete)
The application has been installed to `/home/ur10/Documents/assistant-from-jsecco/`

### Step 2: Configuration
1. **Edit the robot configuration:**
   ```bash
   nano config/robot_config.yaml
   ```
   
2. **Set your UR10's IP address:**
   ```yaml
   robot:
     ip_address: "YOUR_UR10_IP_HERE"  # Replace with actual IP
   ```

### Step 3: Running the Application

⚠️ **IMPORTANT**: The GUI application must be run directly on the Elo i3 device, not via SSH!

#### On the Elo i3 Device:
1. **Open a terminal directly on the Elo i3** (not via SSH)
2. **Navigate to the project directory:**
   ```bash
   cd /home/ur10/Documents/assistant-from-jsecco
   ```
3. **Start the application:**
   ```bash
   ./start_ui.sh
   ```

#### For Testing (Simulation Mode):
```bash
./start_ui.sh --simulate --debug
```

#### Command Line Options:
- `--simulate` - Run without connecting to actual robot
- `--debug` - Enable debug logging
- `--fullscreen` - Start in fullscreen mode (recommended for Elo i3)

### Step 4: Using the Application

#### Main Interface Features:
- **Left Panel**: Jog controls (Cartesian/Joint modes)
- **Center Panel**: Real-time position display and status
- **Right Panel**: Safety controls and system logs

#### Touch Controls:
- **Jog Buttons**: Press and hold for continuous jogging
- **Speed Slider**: Adjust jogging speed
- **Emergency Stop**: Large red button for immediate stop
- **Mode Switch**: Toggle between Cartesian and Joint modes

#### Safety Features:
- Emergency stop functionality
- Real-time safety monitoring
- Connection status indicators
- Automatic disconnect on errors

## 🔧 Troubleshooting

### GUI Not Displaying
**Problem**: Application starts but no GUI appears
**Solution**: Make sure you're running directly on the Elo i3, not via SSH

### Connection Issues
**Problem**: Cannot connect to robot
**Solutions**:
1. Verify robot IP address in config/robot_config.yaml
2. Ensure robot is powered on and network accessible
3. Check network connectivity: `ping YOUR_ROBOT_IP`
4. Verify robot is in remote control mode

### Touch Screen Not Responsive
**Problem**: Touch inputs not working properly
**Solutions**:
1. Restart the application
2. Check if touch screen drivers are installed
3. Run in fullscreen mode: `./start_ui.sh --fullscreen`

### Import Errors
**Problem**: Python import errors
**Solution**: Ensure virtual environment is activated:
```bash
source venv/bin/activate
```

## 📱 Elo i3 Specific Settings

### Optimal Display Settings:
- **Resolution**: 1024x768 (recommended)
- **Fullscreen Mode**: Enabled for best touch experience
- **Font Size**: 12pt (automatically configured)

### Touch Optimization:
- Button minimum size: 80x80 pixels
- Touch margins: 10px
- Large emergency stop button: 100px height

## 🔒 Safety Considerations

⚠️ **CRITICAL SAFETY NOTES:**

1. **Always ensure proper safety measures** when operating the robot
2. **Keep emergency stop accessible** at all times  
3. **Test in simulation mode** before connecting to real robot
4. **Verify workspace clearance** before jogging
5. **Monitor safety status** indicators continuously

## 📊 System Information

### Installed Components:
- ✅ PyQt6 Touch Interface
- ✅ WebSocket Communication (3 channels)
- ✅ Safety Monitoring System
- ✅ Real-time Position Display
- ✅ Emergency Stop Integration

### File Locations:
- **Application**: `/home/ur10/Documents/assistant-from-jsecco/`
- **Configuration**: `config/robot_config.yaml`
- **Logs**: `logs/`
- **Virtual Environment**: `venv/`

### Network Ports Used:
- **30001**: Primary WebSocket (command interface)
- **30003**: Real-time data stream
- **29999**: Dashboard commands

## 🎯 Next Steps

1. **Go to the Elo i3 device directly**
2. **Configure your robot's IP address**
3. **Test in simulation mode first**
4. **Connect to your UR10 and start jogging!**

---

**Author**: jsecco ®  
**Version**: 1.0.0  
**Support**: Check logs in `logs/` directory for troubleshooting
