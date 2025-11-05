# services/sales_script_service.py - PATCH
"""
Add robust JSON parsing to handle LLM response errors
Fix for Issue #7: JSONDecodeError at line 107
"""

import json
import re
import logging

logger = logging.getLogger(__name__)

def parse_llm_response_safe(response_text, source="LLM"):
    """
    Safely parse JSON from LLM response with multiple fallback strategies
    
    Args:
        response_text (str): Raw response from LLM
        source (str): Source identifier for logging
    
    Returns:
        dict: Parsed JSON data
    
    Raises:
        ValueError: If all parsing attempts fail
    """
    if not response_text or not response_text.strip():
        raise ValueError(f"{source}: Empty response")
    
    # Strategy 1: Direct parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.warning(f"{source}: Direct parse failed at line {e.lineno}, col {e.colno}")
        logger.debug(f"Error near: {response_text[max(0, e.pos-100):e.pos+100]}")
    
    # Strategy 2: Extract JSON from markdown code blocks
    try:
        # Match ```json ... ``` or ``` ... ```
        pattern = r'```(?:json)?\s*(.*?)\s*```'
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            json_str = match.group(1)
            logger.info(f"{source}: Extracted JSON from markdown")
            return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"{source}: Markdown extraction failed at line {e.lineno}")
    
    # Strategy 3: Fix common issues
    try:
        cleaned = response_text
        
        # Remove BOM and invisible characters
        cleaned = cleaned.replace('\ufeff', '').replace('\u200b', '')
        
        # Fix single quotes to double quotes (be careful with contractions)
        # Only replace single quotes that are likely JSON delimiters
        cleaned = re.sub(r"(?<=[:\[,\{])\s*'([^']*?)'\s*(?=[,\]\}:])", r'"\1"', cleaned)
        
        # Remove trailing commas before closing brackets
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        # Fix common escaping issues
        cleaned = cleaned.replace("\\'", "'")  # Unescape single quotes
        
        logger.info(f"{source}: Attempting parse with cleaned JSON")
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"{source}: Cleaned parse failed at line {e.lineno}")
    
    # Strategy 4: Try to find and extract valid JSON object
    try:
        # Find first { and last }
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1 and start < end:
            json_str = response_text[start:end+1]
            logger.info(f"{source}: Extracted JSON by finding {{ }} boundaries")
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Strategy 5: Last resort - try to fix specific known issues
    try:
        # Log the problematic section for debugging
        logger.error(f"{source}: All parsing strategies failed")
        logger.error(f"Response length: {len(response_text)} chars")
        logger.error(f"First 500 chars: {response_text[:500]}")
        logger.error(f"Last 500 chars: {response_text[-500:]}")
        
        # Try to identify the specific error location
        lines = response_text.split('\n')
        if len(lines) >= 107:  # Issue #7 error was at line 107
            logger.error(f"Line 107 content: {lines[106]}")
            if len(lines) > 107:
                logger.error(f"Line 108 content: {lines[107]}")
    except:
        pass
    
    raise ValueError(
        f"{source}: Failed to parse JSON after all attempts. "
        f"Response may be malformed. Check logs for details."
    )


# UPDATE: Modify existing generate_script function to use safe parser
def generate_script(config):
    """
    Generate sales script using AI
    
    Args:
        config (dict): Configuration with product info, style, etc.
    
    Returns:
        dict: Generated script data
    """
    try:
        # ... existing code to call LLM ...
        
        # Get response from LLM
        response_text = call_gemini_api(prompt, config)
        
        # OLD (unsafe):
        # script_data = json.loads(response_text)
        
        # NEW (safe with Issue #7 fix):
        script_data = parse_llm_response_safe(
            response_text, 
            source=f"SalesScript_{config.get('script_style', 'Unknown')}"
        )
        
        return script_data
        
    except ValueError as e:
        # Better error message for UI
        error_msg = str(e)
        if "JSONDecodeError" in error_msg or "Failed to parse JSON" in error_msg:
            raise ValueError(
                "Không thể phân tích kịch bản từ AI. "
                "Vui lòng thử lại hoặc thay đổi cài đặt. "
                f"\n\nChi tiết lỗi: {error_msg}"
            )
        raise
    
    except Exception as e:
        logger.exception("Error generating script")
        raise ValueError(f"Lỗi tạo kịch bản: {str(e)}")