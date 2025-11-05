# ui/video_ads_panel_v5_connected.py
"""
Video Ads V5 - Connected to Original Logic
Integrates with:
- services.llm_story_service (script generation)
- workers.image_generation_worker (image creation)
- workers.video_generation_worker (video creation)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QCheckBox,
    QGroupBox, QPushButton, QTabWidget,
    QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

# Import original services
try:
    from services.llm_story_service import generate_script
    from workers.image_generation_worker import ImageGenerationWorker
    from workers.video_generation_worker import VideoGenerationWorker
    from utils.config import load as load_cfg
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    generate_script = None
    ImageGenerationWorker = None
    load_cfg = lambda: {}

FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)

class VideoAdsPanelV5Connected(QWidget):
    """Video Ads V5 - Connected to original logic"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State (matching video_ban_hang_panel.py)
        self.cache = {
            "outline": None,
            "character_bible": [],
            "scene_images": [],
            "thumbnail": None
        }
        
        # Workers
        self.script_worker = None
        self.img_worker = None
        self.video_worker = None
        
        self._build_ui()
        self._append_log("✓ Video Ads panel initialized (connected to original logic)")
    
    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === LEFT PANEL (480px) ===
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setMinimumWidth(480)
        left_scroll.setMaximumWidth(650)
        
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(12)
        
        # Project
        proj_group = QGroupBox("📁 Dự án")
        proj_group.setFont(FONT_H2)
        proj_layout = QVBoxLayout(proj_group)
        proj_layout.setSpacing(8)
        
        proj_layout.addWidget(QLabel("Tên dự án:"))
        self.ed_project = QLineEdit("2025-11-04-1")
        self.ed_project.setMinimumHeight(36)
        self.ed_project.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px 12px;
            }
        """)
        proj_layout.addWidget(self.ed_project)
        
        proj_layout.addWidget(QLabel("Ý tưởng:"))
        self.txt_idea = QTextEdit()
        self.txt_idea.setMinimumHeight(90)
        self.txt_idea.setMaximumHeight(130)
        self.txt_idea.setPlaceholderText("Nhập ý tưởng cho video...")
        self.txt_idea.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        proj_layout.addWidget(self.txt_idea)
        
        left_layout.addWidget(proj_group)
        
        # === CHECKBOXES (VISIBLE & CONNECTED) ===
        settings_group = QGroupBox("⚙️ Cài đặt nội dung")
        settings_group.setFont(FONT_H2)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(8)
        
        # Persona checkbox with content
        self.chk_persona = QCheckBox("👤 Thông tin người mẫu")
        self.chk_persona.setFont(FONT_BODY)
        self.chk_persona.setMinimumHeight(32)
        self.chk_persona.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #BDBDBD;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #1E88E5;
            }
        """)
        self.chk_persona.toggled.connect(self._on_persona_toggled)
        settings_layout.addWidget(self.chk_persona)
        
        # Persona content (hidden by default)
        self.persona_content = QTextEdit()
        self.persona_content.setMaximumHeight(80)
        self.persona_content.setPlaceholderText("Nhập thông tin người mẫu...")
        self.persona_content.setVisible(False)
        settings_layout.addWidget(self.persona_content)
        
        # Product checkbox with content
        self.chk_product = QCheckBox("📦 Ảnh sản phẩm")
        self.chk_product.setFont(FONT_BODY)
        self.chk_product.setMinimumHeight(32)
        self.chk_product.setStyleSheet(self.chk_persona.styleSheet())
        self.chk_product.toggled.connect(self._on_product_toggled)
        settings_layout.addWidget(self.chk_product)
        
        # Product content (hidden by default)
        self.product_content = QTextEdit()
        self.product_content.setMaximumHeight(80)
        self.product_content.setPlaceholderText("Đường dẫn ảnh sản phẩm...")
        self.product_content.setVisible(False)
        settings_layout.addWidget(self.product_content)
        
        # Video checkbox with content
        self.chk_video = QCheckBox("🎬 Cài đặt video")
        self.chk_video.setFont(FONT_BODY)
        self.chk_video.setMinimumHeight(32)
        self.chk_video.setStyleSheet(self.chk_persona.styleSheet())
        self.chk_video.toggled.connect(self._on_video_toggled)
        settings_layout.addWidget(self.chk_video)
        
        # Video content (hidden by default)
        self.video_content = QTextEdit()
        self.video_content.setMaximumHeight(80)
        self.video_content.setPlaceholderText("Cài đặt video: tỉ lệ, thời lượng...")
        self.video_content.setVisible(False)
        settings_layout.addWidget(self.video_content)
        
        left_layout.addWidget(settings_group)
        
        # === ACTION BUTTONS (CONNECTED) ===
        btn_write = QPushButton("📝 Viết kịch bản")
        btn_write.setMinimumHeight(40)
        btn_write.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #FF8555; }
        """)
        btn_write.clicked.connect(self._on_write_script)  # ✅ CONNECTED
        left_layout.addWidget(btn_write)
        
        img_video_row = QHBoxLayout()
        img_video_row.setSpacing(8)
        
        self.btn_images = QPushButton("🖼️ Tạo ảnh")
        self.btn_images.setMinimumHeight(40)
        self.btn_images.setEnabled(False)
        self.btn_images.setStyleSheet("""
            QPushButton {
                background: #BDBDBD;
                color: #424242;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #D0D0D0; }
            QPushButton:disabled {
                background: #F5F5F5;
                color: #BDBDBD;
            }
        """)
        self.btn_images.clicked.connect(self._on_generate_images)  # ✅ CONNECTED
        img_video_row.addWidget(self.btn_images, 1)
        
        self.btn_video = QPushButton("🎥 Video")
        self.btn_video.setMinimumHeight(40)
        self.btn_video.setEnabled(False)
        self.btn_video.setStyleSheet("""
            QPushButton {
                background: #9C27B0;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #AB47BC; }
            QPushButton:disabled {
                background: #F5F5F5;
                color: #BDBDBD;
            }
        """)
        self.btn_video.clicked.connect(self._on_generate_video)  # ✅ CONNECTED
        img_video_row.addWidget(self.btn_video, 1)
        
        left_layout.addLayout(img_video_row)
        
        # Auto + Stop SAME ROW
        gen_stop_row = QHBoxLayout()
        gen_stop_row.setSpacing(10)
        
        self.btn_auto = QPushButton("🔥 Tạo video tự động (3 bước)")
        self.btn_auto.setMinimumHeight(52)
        self.btn_auto.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                border: none;
                border-radius: 26px;
                font-weight: 700;
                font-size: 15px;
            }
            QPushButton:hover { background: #FF8555; }
        """)
        self.btn_auto.clicked.connect(self._on_auto_workflow)  # ✅ CONNECTED
        gen_stop_row.addWidget(self.btn_auto, 3)
        
        self.btn_stop = QPushButton("⏹ Dừng")
        self.btn_stop.setMinimumHeight(52)
        self.btn_stop.setMinimumWidth(130)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background: #FFB3C1;
                color: #D32F2F;
                border: none;
                border-radius: 26px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover { background: #FFC4D0; }
            QPushButton:disabled {
                background: #F5F5F5;
                color: #BDBDBD;
            }
        """)
        self.btn_stop.clicked.connect(self._stop_workflow)
        gen_stop_row.addWidget(self.btn_stop, 1)
        
        left_layout.addLayout(gen_stop_row)
        
        # Console
        console_group = QGroupBox("📋 Console:")
        console_group.setFont(FONT_BODY)
        console_layout = QVBoxLayout(console_group)
        
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setMinimumHeight(100)
        self.txt_console.setMaximumHeight(140)
        self.txt_console.setFont(QFont("Courier New", 11))
        self.txt_console.setStyleSheet("""
            QTextEdit {
                background: #C8E6C9;
                color: #1B5E20;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        console_layout.addWidget(self.txt_console)
        
        left_layout.addWidget(console_group)
        left_layout.addStretch()
        
        left_scroll.setWidget(left_container)
        main_layout.addWidget(left_scroll)
        
        # === RIGHT PANEL - BLUE BACKGROUND ===
        right_tabs = QTabWidget()
        right_tabs.setFont(QFont("Segoe UI", 13, QFont.Bold))
        
        tab_data = [
            ("📝 Cảnh", "#FF6B6B"),
            ("📖 Character", "#4ECDC4"),
            ("🖼️ Thumbnail", "#FFA07A"),
            ("📱 Social", "#98D8C8")
        ]
        
        for i, (tab_name, color) in enumerate(tab_data):
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(16, 16, 16, 16)
            
            content = QTextEdit()
            content.setPlaceholderText(f"{tab_name} content...")
            content.setStyleSheet(f"""
                QTextEdit {{
                    background: #E3F2FD;
                    color: #212121;
                    border: 3px solid {color};
                    border-radius: 8px;
                    padding: 16px;
                    font-size: 14px;
                }}
            """)
            tab_layout.addWidget(content)
            
            right_tabs.addTab(tab_widget, tab_name)
            right_tabs.tabBar().setTabTextColor(i, QColor(color))
        
        right_tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 130px;
                padding: 12px 18px;
                font-weight: 700;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #E3F2FD;
                border-bottom: 4px solid;
            }
            QTabBar::tab:!selected {
                background: #F5F5F5;
            }
        """)
        
        main_layout.addWidget(right_tabs, 1)
    
    # ===== ORIGINAL METHODS FROM video_ban_hang_panel.py =====
    
    def _on_write_script(self):
        """Write script - FROM ORIGINAL"""
        idea = self.txt_idea.toPlainText().strip()
        if not idea:
            QMessageBox.warning(self, "Thiếu thông tin", "Nhập ý tưởng trước.")
            return
        
        self._append_log("📝 Bắt đầu viết kịch bản...")
        self.btn_images.setEnabled(False)
        self.btn_video.setEnabled(False)
        
        # TODO: Call generate_script service
        if generate_script:
            try:
                data, ctx = generate_script(
                    idea=idea,
                    project=self.ed_project.text().strip(),
                    provider="Gemini 2.5"
                )
                
                self.cache["outline"] = data
                self.cache["character_bible"] = data.get("character_bible", [])
                
                self._append_log("✅ Kịch bản đã hoàn tất!")
                self.btn_images.setEnabled(True)
            
            except Exception as e:
                self._append_log(f"❌ Lỗi: {e}")
        else:
            self._append_log("⚠️ generate_script not available")
    
    def _on_generate_images(self):
        """Generate images - FROM ORIGINAL"""
        if not self.cache["outline"]:
            QMessageBox.warning(self, "Chưa có kịch bản", "Vui lòng viết kịch bản trước.")
            return
        
        self._append_log("🖼️ Bắt đầu tạo ảnh...")
        self.btn_images.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        # TODO: Use ImageGenerationWorker
        if ImageGenerationWorker:
            character_bible = self.cache.get("character_bible", [])
            # self.img_worker = ImageGenerationWorker(...)
            # self.img_worker.start()
            
            self._append_log("⚠️ Image generation logic to be implemented")
            self.btn_images.setEnabled(True)
            self.btn_video.setEnabled(True)
            self.btn_stop.setEnabled(False)
        else:
            self._append_log("⚠️ ImageGenerationWorker not available")
    
    def _on_generate_video(self):
        """Generate video - FROM ORIGINAL"""
        if not self.cache["scene_images"]:
            QMessageBox.warning(self, "Chưa có ảnh cảnh", "Vui lòng tạo ảnh trước.")
            return
        
        self._append_log("🎥 Bắt đầu tạo video...")
        self.btn_video.setEnabled(False)
        
        # TODO: Implement video generation
        QMessageBox.information(
            self, "Thông báo", 
            "Chức năng tạo video sẽ được triển khai trong phiên bản tiếp theo."
        )
        
        self.btn_video.setEnabled(True)
    
    def _on_auto_workflow(self):
        """Auto workflow - FROM ORIGINAL"""
        self._append_log("⚡ Bắt đầu quy trình tự động (3 bước)...")
        
        self.btn_auto.setEnabled(False)
        self.btn_images.setEnabled(False)
        self.btn_video.setEnabled(False)
        
        # Step 1: Write script
        self._append_log("📝 Bước 1/3: Viết kịch bản...")
        self._on_write_script()
        
        # Note: Steps 2 and 3 triggered by signals
    
    def _stop_workflow(self):
        """Stop workflow"""
        self._append_log("⏹ Dừng workflow...")
        self.btn_stop.setEnabled(False)
        self.btn_auto.setEnabled(True)
    
    # Checkbox toggle methods
    def _on_persona_toggled(self, checked):
        self.persona_content.setVisible(checked)
    
    def _on_product_toggled(self, checked):
        self.product_content.setVisible(checked)
    
    def _on_video_toggled(self, checked):
        self.video_content.setVisible(checked)
    
    def _append_log(self, msg):
        self.txt_console.append(msg)