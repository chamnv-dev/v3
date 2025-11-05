#!/usr/bin/env python3
# migration_v3_final.py
"""
Final Migration to V3 - All tabs redesigned
"""

import os
import shutil
from pathlib import Path

def update_main(repo_root):
    main_file = repo_root / "main_image2video.py"
    backup_file(main_file)
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    replacements = [
        ("from ui.settings_panel_v2 import SettingsPanelV2",
         "from ui.settings_panel_v3_compact import SettingsPanelV3Compact as SettingsPanel"),
        ("from ui.image2video_panel_v2 import Image2VideoPanelV2",
         "from ui.image2video_panel_v3_merged import Image2VideoPanelV3Merged as Image2VideoPanel"),
        ("from ui.text2video_panel_v2 import Text2VideoPanelV2",
         "from ui.text2video_panel_v3 import Text2VideoPanelV3 as Text2VideoPanel"),
        ("from ui.video_ads_panel_v2 import VideoAdsPanelV2",
         "from ui.video_ads_panel_v3 import VideoAdsPanelV3 as VideoAdsPanel"),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ main_image2video.py updated!")

def backup_file(filepath):
    if filepath.exists():
        backup = filepath.with_suffix(f'.backup_v3_{int(__import__("time").time())}')
        shutil.copy2(filepath, backup)
        print(f"✓ Backup: {backup.name}")

def main():
    print("=" * 70)
    print("🎨 FINAL V3 MIGRATION - ALL TABS REDESIGNED")
    print("=" * 70)
    print()
    
    repo_root = Path(__file__).parent.resolve()
    update_main(repo_root)
    
    print()
    print("✅ MIGRATION COMPLETE!")
    print()
    print("📌 ALL CHANGES:")
    print("  ✅ Settings - 2-column API, super compact")
    print("  ✅ Image2Video - Merged columns, rounded buttons")
    print("  ✅ Text2Video - 'Bạn là chuyên gia', colored tabs, +2px font")
    print("  ✅ Video Ads - Same style as Text2Video")
    print("  ✅ All buttons - Rounded like image, bold +1px")
    print()
    print("🚀 RUN: python main_image2video.py")
    print("=" * 70)

if __name__ == "__main__":
    main()