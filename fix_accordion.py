#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix: Thêm missing function get_voice_config() vào voice_options.py
"""

import os

def fix_voice_options():
    """Add get_voice_config function to voice_options.py"""
    file_path = "services/voice_options.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if function already exists
    if 'def get_voice_config(' in content:
        print(f"ℹ️  {file_path}: get_voice_config() đã tồn tại")
        return False
    
    # Find insertion point - after get_default_voice() function
    insert_marker = '''def get_default_voice(provider: str, language: str = "vi"):
    """Get default voice for a provider and language
    
    Args:
        provider: Provider key
        language: Language code
    
    Returns:
        Voice ID string
    """
    voices = get_voices_for_provider(provider, language)
    return voices[0]["id"] if voices else None'''
    
    new_function = '''

def get_voice_config(provider: str, voice_id: str, language_code: str = "vi") -> Dict[str, Any]:
    """Build voice configuration dictionary for script generation
    
    Args:
        provider: TTS provider key ("google", "elevenlabs", or "openai")
        voice_id: Voice ID
        language_code: Language code (default "vi")
    
    Returns:
        Dictionary with voice configuration including provider, voice_id, language, and metadata
    """
    voice_info = get_voice_info(provider, voice_id)
    
    config = {
        "provider": provider,
        "voice_id": voice_id,
        "language_code": language_code
    }
    
    # Add voice metadata if available
    if voice_info:
        config["voice_name"] = voice_info.get("name", voice_id)
        config["gender"] = voice_info.get("gender", "neutral")
        config["description"] = voice_info.get("description", "")
    
    # Add provider-specific settings
    provider_config = TTS_PROVIDER_CONFIGS.get(provider, {})
    config["supports_ssml"] = provider_config.get("supports_ssml", False)
    config["supports_prosody"] = provider_config.get("supports_prosody", False)
    
    return config'''
    
    if insert_marker in content:
        content = content.replace(insert_marker, insert_marker + new_function)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🔧 Fixed {file_path}:")
        print(f"  ✅ Thêm get_voice_config() function")
        return True
    else:
        print(f"❌ Không tìm thấy điểm insert phù hợp trong {file_path}")
        return False


def main():
    print("=" * 60)
    print("🚀 FIX: Thêm get_voice_config() function")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
    
    if fix_voice_options():
        print("\n✅ HOÀN TẤT!")
        print("\n📌 HƯỚNG DẪN TIẾP THEO:")
        print("1. Chạy lại ứng dụng: python main_image2video.py")
        print("2. Kiểm tra xem còn lỗi import không")
    else:
        print("\nℹ️  Không có thay đổi hoặc đã được fix")


if __name__ == "__main__":
    main()