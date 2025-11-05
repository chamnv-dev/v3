#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Redesign Migration Script
Switches from old UI to new UI v2
"""

import os
import shutil
from pathlib import Path

def backup_file(filepath):
    """Create backup of file"""
    if filepath.exists():
        backup = filepath.with_suffix(filepath.suffix + '.backup_v1')
        shutil.copy2(filepath, backup)
        print(f"✓ Backup created: {backup.name}")
        return True
    return False

def update_main_file(repo_root):
    """Update main_image2video.py to use new UI"""
    main_file = repo_root / "main_image2video.py"
    
    if not main_file.exists():
        print(f"❌ Not found: {main_file}")
        return False
    
    backup_file(main_file)
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace imports
    replacements = [
        ("from ui.settings_panel import SettingsPanel", 
         "from ui.settings_panel_v2 import SettingsPanelV2"),
        ("from ui.styles.light_theme import apply_light_theme",
         "from ui.styles.light_theme_v2 import apply_light_theme_v2"),
        ("SettingsPanel(self)", 
         "SettingsPanelV2(self)"),
        ("apply_light_theme(app)",
         "apply_light_theme_v2(app)"),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✓ Replaced: {old[:50]}...")
    
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated: {main_file}")
    return True

def check_files_exist(repo_root):
    """Check if all new files exist"""
    required_files = [
        "ui/widgets/accordion.py",
        "ui/widgets/compact_button.py",
        "ui/widgets/responsive_utils.py",
        "ui/settings_panel_v2.py",
        "ui/styles/light_theme_v2.py",
    ]
    
    missing = []
    for file_path in required_files:
        full_path = repo_root / file_path
        if not full_path.exists():
            missing.append(file_path)
    
    return missing

def main():
    print("=" * 70)
    print("🚀 GUI REDESIGN MIGRATION")
    print("=" * 70)
    print()
    
    repo_root = Path(__file__).parent.resolve()
    print(f"📁 Repository: {repo_root}")
    print()
    
    # Check if all files exist
    print("📋 Checking required files...")
    missing = check_files_exist(repo_root)
    
    if missing:
        print("❌ Missing files:")
        for f in missing:
            print(f"   • {f}")
        print()
        print("Please create all files first!")
        return
    
    print("✅ All required files exist")
    print()
    
    # Update main file
    print("🔧 Updating main_image2video.py...")
    if update_main_file(repo_root):
        print()
        print("=" * 70)
        print("✅ MIGRATION COMPLETE!")
        print()
        print("📌 CHANGES:")
        print("  • Settings now uses SettingsPanelV2 (accordion, compact)")
        print("  • Theme updated to light_theme_v2 (32px buttons)")
        print("  • Old files backed up with .backup_v1 extension")
        print()
        print("🚀 TEST:")
        print("  python main_image2video.py")
        print()
        print("🔄 ROLLBACK (if needed):")
        print("  mv main_image2video.py.backup_v1 main_image2video.py")
        print("=" * 70)
    else:
        print("❌ Migration failed")

if __name__ == "__main__":
    main()