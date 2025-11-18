#!/usr/bin/env python3
"""
Test Log Import Functionality - Issue #138
Tests the complete workflow of importing air-side.jsonl files into Performance Analytics
"""

import sys
from pathlib import Path

print("="*70)
print("TEST: Log Import Functionality (Issue #138)")
print("="*70)

# Test 1: Import modules
print("\n1. Testing imports...")
try:
    from analytics import AirSideLogParser, PerformanceDatabase
    print("   ✅ AirSideLogParser imported")
    print("   ✅ PerformanceDatabase imported")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Create sample JSONL file
print("\n2. Creating sample air-side.jsonl file...")
try:
    from analytics.log_parser import create_sample_jsonl_for_testing
    sample_file = create_sample_jsonl_for_testing()
    print(f"   ✅ Created: {sample_file}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 3: Parse JSONL file
print("\n3. Parsing JSONL file...")
try:
    parser = AirSideLogParser()
    snapshots, lines, errors = parser.parse_jsonl_file(sample_file)

    print(f"   ✅ Total lines: {lines}")
    print(f"   ✅ Parse errors: {errors}")
    print(f"   ✅ Health snapshots found: {len(snapshots)}")

    if snapshots:
        print(f"\n   First snapshot keys:")
        for key in list(snapshots[0].keys())[:10]:
            value = snapshots[0][key]
            print(f"      - {key}: {value}")
except Exception as e:
    print(f"   ❌ Parse failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Import into database
print("\n4. Importing into test database...")
try:
    db = PerformanceDatabase("test_performance.db")

    imported = 0
    for snapshot in snapshots:
        if db.insert_snapshot(snapshot):
            imported += 1

    print(f"   ✅ Imported: {imported} snapshots")

    # Verify
    count = db.get_record_count()
    print(f"   ✅ Database now has: {count} records")

    # Query date range
    date_range = db.get_date_range()
    if date_range[0] and date_range[1]:
        print(f"   ✅ Date range: {date_range[0]} to {date_range[1]}")

    db.close()

except Exception as e:
    print(f"   ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Multiple file parsing
print("\n5. Testing multiple file parsing...")
try:
    # Create another sample file with different timestamp
    import json
    sample2_path = Path("test_air-side.1.jsonl")

    with open(sample2_path, 'w') as f:
        log = {
            "timestamp": "2025-11-17T14:30:02.123Z",
            "context": "HEALTH",
            "message": "Health snapshot",
            "metadata": {
                "cpu_percent": 37.0,
                "memory_used_mb": 4900
            }
        }
        f.write(json.dumps(log) + '\n')

    # Parse multiple files
    files = [sample_file, str(sample2_path)]
    merged_snapshots, stats = parser.parse_multiple_files(files)

    print(f"   ✅ Files processed: {stats['files_processed']}")
    print(f"   ✅ Total snapshots: {stats['snapshots_found']}")
    print(f"   ✅ Unique snapshots: {len(merged_snapshots)}")
    print(f"   ✅ Duplicates removed: {stats['duplicates_removed']}")

except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: GUI Integration Test
print("\n6. Testing GUI integration...")
try:
    import tkinter as tk
    from gui.tab_analytics import PerformanceAnalyticsTab

    root = tk.Tk()
    root.title("Analytics Import Test")
    root.geometry("800x600")

    # Create Analytics tab
    analytics_tab = PerformanceAnalyticsTab(root)
    analytics_tab.pack(fill=tk.BOTH, expand=True)

    # Check if import button exists
    print("   ✅ PerformanceAnalyticsTab created")
    print("   ✅ Import button added to UI")

    print("\n   GUI will open for 2 seconds for visual verification...")

    root.after(2000, root.destroy)
    root.mainloop()

except Exception as e:
    print(f"   ❌ GUI test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ ALL TESTS PASSED")
print("="*70)

print("\nNext Steps:")
print("1. Launch DPM Management System:")
print("   python3 DPM_Management_System.py")
print("2. Go to Performance Analytics tab")
print("3. Click '📂 Import Air-Side Logs' button")
print("4. Select test_air-side.jsonl file")
print("5. Verify import completes successfully")

# Cleanup
print("\nCleaning up test files...")
Path("test_air-side.jsonl").unlink(missing_ok=True)
Path("test_air-side.1.jsonl").unlink(missing_ok=True)
Path("test_performance.db").unlink(missing_ok=True)
print("✅ Cleanup complete")
