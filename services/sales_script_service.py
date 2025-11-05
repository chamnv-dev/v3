# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
import datetime, json, re
import sys
from pathlib import Path
from services.gemini_client import GeminiClient, MissingAPIKey

def parse_llm_response_safe(response_text: str, source: str = "LLM") -> Dict[str, Any]:
    """
    Robust JSON parser with 5 fallback strategies to handle malformed LLM responses.
    
    Args:
        response_text: Raw text response from LLM
        source: Source identifier for logging (e.g., "SalesScript", "SocialMedia")
    
    Returns:
        Parsed JSON dictionary
        
    Raises:
        json.JSONDecodeError: If all parsing strategies fail
    """
    if not response_text or not response_text.strip():
        raise ValueError(f"Empty response from {source}")
    
    # Strategy 1: Direct JSON parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 1 failed (direct parse): {e}", file=sys.stderr)
    
    # Strategy 2: Extract from markdown code blocks
    try:
        # Remove markdown code blocks (```json ... ``` or ``` ... ```)
        cleaned = response_text
        if "```" in cleaned:
            # Extract content between code blocks
            pattern = r'```(?:json)?\s*(.*?)\s*```'
            matches = re.findall(pattern, cleaned, re.DOTALL)
            if matches:
                cleaned = matches[0].strip()
                return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 2 failed (markdown extraction): {e}", file=sys.stderr)
    
    # Strategy 3: Fix common issues
    try:
        cleaned = response_text.strip()
        
        # Remove BOM if present
        if cleaned.startswith('\ufeff'):
            cleaned = cleaned[1:]
        
        # Remove markdown code blocks
        cleaned = re.sub(r'```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```', '', cleaned)
        
        # Replace single quotes with double quotes (but not within strings)
        # Simple approach: only if not already using double quotes
        if "'" in cleaned and cleaned.count("'") > cleaned.count('"'):
            # This is a simplified approach - may need refinement
            cleaned = cleaned.replace("'", '"')
        
        # Remove trailing commas before } or ]
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        # Fix common escaping issues
        cleaned = cleaned.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
        
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 3 failed (common fixes): {e}", file=sys.stderr)
    
    # Strategy 4: Find JSON by boundaries
    try:
        # Find first { and last }
        start = response_text.find('{')
        end = response_text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            json_str = response_text[start:end+1]
            
            # Try to parse
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Apply fixes from strategy 3
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 4 failed (boundary extraction): {e}", file=sys.stderr)
    
    # Strategy 5: Detailed error logging and re-raise
    print(f"[ERROR] {source} All parsing strategies failed!", file=sys.stderr)
    print(f"[ERROR] Response length: {len(response_text)} characters", file=sys.stderr)
    print(f"[ERROR] First 500 chars: {response_text[:500]}", file=sys.stderr)
    print(f"[ERROR] Last 500 chars: {response_text[-500:]}", file=sys.stderr)
    
    # Try one last time to get a better error message
    try:
        json.loads(response_text)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"{source} JSON parsing failed after all strategies. "
            f"Error at line {e.lineno}, column {e.colno}: {e.msg}",
            e.doc,
            e.pos
        )
    
    # Should not reach here
    raise ValueError(f"Unexpected parsing failure for {source}")

def _scene_count(total_sec:int)->int:
    return max(1, (int(total_sec)+8-1)//8)

logger = logging.getLogger(__name__)

def _try_parse_json(raw:str)->Dict[str,Any]:
    """Parse JSON with robust error handling - delegates to parse_llm_response_safe"""
    return parse_llm_response_safe(raw, "GeneralJSON")

def _models_description(first_model_json:str)->str:
    return first_model_json if first_model_json else "No specific models described."

def _images_refs(has_model:bool, product_count:int)->str:
    out=[]
    if has_model: out.append("- An image is provided with source reference 'model-1'")
    for i in range(product_count): out.append(f"- An image is provided with source reference 'product-{i+1}'")
    return "\\n".join(out)

def _build_system_prompt(cfg:Dict[str,Any], sceneCount:int, models_json:str, product_count:int)->str:
    visualStyleString = cfg.get("image_style") or "Cinematic"
    idea = cfg.get("idea") or ""
    content = cfg.get("product_main") or ""
    duration = int(cfg.get("duration_sec") or 0)
    scriptStyle = cfg.get("script_style") or "story-telling"
    languageCode = cfg.get("speech_lang") or "vi"
    aspectRatio = cfg.get("ratio") or "9:16"
    voiceId = cfg.get("voice_id") or "ElevenLabs_VoiceID"
    imagesList = _images_refs(bool(models_json.strip()), product_count)

    return f"""
Objective: Create a detailed video script in JSON format. The output MUST be a valid JSON object with a "scenes" key containing an array of scene objects. The entire script, including all descriptions and voiceovers, MUST be in the language specified by the languageCode ({languageCode}).

Video Idea: {idea}
Core Content: {content}
Total Duration: Approximately {duration} seconds.
Script Style: {scriptStyle}
Visual Style: {visualStyleString}
Setting/Background Generation: You MUST invent a suitable and compelling setting/background for the video based on the idea, content, and characters. The setting must be consistent with the overall theme.
Models/Characters:
{_models_description(models_json)}

Reference Images:
{imagesList if imagesList else '- No reference images provided.'}

Task Instructions:
1.  Analyze all provided information.
2.  Break down the video into exactly {sceneCount} distinct scenes for the {duration}-second duration.
3.  For each scene, provide a concise description in the target language ({languageCode}).
4.  Create a separate voiceover field containing the dialogue/narration in the target language ({languageCode}). This field MUST include descriptive audio tags in square brackets to guide the text-to-speech model. The tags should also be in the target language if appropriate (e.g., for actions like [cười], [khóc]). This is a critical requirement.
    Available Audio Tags (Adapt these to the target language for the voiceover):
    {{
      "emotion_tags": {{"happy": "[vui vẻ]", "excited": "[hào hứng]", "sad": "[buồn bã]", "angry": "[tức giận]", "surprised": "[ngạc nhiên]", "disappointed": "[thất vọng]", "scared": "[sợ hãi]", "confident": "[tự tin]", "nervous": "[lo lắng]", "crying": "[khóc]", "laughs": "[cười]", "sighs": "[thở dài]"}},
      "tone_tags": {{"whispers": "[thì thầm]", "shouts": "[hét lên]", "sarcastic": "[mỉa mai]", "dramatic_tone": "[giọng kịch tính]", "reflective": "[suy tư]", "gentle_voice": "[giọng nhẹ nhàng]", "serious_tone": "[giọng nghiêm túc]"}},
      "style_tags": {{"storytelling": "[giọng kể chuyện]", "advertisement": "[giọng quảng cáo]"}},
      "timing_tags": {{"pause": "[ngừng lại]", "hesitates": "[do dự]", "rushed": "[vội vã]", "slows_down": "[chậm lại]"}},
      "action_tags": {{"clears_throat": "[hắng giọng]", "gasp": "[thở hổn hển]"}}
    }}
5.  The voicer field MUST be set to this exact value: {voiceId}.
6.  The languageCode field MUST be set to {languageCode}.
7.  Generate a detailed prompt object for a text-to-video AI model.
8.  The prompt.Output_Format.Structure must be filled with specific details (English):
    - character_details: reference image ('model-1') + EXACT clothing/hairstyle/gender from Models/Characters.
    - setting_details, key_action (may reference 'product-1'), camera_direction.
    - original_language_dialogue: copy top-level voiceover without audio tags (in {languageCode}).
    - dialogue_or_voiceover: English translation of the original dialogue.
9.  Audio tags appear ONLY in the top-level voiceover.
10. Output ONLY a valid JSON object. No extra text.

Output Format (Strictly Adhere):
{{
  "scenes": [
    {{
      "scene": 1,
      "description": "A short summary of the scene, in the target language.",
      "voiceover": "[emotion][pause] sample voiceover in target language.",
      "voicer": "{voiceId}",
      "languageCode": "{languageCode}",
      "prompt": {{
        "Objective": "Generate a short video clip for this scene.",
        "Persona": {{
          "Role": "Creative Video Director",
          "Tone": "Cinematic and evocative",
          "Knowledge_Level": "Expert in visual storytelling"
        }},
        "Task_Instructions": [
          "Create a video clip lasting approximately {{round({duration} / {sceneCount})}} seconds."
        ],
        "Constraints": [
          "Aspect ratio: {aspectRatio}",
          "Visual style: {visualStyleString}"
        ],
        "Input_Examples": [],
        "Output_Format": {{
          "Type": "JSON",
          "Structure": {{
            "character_details": "In English...",
            "setting_details": "In English...",
            "key_action": "In English...",
            "camera_direction": "In English...",
            "original_language_dialogue": "In {languageCode}, no audio tags.",
            "dialogue_or_voiceover": "In English translation."
          }}
        }}
      }}
    }}
  ]
}}
""".strip()

def _build_image_prompt(struct:Dict[str,Any], visualStyleString:str)->str:
    camera = (struct or {}).get("camera_direction","")
    setting = (struct or {}).get("setting_details","")
    character = (struct or {}).get("character_details","")
    action = (struct or {}).get("key_action","")
    return f"""Objective: Generate ONE SINGLE photorealistic, high-quality preview image for a video scene, meticulously following all instructions. The output MUST be a single, unified image.

--- SCENE COMPOSITION ---
- Overall Style: {visualStyleString}.
- Camera & Shot: {camera}.
- Setting: {setting}.
- Character & Clothing: {character}.
- Key Action: {action}.

--- ABSOLUTE, NON-NEGOTIABLE RULES ---
1. SINGLE IMAGE OUTPUT (CRITICAL): The output MUST be ONE single, coherent image. NO collages, grids, split-screens, or multi-panel images are allowed under any circumstances.
2. CHARACTER FIDELITY: The character's clothing, hairstyle, and gender MUST PERFECTLY and EXACTLY match the description provided in the scene composition. This OVERRIDES ALL other instructions.
3. NO TEXT OR WATERMARKS: The image MUST be 100% free of any text, letters, words, subtitles, captions, logos, watermarks, or any form of typography.

--- NEGATIVE PROMPT (Elements to strictly AVOID) ---
- collage, grid, multiple panels, multi-panel, split screen, diptych, triptych, multiple frames.
- text, words, letters, logos, watermarks, typography, signatures, labels, captions, subtitles.
- cartoon, illustration, drawing, sketch, anime, 3d render.
""".strip()

def _build_social_media_prompt(cfg: Dict[str, Any], outline_vi: str) -> str:
    """Build prompt for generating social media content"""
    platform = cfg.get("social_platform", "TikTok")
    language = cfg.get("speech_lang", "vi")
    product = cfg.get("product_main", "")
    idea = cfg.get("idea", "")
    
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