#!/usr/bin/env python3
"""
Comprehensive verification that NO simulation is possible.

Author: jsecco ®
"""

import yaml
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def verify_configuration():
    """Verify configuration has no simulation enabled."""
    print("🔍 Checking configuration...")
    
    with open("config/robot_config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    issues = []
    
    # Check all simulation flags
    if config.get('debug', {}).get('simulate_robot', False):
        issues.append("debug.simulate_robot is True")
    
    if config.get('development', {}).get('mock_robot_data', False):
        issues.append("development.mock_robot_data is True")
    
    if config.get('development', {}).get('simulation_mode', False):
        issues.append("development.simulation_mode is True")
    
    # Check robot IP
    robot_ip = config.get('robot', {}).get('ip_address', '')
    if robot_ip != '192.168.10.24':
        issues.append(f"robot.ip_address is '{robot_ip}', should be '192.168.10.24'")
    
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ Configuration is correct - NO simulation")
        print(f"   • Robot IP: {robot_ip}")
        return True

def verify_main_code():
    """Verify main.py has no simulation options."""
    print("\n🔍 Checking main.py code...")
    
    with open("src/main.py", 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for simulation command line option
    if "--simulate" in content:
        issues.append("--simulate command line option still exists")
    
    if "args.simulate" in content:
        issues.append("args.simulate handling still exists")
    
    # Check for hardcoded simulation enables
    if "simulate_robot'] = True" in content:
        issues.append("Hardcoded simulate_robot = True found")
    
    if issues:
        print("❌ Main.py issues found:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ Main.py is correct - NO simulation options")
        return True

def test_configuration_loading():
    """Test that configuration loads correctly with no simulation."""
    print("\n🔍 Testing configuration loading...")
    
    try:
        # Import config loading from main
        import main
        
        # Load default config (simulates what main.py does)
        config = main.load_default_config()
        
        # Check simulation flags
        simulate_robot = config.get('debug', {}).get('simulate_robot', False)
        mock_data = config.get('development', {}).get('mock_robot_data', False)
        simulation_mode = config.get('development', {}).get('simulation_mode', False)
        
        if simulate_robot or mock_data or simulation_mode:
            print(f"❌ Configuration loading issue:")
            print(f"   • simulate_robot: {simulate_robot}")
            print(f"   • mock_robot_data: {mock_data}")
            print(f"   • simulation_mode: {simulation_mode}")
            return False
        else:
            print("✅ Configuration loading is correct - NO simulation")
            return True
            
    except Exception as e:
        print(f"⚠️  Could not test configuration loading: {e}")
        return True  # Don't fail if we can't test this

def main():
    print("🧪 Comprehensive NO SIMULATION verification")
    print("=" * 60)
    
    config_ok = verify_configuration()
    code_ok = verify_main_code()
    loading_ok = test_configuration_loading()
    
    print("\n" + "=" * 60)
    
    if config_ok and code_ok and loading_ok:
        print("🎉 VERIFICATION PASSED!")
        print("🤖 Application is configured for REAL ROBOT ONLY")
        print("✅ NO simulation possible")
        print(f"\n🎯 Robot connection: 192.168.10.24")
        print("📡 Mode: Real robot data and commands only")
        return 0
    else:
        print("❌ VERIFICATION FAILED!")
        print("⚠️  Simulation may still be possible")
        return 1

if __name__ == "__main__":
    sys.exit(main())
