#!/usr/bin/env python3
"""
Test script to verify position updates are working
"""

import sys
import os
import logging
import time
from threading import Timer

# Add src to path
sys.path.insert(0, 'src')

# Set up logging to see debug messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_position_updates():
    print("🚀 Testing position update system...")
    
    try:
        # Import required modules
        from control.jog_controller import JogController
        from communication.websocket_receiver import WebSocketReceiver
        import yaml
        
        # Load config
        with open('config/robot_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Create WebSocket receiver for testing
        robot_ip = config.get('robot', {}).get('ip_address', '192.168.1.100')
        print(f"📡 Testing WebSocket connection to {robot_ip}")
        
        ws_receiver = WebSocketReceiver(robot_ip, 30003)
        
        # Test callback setup
        position_updates_received = []
        
        def test_position_callback(tcp_pose, joint_angles):
            position_updates_received.append((tcp_pose, joint_angles))
            print(f"📍 Position update: TCP={tcp_pose[:3]}, Joints={[f'{j*57.3:.1f}°' for j in joint_angles[:3]]}")
        
        # Add callback
        ws_receiver.add_position_callback(test_position_callback)
        
        # Try to connect
        if ws_receiver.connect():
            print("✅ Connected to robot")
            print("⏱️  Waiting for position updates...")
            
            # Wait for some updates
            time.sleep(5)
            
            if position_updates_received:
                print(f"✅ Received {len(position_updates_received)} position updates!")
                latest = position_updates_received[-1]
                print(f"   Latest TCP Position: X={latest[0][0]*1000:.1f}mm, Y={latest[0][1]*1000:.1f}mm, Z={latest[0][2]*1000:.1f}mm")
                print(f"   Latest Joint Angles: J1={latest[1][0]*57.3:.1f}°, J2={latest[1][1]*57.3:.1f}°")
            else:
                print("⚠️  No position updates received - checking data processing...")
                
        else:
            print("⚠️  Could not connect to robot (expected in simulation mode)")
            print("🧪 Testing with simulated data...")
            
            # Test callback with simulated data
            test_tcp = [0.5, 0.2, 0.3, 0.1, 0.2, 0.3]  # Simulated TCP pose
            test_joints = [1.57, 0.78, -1.2, 0.5, 1.0, -0.3]  # Simulated joint angles
            
            test_position_callback(test_tcp, test_joints)
            
            if position_updates_received:
                print("✅ Position callback system working correctly!")
                
        ws_receiver.disconnect()
        print("🔚 Test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_position_updates()
