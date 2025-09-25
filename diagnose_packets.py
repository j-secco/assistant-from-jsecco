#!/usr/bin/env python3
"""
Diagnose the actual packet structure from the UR10
"""

import sys
import struct
import time

sys.path.insert(0, 'src')

from communication.websocket_receiver import WebSocketReceiver
import yaml

# Load config
with open('config/robot_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

robot_ip = config.get('robot', {}).get('ip_address', '192.168.1.100')
print(f"🔍 Diagnosing packets from {robot_ip}")

ws_receiver = WebSocketReceiver(robot_ip, 30003)

# Disable normal parsing and add packet diagnosis
packet_count = 0

def diagnose_packet(data):
    global packet_count
    packet_count += 1
    
    if packet_count > 5:  # Only analyze first few packets
        return
        
    print(f"\n📦 Packet #{packet_count} - Size: {len(data)} bytes")
    
    # Show first 64 bytes as hex
    hex_data = ' '.join(f'{b:02x}' for b in data[:64])
    print(f"First 64 bytes (hex): {hex_data}")
    
    # Try to find reasonable double values at different offsets
    print("\n🔍 Testing for reasonable doubles at different offsets:")
    
    for offset in range(0, min(len(data)-48, 500), 8):  # Test every 8 bytes
        try:
            # Try both endiannesses
            for endian, name in [('<', 'LE'), ('>', 'BE')]:
                if len(data) >= offset + 48:
                    values = struct.unpack(f'{endian}6d', data[offset:offset + 48])
                    
                    # Check if these look like reasonable robot values
                    if all(-10 < v < 10 for v in values):  # Reasonable range for joints or TCP
                        print(f"  Offset {offset:3d} ({name}): {[f'{v:.3f}' for v in values]}")
                        
        except struct.error:
            continue
            
    print(f"{'='*80}")

# Override the data processing method
ws_receiver._process_realtime_data = diagnose_packet

if ws_receiver.connect():
    print("✅ Connected - collecting packets...")
    time.sleep(3)
    ws_receiver.disconnect()
    print(f"\n📊 Analyzed {packet_count} packets")
else:
    print("❌ Could not connect")
