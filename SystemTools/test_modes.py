"""
Test script for DevTools mode switching
Tests development/deployment modes and GUI/CLI interfaces
"""

import sys
import json
import os
from pathlib import Path

# Add SystemTools to path
sys.path.insert(0, str(Path(__file__).parent))

from devtools_config import DevToolsConfig, DevMode, UIMode


def test_config_creation():
    """Test configuration file creation"""
    print("Testing configuration creation...")

    # Create test config
    test_config = DevToolsConfig("test_devtools.json")

    # Check default mode
    assert test_config.current_mode == DevMode.DEVELOPMENT
    print(f"  [OK] Default mode: {test_config.current_mode.value}")

    # Check file creation
    assert os.path.exists("test_devtools.json")
    print(f"  [OK] Config file created")

    # Cleanup
    os.remove("test_devtools.json")
    print("  [OK] Test file cleaned up\n")


def test_mode_switching():
    """Test switching between modes"""
    print("Testing mode switching...")

    config = DevToolsConfig("test_devtools.json")

    # Test development mode
    config.set_mode(DevMode.DEVELOPMENT)
    assert config.is_development()
    assert config.get("verbose_logging") == True
    assert config.get_log_level() == "DEBUG"
    print(f"  [OK] Development mode: verbose={config.get('verbose_logging')}, log={config.get_log_level()}")

    # Test deployment mode
    config.set_mode(DevMode.DEPLOYMENT)
    assert config.is_deployment()
    assert config.get("verbose_logging") == False
    assert config.get_log_level() == "INFO"
    print(f"  [OK] Deployment mode: verbose={config.get('verbose_logging')}, log={config.get_log_level()}")

    # Cleanup
    os.remove("test_devtools.json")
    print("  [OK] Mode switching works\n")


def test_ui_modes():
    """Test UI mode selection"""
    print("Testing UI modes...")

    config = DevToolsConfig("test_devtools.json")

    # Test GUI mode
    config.set_ui_mode(UIMode.GUI)
    assert config.ui_mode == UIMode.GUI
    print(f"  [OK] GUI mode set")

    # Test CLI mode
    config.set_ui_mode(UIMode.CLI)
    assert config.ui_mode == UIMode.CLI
    assert not config.should_use_gui()
    print(f"  [OK] CLI mode set")

    # Test AUTO mode
    config.set_ui_mode(UIMode.AUTO)
    assert config.ui_mode == UIMode.AUTO
    # Auto detection result depends on environment
    gui_available = config.should_use_gui()
    print(f"  [OK] Auto mode: GUI={'available' if gui_available else 'not available'}")

    # Cleanup
    os.remove("test_devtools.json")
    print("  [OK] UI mode selection works\n")


def test_config_persistence():
    """Test configuration persistence"""
    print("Testing configuration persistence...")

    # Create and configure
    config1 = DevToolsConfig("test_devtools.json")
    config1.set_mode(DevMode.DEPLOYMENT)
    config1.set_ui_mode(UIMode.CLI)

    # Load in new instance
    config2 = DevToolsConfig("test_devtools.json")
    assert config2.current_mode == DevMode.DEPLOYMENT
    assert config2.ui_mode == UIMode.CLI
    print(f"  [OK] Settings persisted: mode={config2.current_mode.value}, ui={config2.ui_mode.value}")

    # Cleanup
    os.remove("test_devtools.json")
    print("  [OK] Persistence works\n")


def test_mode_specific_settings():
    """Test mode-specific configuration retrieval"""
    print("Testing mode-specific settings...")

    config = DevToolsConfig("test_devtools.json")

    # Development mode settings
    config.set_mode(DevMode.DEVELOPMENT)
    dev_settings = config.get_mode_config()
    assert "verbose_logging" in dev_settings
    assert dev_settings["log_level"] == "DEBUG"
    print(f"  [OK] Development settings: {len(dev_settings)} options")

    # Deployment mode settings
    config.set_mode(DevMode.DEPLOYMENT)
    deploy_settings = config.get_mode_config()
    assert "verbose_logging" in deploy_settings
    assert deploy_settings["log_level"] == "INFO"
    print(f"  [OK] Deployment settings: {len(deploy_settings)} options")

    # Verify different settings
    assert dev_settings["verbose_logging"] != deploy_settings["verbose_logging"]
    assert dev_settings["max_log_size_mb"] > deploy_settings["max_log_size_mb"]
    print(f"  [OK] Settings differ between modes")

    # Cleanup
    os.remove("test_devtools.json")
    print("  [OK] Mode-specific settings work\n")


def test_cli_integration():
    """Test CLI interface detection"""
    print("Testing CLI interface integration...")

    config = DevToolsConfig("test_devtools.json")

    # Test CLI-specific options
    config.set_ui_mode(UIMode.CLI)
    colored = config.get("colored_output")
    compact = config.get("compact_display")
    interactive = config.get("interactive_mode")

    print(f"  [OK] CLI options: colored={colored}, compact={compact}, interactive={interactive}")

    # Test GUI-specific options
    config.set_ui_mode(UIMode.GUI)
    theme = config.get("theme")
    window_size = config.get("window_size")
    tooltips = config.get("show_tooltips")

    print(f"  [OK] GUI options: theme={theme}, size={window_size}, tooltips={tooltips}")

    # Cleanup
    os.remove("test_devtools.json")
    print("  [OK] UI-specific options work\n")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("DevTools Mode System - Test Suite")
    print("=" * 60 + "\n")

    tests = [
        test_config_creation,
        test_mode_switching,
        test_ui_modes,
        test_config_persistence,
        test_mode_specific_settings,
        test_cli_integration
    ]

    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"  [FAIL] Test failed: {e}\n")
            failed.append(test.__name__)

    print("=" * 60)
    if not failed:
        print("[PASSED] All tests passed!")
    else:
        print(f"[FAILED] {len(failed)} tests failed: {', '.join(failed)}")
    print("=" * 60)

    return len(failed) == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)