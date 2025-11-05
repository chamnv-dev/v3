#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration Script V2 - Update to all new panels
"""

import os
import shutil
from pathlib import Path

def backup_file(filepath):
    """Backup file"""
    if filepath.exists():
        backup = filepath.with_suffix(filepath.suffix + '.backup_v2_' + str(int(__import__('time').time())))
        shutil.copy2(filepath, backup)
        print(f"✓ Backup: {backup.name}")
        return True
    return False

def update_main_file(repo_root):
    """Update main_image2video.py"""
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
         "from ui.settings_panel_v2_fixed import SettingsPanelV2Fixed as SettingsPanel"),
        ("from ui.image2video_panel import Image2VideoPanel",
         "from ui.image2video_panel_v2 import Image2VideoPanelV2 as Image2VideoPanel"),
        ("from ui.text2video_panel import Text2VideoPanel",
         "from ui.text2video_panel_v2 import Text2VideoPanelV2 as Text2VideoPanel"),
        ("from ui.video_ads_panel import VideoAdsPanel",
         "from ui.video_ads_panel_v2 import VideoAdsPanelV2 as VideoAdsPanel"),
        ("from ui.styles.light_theme import apply_light_theme",
         "from ui.styles.light_theme_v2 import apply_light_theme_v2 as apply_light_theme"),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✓ Replaced: {old[:40]}...")
    
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated: {main_file.name}")
    return True

def main():
    print("=" * 70)
    print("🚀 COMPLETE GUI REDESIGN V2 - MIGRATION")
    print("=" * 70)
    print()
    
    repo_root = Path(__file__).parent.resolve()
    
    print("🔧 Updating main_image2video.py...")
    if update_main_file(repo_root):
        print()
        print("=" * 70)
        print("✅ MIGRATION COMPLETE!")
        print()
        print("📌 ALL TABS REDESIGNED:")
        print("  ✅ Settings Panel - Accordion, compact, prominent inputs")
        print("  ✅ Image2Video - 250px sidebar, better scenes")
        print("  ✅ Text2Video - Compact left, prominent inputs")
        print("  ✅ Video Ads - 250px sidebar, horizontal buttons")
        print()
        print("🚀 TEST:")
        print("  python main_image2video.py")
        print("=" * 70)

if __name__ == "__main__":
    main()