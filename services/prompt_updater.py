# -*- coding: utf-8 -*-
"""
System Prompts Updater Service
Fetches and updates domain prompts from Google Sheets
"""
import csv
import io
import re
import requests
from typing import Dict, List, Tuple


# Default Google Sheets URL (can be overridden)
DEFAULT_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1ohiL6xOBbjC7La2iUdkjrVjG4IEUnVWhI0fRoarD6P0/edit?gid=1507296519"

def extract_sheet_info(sheet_url: str) -> Tuple[str, str, str]:
    """
    Extract sheet ID and gid from Google Sheets URL
    
    Args:
        sheet_url: Full Google Sheets URL
        
    Returns:
        Tuple of (sheet_id, gid, error_message)
        - sheet_id: The spreadsheet ID
        - gid: The sheet/tab ID (gid parameter)
        - error_message: Empty if success, error message if failed
    
    Examples:
        https://docs.google.com/spreadsheets/d/SHEET_ID/edit?gid=GID
        https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=GID
    """
    try:
        # Extract sheet ID
        sheet_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not sheet_match:
            return "", "", "❌ URL không hợp lệ: Không tìm thấy spreadsheet ID"
        
        sheet_id = sheet_match.group(1)
        
        # Extract gid (optional, default to 0)
        gid_match = re.search(r'[?&#]gid=(\d+)', sheet_url)
        gid = gid_match.group(1) if gid_match else "0"
        
        return sheet_id, gid, ""
        
    except Exception as e:
        return "", "", f"❌ Lỗi khi parse URL: {str(e)}"

def fetch_prompts_from_sheets(sheet_url: str = None) -> Tuple[Dict[str, Dict[str, str]], str]:
    """
    Fetch system prompts from Google Sheets CSV export
    
    Args:
        sheet_url: Custom Google Sheets URL (optional, uses default if None)
    
    Returns:
        Tuple of (prompts_dict, error_message)
        - prompts_dict: Nested dict with structure {domain: {topic: system_prompt}}
        - error_message: Empty string if success, error message if failure
    
    Expected CSV format:
    Domain,Topic,System Prompt
    GIÁO DỤC/HACKS,Mẹo Vặt (Life Hacks) Độc đáo,"Prompt text..."
    """
    # Use default URL if not provided
    if sheet_url is None:
        sheet_url = DEFAULT_SHEETS_URL
    
    # Extract sheet ID and gid from URL
    sheet_id, gid, error = extract_sheet_info(sheet_url)
    if error:
        return {}, error
    
    # Build CSV export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{{sheet_id}}/export?format=csv&gid={{gid}}"
    
    try:
        # Fetch CSV from Google Sheets
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        # Parse CSV
        csv_content = response.content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Build nested dictionary
        prompts = {}
        row_count = 0
        
        for row in csv_reader:
            domain = row.get('Domain', '').strip()
            topic = row.get('Topic', '').strip()
            system_prompt = row.get('System Prompt', '').strip()
            
            # Skip empty rows
            if not domain or not topic or not system_prompt:
                continue
            
            # Add to nested dict
            if domain not in prompts:
                prompts[domain] = {}
            
            prompts[domain][topic] = system_prompt
            row_count += 1
        
        if row_count == 0:
            return {}, "⚠️ Không tìm thấy dữ liệu hợp lệ trong CSV (file trống hoặc sai định dạng)"
        
        return prompts, ""
        
    except requests.exceptions.Timeout:
        return {}, "❌ Timeout - vui lòng kiểm tra kết nối internet"
    
    except requests.exceptions.RequestException as e:
        return {}, f"❌ Lỗi mạng: {str(e)}"
    
    except Exception as e:
        return {}, f"❌ Lỗi không xác định: {str(e)}"


def generate_prompts_code(prompts: Dict[str, Dict[str, str]], sheet_url: str = None) -> str:
    """
    Generate Python code for domain_prompts.py from prompts dictionary
    
    Args:
        prompts: Nested dict with structure {domain: {topic: system_prompt}}
        sheet_url: Google Sheets URL for documentation (optional)
    
    Returns:
        Complete Python code for domain_prompts.py
    """
    # Use default URL if not provided
    if sheet_url is None:
        sheet_url = DEFAULT_SHEETS_URL
    
    lines = [
        '# -*- coding: utf-8 -*-',
        '"""',
        'Domain-specific system prompts for video generation',
        f'Auto-generated from Google Sheet: {{sheet_url}}',
        '"""',
        '',
        '# Domain → Topics → System Prompts mapping',
        'DOMAIN_PROMPTS = {'
    ]
    
    # Sort domains for consistent output
    for domain in sorted(prompts.keys()):
        lines.append(f'    "{{domain}}": {{')
        
        # Sort topics within each domain
        topics = prompts[domain]
        for topic in sorted(topics.keys()):
            prompt = topics[topic]
            # Escape quotes in prompt text
            escaped_prompt = prompt.replace('\\', '\\\\').replace('"', '\"')
            lines.append(f'        "{{topic}}": "{{escaped_prompt}}",')
        
        lines.append('    },')
    
    lines.append('}')
    lines.append('')
    
    # Add utility functions
    utility_code = '''

def get_all_domains():
    """Get list of all domain names"""
    return list(DOMAIN_PROMPTS.keys())


def get_topics_for_domain(domain):
    """Get list of topics for a specific domain"""
    return list(DOMAIN_PROMPTS.get(domain, {}).keys())


def get_system_prompt(domain, topic):
    """Get system prompt for a specific domain and topic"""
    return DOMAIN_PROMPTS.get(domain, {}).get(topic, "")


def build_expert_intro(domain, topic, language="vi"):
    """Build expert introduction text for script generation
    
    Args:
        domain: Domain name (e.g., "GIÁO DỤC/HACKS")
        topic: Topic name (e.g., "Mẹo Vặt (Life Hacks) Độc đáo")
        language: Language code ("vi" or "en")
    
    Returns:
        Formatted expert introduction text
    """
    system_prompt = get_system_prompt(domain, topic)
    
    if not system_prompt:
        return ""
    
    if language == "vi":
        intro = f"""Tôi là chuyên gia trong lĩnh vực {{domain}}, chuyên về {{topic}}. 
Tôi đã nhận ý tưởng từ bạn và sẽ biến nó thành kịch bản và câu chuyện theo yêu cầu của bạn. 

{{system_prompt}}

Kịch bản như sau:"""
    else:
        intro = f"""I am an expert in {{domain}}, specializing in {{topic}}. 
I have received your idea and will turn it into a script and story according to your requirements.

{{system_prompt}}

Script as follows:"""
    
    return intro


def get_all_prompts():
    """Get all domain-topic-prompt combinations"""
    result = []
    for domain, topics in DOMAIN_PROMPTS.items():
        for topic, prompt in topics.items():
            result.append({
                "domain": domain,
                "topic": topic,
                "system_prompt": prompt
            })
    return result


def reload_prompts():
    """
    Hot reload prompts by reimporting the module
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import importlib
        import sys
        
        # Get the current module
        current_module = sys.modules.get(__name__)
        
        if current_module:
            # Reload the module
            importlib.reload(current_module)
            return True, "✅ Đã reload prompts thành công!"
        else:
            return False, "❌ Không tìm thấy module để reload"
            
    except Exception as e:
        return False, f"❌ Lỗi khi reload: {str(e)}"
'''    
    lines.append(utility_code)
    
    return '\n'.join(lines)

def update_prompts_file(file_path: str, sheet_url: str = None) -> Tuple[bool, str]:
    """
    Update domain_prompts.py file with latest data from Google Sheets
    
    Args:
        file_path: Path to domain_prompts.py file
        sheet_url: Custom Google Sheets URL (optional, uses default if None)
    
    Returns:
        Tuple of (success, message)
    """
    # Fetch prompts
    prompts, error = fetch_prompts_from_sheets(sheet_url)
    
    if error:
        return False, error
    
    # Generate new code
    new_code = generate_prompts_code(prompts, sheet_url)
    
    # Write to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        
        # Count domains and topics
        domain_count = len(prompts)
        topic_count = sum(len(topics) for topics in prompts.values())
        
        return True, f"✅ Cập nhật thành công! {{domain_count}} domains, {{topic_count}} topics"
        
    except Exception as e:
        return False, f"❌ Lỗi khi ghi file: {{str(e)}}"


if __name__ == "__main__":
    # Test fetching
    prompts, error = fetch_prompts_from_sheets()
    if error:
        print(f"Error: {{error}}")
    else:
        print(f"Success! Fetched {{len(prompts)}} domains")
        for domain, topics in prompts.items():
            print(f"  - {{domain}}: {{len(topics)}} topics")