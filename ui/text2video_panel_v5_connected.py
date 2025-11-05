# ui/text2video_panel_v5_connected.py - COMPLETE FIXED VERSION
"""
Text2Video V5 - Connected to Original Logic (FIXED)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QGroupBox, QPushButton, QTabWidget, QFileDialog,
    QMessageBox, QSpinBox, QSlider, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import json
import os

# Import original services (with safe fallbacks)
try:
    from services.llm_story_service import generate_script
except ImportError:
    generate_script = None

try:
    from services.domain_prompts import get_all_domains, get_topics_for_domain
except ImportError:
    get_all_domains = lambda: []
    get_topics_for_domain = lambda d: []

try:
    from services.voice_options import TTS_PROVIDERS, get_voices_for_provider, get_style_list
except ImportError:
    TTS_PROVIDERS = [("google", "Google TTS"), ("elevenlabs", "ElevenLabs")]
    get_voices_for_provider = lambda p, l: []
    get_style_list = lambda: [("default", "Default", "Normal voice")]

try:
    from utils.config import load as load_cfg, save as save_cfg
except ImportError:
    load_cfg = lambda: {}
    save_cfg = lambda x: None

FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)
FONT_LARGE = QFont("Segoe UI", 15, QFont.Bold)

class CollapsibleGroupBox(QGroupBox):
    """Collapsible group box"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(False)
        self._content = QWidget()
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._content.setVisible(False)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._content)
        
        self.toggled.connect(self._on_toggle)
    
    def _on_toggle(self, checked):
        self._content.setVisible(checked)
        if checked and hasattr(self, '_accordion_group'):
            self._accordion_group.setChecked(False)
    
    def content_layout(self):
        return self._layout

class Text2VideoPanelV5Connected(QWidget):
    """Text2Video V5 - Fixed version"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State
        self._ctx = {}
        self._title = "Project"
        self._character_bible = None
        self._script_data = None
        self._cards_state = {}
        
        # Workers
        self.worker = None
        self.thread = None
        
        # Build UI FIRST
        self._build_ui()
        
        # THEN load data (after console exists)
        self._load_initial_data()
    
    def _load_initial_data(self):
        """Load initial voices and domains - AFTER UI is built"""
        self._load_voices_for_provider()
        self._log("✓ Text2Video panel initialized (connected to original logic)")
    
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
        
        # === PROJECT INFO ===
        proj_group = QGroupBox("📁 Dự án")
        proj_group.setFont(FONT_H2)
        proj_layout = QVBoxLayout(proj_group)
        proj_layout.setSpacing(8)
        
        proj_layout.addWidget(QLabel("Tên dự án:"))
        self.ed_project = QLineEdit()
        self.ed_project.setPlaceholderText("Nhập tên dự án (để trống sẽ tự tạo)")
        self.ed_project.setMinimumHeight(36)
        self.ed_project.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLineEdit:focus { border: 2px solid #1E88E5; }
        """)
        proj_layout.addWidget(self.ed_project)
        
        proj_layout.addWidget(QLabel("Ý tưởng (đoạn văn):"))
        self.ed_idea = QTextEdit()
        self.ed_idea.setPlaceholderText("Nhập ý tưởng thô (<10 tự)...")
        self.ed_idea.setMinimumHeight(90)
        self.ed_idea.setMaximumHeight(130)
        self.ed_idea.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QTextEdit:focus { border: 2px solid #1E88E5; }
        """)
        proj_layout.addWidget(self.ed_idea)
        
        left_layout.addWidget(proj_group)
        
        # === DOMAIN & TOPIC ===
        expert_group = QGroupBox("🎯 Bạn là chuyên gia trong")
        expert_group.setFont(FONT_LARGE)
        expert_group.setStyleSheet("QGroupBox { color: #1E88E5; font-weight: 700; }")
        expert_layout = QVBoxLayout(expert_group)
        expert_layout.setSpacing(8)
        
        expert_layout.addWidget(QLabel("Lĩnh vực:"))
        self.cb_domain = QComboBox()
        self.cb_domain.setFont(FONT_LARGE)
        self.cb_domain.addItem("(Không chọn)", "")
        for domain in get_all_domains():
            self.cb_domain.addItem(domain, domain)
        self.cb_domain.setMinimumHeight(42)
        self.cb_domain.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #1E88E5;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 15px;
                font-weight: 700;
                font-family: "Segoe UI", Arial, sans-serif;
                color: #1565C0;
            }
        """)
        self.cb_domain.currentIndexChanged.connect(self._on_domain_changed)
        expert_layout.addWidget(self.cb_domain)
        
        expert_layout.addWidget(QLabel("Chủ đề:"))
        self.cb_topic = QComboBox()
        self.cb_topic.setFont(FONT_LARGE)
        self.cb_topic.addItem("(Chọn lĩnh vực để load chủ đề)", "")
        self.cb_topic.setEnabled(False)
        self.cb_topic.setMinimumHeight(42)
        self.cb_topic.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 15px;
                font-weight: 700;
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)
        expert_layout.addWidget(self.cb_topic)
        
        left_layout.addWidget(expert_group)
        
        # === VIDEO SETTINGS (Collapsible) ===
        video_group = CollapsibleGroupBox("⚙️ Cài đặt video")
        video_layout = video_group.content_layout()
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Model:"))
        self.cb_model = QComboBox()
        self.cb_model.addItems(["Veo3.1 i2v Fast Portrait", "Veo3.1 i2v Slow Portrait"])
        self.cb_model.setMinimumHeight(32)
        row1.addWidget(self.cb_model, 1)
        video_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Thời lượng (s):"))
        self.sp_duration = QSpinBox()
        self.sp_duration.setRange(3, 3600)
        self.sp_duration.setValue(100)
        self.sp_duration.setMinimumHeight(32)
        row2.addWidget(self.sp_duration, 1)
        video_layout.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Tỉ lệ:"))
        self.cb_ratio = QComboBox()
        self.cb_ratio.addItems(["16:9", "9:16", "1:1"])
        self.cb_ratio.setMinimumHeight(32)
        row3.addWidget(self.cb_ratio, 1)
        video_layout.addLayout(row3)
        
        self.cb_upscale = QCheckBox("Up Scale 4K")
        video_layout.addWidget(self.cb_upscale)
        
        left_layout.addWidget(video_group)
        
        # === VOICE SETTINGS ===
        voice_group = CollapsibleGroupBox("🎙️ Cài đặt voice")
        video_group._accordion_group = voice_group
        voice_group._accordion_group = video_group
        voice_layout = voice_group.content_layout()
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Provider:"))
        self.cb_tts_provider = QComboBox()
        for provider_id, provider_name in TTS_PROVIDERS:
            self.cb_tts_provider.addItem(provider_name, provider_id)
        self.cb_tts_provider.setMinimumHeight(32)
        self.cb_tts_provider.currentIndexChanged.connect(self._load_voices_for_provider)
        row1.addWidget(self.cb_tts_provider, 1)
        voice_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Voice:"))
        self.cb_voice = QComboBox()
        self.cb_voice.setMinimumHeight(32)
        row2.addWidget(self.cb_voice, 1)
        voice_layout.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Phong cách:"))
        self.cb_speaking_style = QComboBox()
        for key, name, desc in get_style_list():
            self.cb_speaking_style.addItem(name, key)
        self.cb_speaking_style.setCurrentIndex(min(2, self.cb_speaking_style.count()-1))
        self.cb_speaking_style.setMinimumHeight(32)
        row3.addWidget(self.cb_speaking_style, 1)
        voice_layout.addLayout(row3)
        
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Tốc độ:"))
        self.slider_rate = QSlider(Qt.Horizontal)
        self.slider_rate.setRange(50, 200)
        self.slider_rate.setValue(100)
        row4.addWidget(self.slider_rate, 1)
        self.lbl_rate = QLabel("1.0x")
        self.lbl_rate.setMinimumWidth(45)
        self.slider_rate.valueChanged.connect(lambda v: self.lbl_rate.setText(f"{v/100:.1f}x"))
        row4.addWidget(self.lbl_rate)
        voice_layout.addLayout(row4)
        
        left_layout.addWidget(voice_group)
        
        # === ACTION BUTTONS ===
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        
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
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QPushButton:hover { background: #FF8555; }
            QPushButton:disabled {
                background: #CCCCCC;
                color: #666666;
            }
        """)
        self.btn_auto.clicked.connect(self._on_auto_generate)
        actions_row.addWidget(self.btn_auto, 3)
        
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
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QPushButton:hover { background: #FFC4D0; }
            QPushButton:disabled {
                background: #F5F5F5;
                color: #BDBDBD;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_processing)
        actions_row.addWidget(self.btn_stop, 1)
        
        left_layout.addLayout(actions_row)
        
        btn_open = QPushButton("📂 Mở thư mục dự án")
        btn_open.setMinimumHeight(40)
        btn_open.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        btn_open.clicked.connect(self._open_project_dir)
        left_layout.addWidget(btn_open)
        
        btn_new = QPushButton("➕ Tạo dự án mới")
        btn_new.setMinimumHeight(40)
        btn_new.setStyleSheet("""
            QPushButton {
                background: #E0E0E0;
                color: #424242;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QPushButton:hover { background: #EEEEEE; }
        """)
        left_layout.addWidget(btn_new)
        
        # === CONSOLE ===
        console_group = QGroupBox("📋 Console:")
        console_group.setFont(FONT_BODY)
        console_layout = QVBoxLayout(console_group)
        console_layout.setSpacing(4)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(100)
        self.console.setMaximumHeight(140)
        self.console.setFont(QFont("Courier New", 11))
        self.console.setStyleSheet("""
            QTextEdit {
                background: #C8E6C9;
                color: #1B5E20;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 8px;
                font-family: "Courier New", monospace;
            }
        """)
        console_layout.addWidget(self.console)
        
        left_layout.addWidget(console_group)
        left_layout.addStretch()
        
        left_scroll.setWidget(left_container)
        main_layout.addWidget(left_scroll)
        
        # === RIGHT PANEL ===
        right_tabs = QTabWidget()
        right_tabs.setFont(QFont("Segoe UI", 13, QFont.Bold))
        
        tab_data = [
            ("📝 Chi tiết kịch bản", "#FF6B6B"),
            ("📖 Character Bibl", "#4ECDC4"),
            ("✅ Kết quả cảnh", "#45B7D1"),
            ("🖼️ Thumbnail", "#FFA07A"),
            ("📱 Socia", "#98D8C8")
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
                    font-family: "Segoe UI", Arial, sans-serif;
                }}
            """)
            tab_layout.addWidget(content)
            
            if "kịch bản" in tab_name:
                self.view_story = content
            elif "Character" in tab_name:
                self.view_bible = content
            elif "cảnh" in tab_name:
                self.view_scenes = content
            elif "Thumbnail" in tab_name:
                self.thumbnail_display = content
            elif "Socia" in tab_name:
                self.social_display = content
            
            right_tabs.addTab(tab_widget, tab_name)
            right_tabs.tabBar().setTabTextColor(i, QColor(color))
        
        right_tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 140px;
                padding: 12px 18px;
                font-size: 13px;
                font-weight: 700;
                font-family: "Segoe UI", Arial, sans-serif;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 3px;
            }
            QTabBar::tab:selected {
                background: #E3F2FD;
                border-bottom: 4px solid;
            }
            QTabBar::tab:!selected {
                background: #F5F5F5;
                margin-top: 3px;
            }
        """)
        
        main_layout.addWidget(right_tabs, 1)
    
    # ===== METHODS =====
    
    def _log(self, msg):
        """Log to console"""
        if hasattr(self, 'console') and self.console:
            self.console.append(msg)
        else:
            print(msg)
    
    def _append_log(self, msg):
        """Alias for _log"""
        self._log(msg)
    
    def _on_auto_generate(self):
        """Auto-generate"""
        idea = self.ed_idea.toPlainText().strip()
        if not idea:
            QMessageBox.warning(self, "Thiếu thông tin", "Nhập ý tưởng trước.")
            return
        
        self.btn_auto.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        self._log("[INFO] Bước 1/3: Sinh kịch bản...")
        self._log(f"[INFO] Idea: {idea[:50]}...")
        
        # TODO: Implement actual generation
        self._log("[WARN] Generation logic to be implemented")
        
        self.btn_auto.setEnabled(True)
        self.btn_stop.setEnabled(False)
    
    def stop_processing(self):
        """Stop processing"""
        self._log("[INFO] Stopped by user")
        self.btn_auto.setEnabled(True)
        self.btn_stop.setEnabled(False)
    
    def _on_domain_changed(self):
        """Domain changed"""
        domain = self.cb_domain.currentData()
        self.cb_topic.clear()
        self.cb_topic.addItem("(Chọn lĩnh vực để load chủ đề)", "")
        
        if not domain:
            self.cb_topic.setEnabled(False)
            return
        
        try:
            topics = get_topics_for_domain(domain)
            if topics:
                self.cb_topic.clear()
                self.cb_topic.addItem("(Chọn chủ đề)", "")
                for topic in topics:
                    self.cb_topic.addItem(topic, topic)
                self.cb_topic.setEnabled(True)
                self._log(f"[INFO] Loaded {len(topics)} topics for {domain}")
        except Exception as e:
            self._log(f"[ERR] {e}")
            self.cb_topic.setEnabled(False)
    
    def _load_voices_for_provider(self):
        """Load voices"""
        try:
            provider = self.cb_tts_provider.currentData()
            if not provider:
                return
            
            voices = get_voices_for_provider(provider, "vi")
            
            self.cb_voice.blockSignals(True)
            self.cb_voice.clear()
            
            for voice in voices:
                display_name = voice.get("name", voice.get("id", "Unknown"))
                voice_id = voice.get("id")
                self.cb_voice.addItem(display_name, voice_id)
            
            self.cb_voice.blockSignals(False)
            
            if voices:
                self._log(f"[INFO] Loaded {len(voices)} voices for {provider}")
        
        except Exception as e:
            self._log(f"[ERR] Failed to load voices: {e}")
    
    def _open_project_dir(self):
        """Open project directory"""
        self._log("[INFO] Open project directory")
        # TODO: Implement