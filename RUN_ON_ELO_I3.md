# 🚀 **RUN UR10 KIOSK INTERFACE ON ELO i3**

## ⚠️ **IMPORTANT: Run Directly on Elo i3 Device**

The kiosk interface must be run directly on the Elo i3 touchscreen device, **NOT via SSH**.

## 📱 **Step-by-Step Instructions**

### **Step 1: Access the Elo i3 Device**
1. **Go to the Elo i3 touchscreen device physically**
2. **Do not use SSH or remote connection**
3. **Open a terminal directly on the Elo i3**

### **Step 2: Navigate to Application**
```bash
cd /home/ur10/Documents/assistant-from-jsecco
```

### **Step 3: Launch the Kiosk Interface**

**Option A: Using the launcher script (Recommended)**
```bash
./launch_kiosk.sh
```

**Option B: Manual launch**
```bash
source venv/bin/activate
export DISPLAY=:0
python run_local.py --fullscreen --simulate
```

**Option C: Using the desktop launcher**
- Double-click the **"UR10 Kiosk Interface"** icon on the desktop

## 🎮 **What to Expect**

When you run the application on the Elo i3, you should see:

1. **Fullscreen kiosk interface** opens automatically
2. **Large touch buttons** (120×80 pixels) optimized for fingers
3. **Settings button (⚙️)** in the top header
4. **Three main panels**:
   - **Left**: Jog controls (Cartesian/Joint modes)
   - **Center**: Position display and status
   - **Right**: Safety controls and emergency stop

## ⚙️ **Configuration**

1. **Click the ⚙️ Settings button** in the header
2. **Go to Robot Connection tab**
3. **Enter your UR10's IP address** (e.g., 192.168.1.100)
4. **Click Test Connection** to verify
5. **Save & Apply** changes
6. **Restart the application**

## 🔧 **Troubleshooting**

### **If the interface doesn't appear:**
- Make sure you're running directly on the Elo i3, not via SSH
- Check that the display is set: `echo $DISPLAY` (should show `:0`)
- Try: `export DISPLAY=:0` before running

### **If buttons are too small:**
1. Click **⚙️ Settings**
2. Go to **Interface** tab
3. Increase **Button Size** (60-200 pixels)
4. Save and restart

### **To exit the application:**
- Press **Ctrl+C** in the terminal
- Or click the **Exit** button in the footer

## 🎯 **Current Configuration**

The kiosk is currently configured with:
- **Button Size**: 120 pixels (large for touch)
- **Touch Margins**: 15 pixels
- **Fullscreen Mode**: Enabled
- **Simulation Mode**: Enabled (safe for testing)

## 📁 **Files Ready for Deployment**

All files are prepared in: `/home/ur10/Documents/assistant-from-jsecco/`

- ✅ **launch_kiosk.sh** - Main launcher script
- ✅ **UR10-Kiosk-Launch.desktop** - Desktop shortcut
- ✅ **Configuration dialog** - Built-in settings
- ✅ **Large touch buttons** - Kiosk optimized
- ✅ **Safety systems** - Industrial grade

## 🎉 **Ready to Test!**

**Go to the Elo i3 device now and run:**
```bash
cd /home/ur10/Documents/assistant-from-jsecco
./launch_kiosk.sh
```

The kiosk interface should open in fullscreen mode with large, touch-friendly buttons! 📱✨
