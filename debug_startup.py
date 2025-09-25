#!/usr/bin/env python3
"""
Debug version to identify why the application closes immediately.

Author: jsecco ®
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_basic_qt():
    """Test basic Qt functionality."""
    print("🔍 Testing basic Qt functionality...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QLabel
        from PyQt6.QtCore import QTimer
        
        print("✅ Qt imports successful")
        
        # Test QApplication creation
        app = QApplication.instance() or QApplication(sys.argv)
        print("✅ QApplication created")
        
        # Test basic widget creation
        label = QLabel("Test")
        print("✅ Basic widget created")
        
        # Test timer creation
        timer = QTimer()
        print("✅ Timer created")
        
        return True
        
    except Exception as e:
        print(f"❌ Qt test failed: {e}")
        traceback.print_exc()
        return False

def test_imports():
    """Test all required imports."""
    print("🔍 Testing imports...")
    
    try:
        # Test main imports
        from ui.main_window import MainWindow
        print("✅ MainWindow import")
        
        from control.jog_controller import JogController  
        print("✅ JogController import")
        
        import yaml
        print("✅ YAML import")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_config_loading():
    """Test configuration loading."""
    print("🔍 Testing configuration loading...")
    
    try:
        import yaml
        with open("config/robot_config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"✅ Configuration loaded")
        print(f"   Robot IP: {config.get('robot', {}).get('ip_address')}")
        print(f"   Simulation: {config.get('debug', {}).get('simulate_robot', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        traceback.print_exc()
        return False

def test_display_environment():
    """Test display environment."""
    print("🔍 Testing display environment...")
    
    display = os.environ.get('DISPLAY', 'Not set')
    print(f"   DISPLAY: {display}")
    
    wayland_display = os.environ.get('WAYLAND_DISPLAY', 'Not set')
    print(f"   WAYLAND_DISPLAY: {wayland_display}")
    
    xdg_session_type = os.environ.get('XDG_SESSION_TYPE', 'Not set')
    print(f"   XDG_SESSION_TYPE: {xdg_session_type}")
    
    return True

def run_minimal_app():
    """Run a minimal Qt application to test event loop."""
    print("🔍 Testing minimal Qt application...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
        from PyQt6.QtCore import QTimer
        
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create minimal window
        window = QMainWindow()
        window.setWindowTitle("Qt Test")
        window.setCentralWidget(QLabel("If you see this, Qt is working!"))
        window.resize(300, 100)
        window.show()
        
        print("✅ Minimal window created and shown")
        
        # Set up a timer to close after 3 seconds
        def close_app():
            print("✅ Timer triggered - closing test app")
            app.quit()
            
        timer = QTimer()
        timer.timeout.connect(close_app)
        timer.start(3000)  # 3 seconds
        
        print("🚀 Starting Qt event loop for 3 seconds...")
        result = app.exec()
        print(f"✅ Qt event loop finished with code: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal app test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run comprehensive startup diagnostics."""
    print("🧪 UR10 Application Startup Diagnostics")
    print("=" * 50)
    
    # Change to correct directory
    os.chdir(Path(__file__).parent)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Run tests
    tests = [
        ("Display Environment", test_display_environment),
        ("Basic Qt", test_basic_qt),
        ("Imports", test_imports), 
        ("Configuration", test_config_loading),
        ("Minimal Qt App", run_minimal_app),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            traceback.print_exc()
            results[test_name] = False
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Results Summary:")
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! The issue might be elsewhere.")
        print("💡 Suggestion: Check for signal handlers or external process termination")
    else:
        print("\n❌ Some tests failed. Fix these issues first.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
