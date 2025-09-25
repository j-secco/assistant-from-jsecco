#!/usr/bin/env python3
"""
Test different display connection methods.

Author: jsecco ®
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_display_method(display_env, description):
    """Test a specific display environment setup."""
    print(f"\n🔍 Testing {description}...")
    
    # Save current environment
    old_env = {}
    for key in ['DISPLAY', 'WAYLAND_DISPLAY', 'XDG_SESSION_TYPE', 'XDG_RUNTIME_DIR']:
        old_env[key] = os.environ.get(key)
    
    try:
        # Set new environment
        for key, value in display_env.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value
        
        print(f"   Environment set:")
        for key, value in display_env.items():
            print(f"     {key}={value}")
        
        # Try Qt
        from PyQt6.QtWidgets import QApplication, QLabel
        
        app = QApplication.instance() or QApplication(sys.argv)
        label = QLabel("Test")
        label.show()
        
        print(f"   ✅ Qt application created successfully")
        
        # Quick test of event loop
        start_time = time.time()
        app.processEvents()  # Process pending events
        duration = time.time() - start_time
        
        print(f"   ✅ Event processing works (took {duration:.3f}s)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    finally:
        # Restore environment
        for key, value in old_env.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value

def main():
    """Test different display connection methods."""
    print("🧪 Display Connection Test")
    print("=" * 50)
    
    # Test different display configurations
    test_configs = [
        # Wayland configuration
        ({
            'WAYLAND_DISPLAY': 'wayland-0',
            'XDG_SESSION_TYPE': 'wayland',
            'XDG_RUNTIME_DIR': '/run/user/1000',
            'DISPLAY': None
        }, "Wayland (wayland-0)"),
        
        # X11 configuration with :0
        ({
            'DISPLAY': ':0',
            'XDG_SESSION_TYPE': 'x11',
            'XDG_RUNTIME_DIR': '/run/user/1000',
            'WAYLAND_DISPLAY': None
        }, "X11 (:0)"),
        
        # X11 configuration with :1
        ({
            'DISPLAY': ':1',
            'XDG_SESSION_TYPE': 'x11', 
            'XDG_RUNTIME_DIR': '/run/user/1000',
            'WAYLAND_DISPLAY': None
        }, "X11 (:1)"),
        
        # Try both (let Qt choose)
        ({
            'DISPLAY': ':0',
            'WAYLAND_DISPLAY': 'wayland-0',
            'XDG_SESSION_TYPE': 'wayland',
            'XDG_RUNTIME_DIR': '/run/user/1000'
        }, "Auto-detect (both set)"),
    ]
    
    results = []
    for config, description in test_configs:
        result = test_display_method(config, description)
        results.append((description, result))
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Results:")
    working_configs = []
    for description, result in results:
        status = "✅ WORKS" if result else "❌ FAILS"
        print(f"   {status} {description}")
        if result:
            working_configs.append(description)
    
    if working_configs:
        print(f"\n🎉 Working configurations found:")
        for config in working_configs:
            print(f"   • {config}")
    else:
        print(f"\n❌ No working display configurations found")
        print("💡 Suggestions:")
        print("   • Check if you're running from the actual desktop session")
        print("   • Try running directly on the console (not SSH)")
        print("   • Check display permissions")
    
    return len(working_configs) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
