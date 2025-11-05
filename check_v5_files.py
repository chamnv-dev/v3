# check_v5_files.py
"""
Check if all V5 files exist
"""

import os
from pathlib import Path

def check_files():
    """Check if all required V5 files exist"""
    
    repo_root = Path(__file__).parent
    
    required_files = [
        # V5 Panels
        "ui/image2video_panel_v5_connected.py",
        "ui/text2video_panel_v5_connected.py",
        "ui/video_ads_panel_v5_connected.py",
        
        # V3 Settings (fallback)
        "ui/settings_panel_v3_compact.py",
        
        # Widgets
        "ui/widgets/accordion.py",
        "ui/widgets/compact_button.py",
        "ui/widgets/responsive_utils.py",
        "ui/widgets/key_list_v2.py",
        
        # Styles
        "ui/styles/light_theme_v2.py",
        "ui/styles/main_tab_style.py",
        
        # Main
        "main_image2video.py",
    ]
    
    print("=" * 70)
    print("🔍 CHECKING V5 FILES")
    print("=" * 70)
    print()
    
    missing = []
    existing = []
    
    for file_path in required_files:
        full_path = repo_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
            existing.append(file_path)
        else:
            print(f"❌ {file_path}")
            missing.append(file_path)
    
    print()
    print("=" * 70)
    print(f"📊 SUMMARY: {len(existing)}/{len(required_files)} files found")
    print("=" * 70)
    
    if missing:
        print()
        print("❌ MISSING FILES:")
        for f in missing:
            print(f"   • {f}")
        print()
        print("Please create these files before running the application.")
        return False
    else:
        print()
        print("✅ ALL FILES EXIST!")
        print("You can now run: python main_image2video.py")
        return True

if __name__ == "__main__":
    success = check_files()
    exit(0 if success else 1)