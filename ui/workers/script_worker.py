# ui/workers/script_worker.py - PATCH
"""
Enhanced error handling for script generation
Fix for Issue #7: Better error messages
"""

from PyQt5.QtCore import QThread, pyqtSignal
import traceback
import json

class ScriptWorker(QThread):
    progress = pyqtSignal(str)
    done = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.should_stop = False
    
    def run(self):
        try:
            from services import sales_script_service as sscript
            
            self.progress.emit("Đang kết nối với AI...")
            
            # Generate script
            outline = sscript.generate_script(self.config)
            
            if self.should_stop:
                return
            
            self.progress.emit("✓ Kịch bản đã được tạo")
            self.done.emit(outline)
            
        except ValueError as e:
            # Specific error handling for JSON issues
            error_msg = str(e)
            
            if "Failed to parse JSON" in error_msg:
                # Issue #7: JSON parsing failed
                self.progress.emit("❌ Lỗi phân tích dữ liệu từ AI")
                
                detailed_error = (
                    "JSONDecodeError: Không thể đọc kịch bản từ AI\n\n"
                    "Nguyên nhân có thể:\n"
                    "• AI trả về dữ liệu không đúng định dạng\n"
                    "• Kịch bản quá dài hoặc phức tạp\n"
                    "• Có ký tự đặc biệt trong nội dung\n\n"
                    "Giải pháp:\n"
                    "1. Thử viết lại kịch bản với nội dung ngắn gọn hơn\n"
                    "2. Kiểm tra API key còn hoạt động\n"
                    "3. Thử đổi model (Gemini ↔ ChatGPT)\n\n"
                    f"Chi tiết kỹ thuật: {error_msg}"
                )
                
                self.error.emit(detailed_error)
            else:
                self.progress.emit(f"❌ {error_msg}")
                self.error.emit(error_msg)
        
        except json.JSONDecodeError as e:
            # Direct JSON error (shouldn't happen with safe parser, but just in case)
            self.progress.emit("❌ Lỗi JSON")
            
            error_details = (
                f"JSONDecodeError at line {e.lineno}, column {e.colno}\n\n"
                f"This error occurred while parsing the AI response.\n"
                f"The response may contain invalid JSON syntax.\n\n"
                f"Technical details:\n"
                f"Position: {e.pos}\n"
                f"Message: {e.msg}\n\n"
                f"Please try again or contact support if the issue persists."
            )
            
            self.error.emit(error_details)
        
        except Exception as e:
            # Generic error
            self.progress.emit(f"❌ Lỗi: {str(e)}")
            
            # Get full traceback for logging
            tb = traceback.format_exc()
            print(f"ScriptWorker error:\n{tb}")
            
            self.error.emit(f"Lỗi không xác định: {str(e)}\n\nCheck console for details.")
    
    def stop(self):
        self.should_stop = True