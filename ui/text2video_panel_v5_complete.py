# ui/text2video_panel_v5_complete.py
"""
Text2Video V5 - Complete Implementation
- Ocean blue tab colors (#00ACC1)
- Bold labels (15px)
- 6-line text area
- 2 fields per row
- Custom Voice ID
- Full original logic from text2video_panel.py
Author: chamnv-dev
Date: 2025-01-05
"""

import json
import os
import re

from PyQt5.Qt import QDesktopServices
from PyQt5.QtCore import QLocale, QSize, Qt, QThread, QUrl
from PyQt5.QtGui import QColor, QFont, QKeySequence, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QScrollArea, QCheckBox, QComboBox, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QPushButton, QShortcut, QSlider, QSpinBox, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget, QTabWidget,
    QFileDialog, QFrame
)

# Original imports
try:
    from utils import config as cfg
    from services.voice_options import (
        get_style_list, get_style_info, get_voices_for_provider,
        SPEAKING_STYLES, TTS_PROVIDERS
    )
    from services.domain_prompts import (
        get_all_domains, get_topics_for_domain, get_system_prompt
    )
    from services.llm_story_service import (
        generate_social_media, generate_thumbnail_design
    )
    from ui.text2video_panel_impl import (
        _ASPECT_MAP, _LANGS, _VIDEO_MODELS, _Worker,
        build_prompt_json, get_model_key_from_display, extract_location_context
    )
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    cfg = None
    TTS_PROVIDERS = [("google", "Google TTS")]
    _LANGS = [("Tiếng Việt", "vi"), ("English", "en")]
    _ASPECT_MAP = {"16:9": "VIDEO_ASPECT_RATIO_LANDSCAPE"}

# V5 STYLING
FONT_H2 = QFont("Segoe UI", 15, QFont.Bold)  # +2px, bold
FONT_BODY = QFont("Segoe UI", 13)

class CollapsibleGroupBox(QGroupBox):
    """Collapsible group box"""
    def __init__(self, title="", parent=None, accordion_group=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self._accordion_group = accordion_group
        
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(10, 5, 10, 5)
        self._content_layout.setSpacing(6)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 8, 0, 0)
        main_layout.addWidget(self._content_widget)
        
        self.blockSignals(True)
        self._content_widget.setVisible(False)
        self.setChecked(False)
        self.blockSignals(False)
        
        self.toggled.connect(self._on_toggle)
    
    def content_layout(self):
        return self._content_layout
    
    def _on_toggle(self, checked):
        self._content_widget.setVisible(checked)
        if checked and self._accordion_group:
            self._accordion_group.setChecked(False)

class Text2VideoPanelV5(QWidget):
    """Text2Video V5 - Complete with full original logic"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State (from original)
        self._cards_state = {}
        self._ctx = {}
        self._title = "Project"
        self._character_bible = None
        self._script_data = None
        self.worker = None
        self.thread = None
        
        self._build_ui()
        self._apply_styles()
        self._update_folder_label()
    
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(8, 8, 8, 8)
        self.setMinimumWidth(1000)
        
        # === LEFT COLUMN (1/3) ===
        colL = QVBoxLayout()
        colL.setSpacing(8)
        
        # PROJECT INFO
        project_group = QGroupBox("📋 Dự án")
        project_layout = QVBoxLayout(project_group)
        project_layout.setContentsMargins(10, 15, 10, 8)
        project_layout.setSpacing(6)
        
        lbl = QLabel("Tên dự án:")
        lbl.setFont(FONT_H2)
        project_layout.addWidget(lbl)
        
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
            }
            QLineEdit:focus { border: 2px solid #1E88E5; }
        """)
        project_layout.addWidget(self.ed_project)
        
        lbl = QLabel("Ý tưởng (đoạn văn):")
        lbl.setFont(FONT_H2)
        project_layout.addWidget(lbl)
        
        self.ed_idea = QTextEdit()
        self.ed_idea.setAcceptRichText(False)
        self.ed_idea.setLocale(QLocale(QLocale.Vietnamese, QLocale.Vietnam))
        self.ed_idea.setPlaceholderText("Nhập ý tưởng thô (<10 từ)…")
        self.ed_idea.setMinimumHeight(150)  # 6 lines
        self.ed_idea.setMaximumHeight(180)
        self.ed_idea.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QTextEdit:focus { border: 2px solid #1E88E5; }
        """)
        project_layout.addWidget(self.ed_idea)
        
        # Domain/Topic
        row_d = QHBoxLayout()
        lbl = QLabel("Lĩnh vực:")
        lbl.setFont(FONT_H2)
        row_d.addWidget(lbl)
        self.cb_domain = QComboBox()
        self.cb_domain.setMinimumHeight(32)
        self.cb_domain.addItem("(Không chọn)", "")
        if get_all_domains:
            for domain in get_all_domains():
                self.cb_domain.addItem(domain, domain)
        row_d.addWidget(self.cb_domain, 1)
        project_layout.addLayout(row_d)
        
        row_t = QHBoxLayout()
        lbl = QLabel("Chủ đề:")
        lbl.setFont(FONT_H2)
        row_t.addWidget(lbl)
        self.cb_topic = QComboBox()
        self.cb_topic.setMinimumHeight(32)
        self.cb_topic.addItem("(Chọn lĩnh vực để load chủ đề)", "")
        self.cb_topic.setEnabled(False)
        row_t.addWidget(self.cb_topic, 1)
        project_layout.addLayout(row_t)
        
        colL.addWidget(project_group)
        
        # VIDEO SETTINGS
        video_group = CollapsibleGroupBox("⚙️ Cài đặt video")
        video_group.setFont(FONT_H2)
        video_layout = video_group.content_layout()
        
        # Row 1: Style + Model
        row1 = QHBoxLayout()
        lbl = QLabel("Phong cách:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row1.addWidget(lbl)
        self.cb_style = QComboBox()
        self.cb_style.setMinimumHeight(32)
        self.cb_style.addItems([
            "Điện ảnh (Cinematic)", "Anime", "Tài liệu",
            "Quay thực", "3D/CGI", "Stop-motion"
        ])
        row1.addWidget(self.cb_style, 1)
        
        row1.addSpacing(12)
        lbl = QLabel("Model:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row1.addWidget(lbl)
        self.cb_model = QComboBox()
        self.cb_model.setMinimumHeight(32)
        self.cb_model.addItems([
            "Veo3.1 i2v Fast Portrait",
            "Veo3.1 i2v Fast Landscape",
            "Veo3.1 i2v Slow Portrait",
            "Veo3.1 i2v Slow Landscape",
            "Veo2 General",
            "Veo2 i2v"
        ])
        row1.addWidget(self.cb_model, 1)
        video_layout.addLayout(row1)
        
        # Row 2: Duration + Videos per scene
        row2 = QHBoxLayout()
        lbl = QLabel("Thời lượng (s):")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row2.addWidget(lbl)
        self.sp_duration = QSpinBox()
        self.sp_duration.setMinimumHeight(32)
        self.sp_duration.setRange(3, 3600)
        self.sp_duration.setValue(100)
        row2.addWidget(self.sp_duration, 1)
        
        row2.addSpacing(12)
        lbl = QLabel("Số video/cảnh:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row2.addWidget(lbl)
        self.sp_copies = QSpinBox()
        self.sp_copies.setMinimumHeight(32)
        self.sp_copies.setRange(1, 5)
        self.sp_copies.setValue(1)
        row2.addWidget(self.sp_copies, 1)
        video_layout.addLayout(row2)
        
        # Row 3: Ratio + Language
        row3 = QHBoxLayout()
        lbl = QLabel("Tỉ lệ:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row3.addWidget(lbl)
        self.cb_ratio = QComboBox()
        self.cb_ratio.setMinimumHeight(32)
        self.cb_ratio.addItems(["16:9", "9:16", "1:1", "4:5", "21:9"])
        row3.addWidget(self.cb_ratio, 1)
        
        row3.addSpacing(12)
        lbl = QLabel("Ngôn ngữ:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row3.addWidget(lbl)
        self.cb_out_lang = QComboBox()
        self.cb_out_lang.setMinimumHeight(32)
        for name, code in _LANGS:
            self.cb_out_lang.addItem(name, code)
        row3.addWidget(self.cb_out_lang, 1)
        video_layout.addLayout(row3)
        
        # Row 4: Upscale
        self.cb_upscale = QCheckBox("Up Scale 4K")
        video_layout.addWidget(self.cb_upscale)
        
        colL.addWidget(video_group)
        
        # VOICE SETTINGS
        voice_group = CollapsibleGroupBox("🎙️ Cài đặt voice")
        voice_group.setFont(FONT_H2)
        video_group._accordion_group = voice_group
        voice_group._accordion_group = video_group
        voice_layout = voice_group.content_layout()
        
        # Row 1: Provider + Voice
        row1 = QHBoxLayout()
        lbl = QLabel("Provider:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row1.addWidget(lbl)
        self.cb_tts_provider = QComboBox()
        self.cb_tts_provider.setMinimumHeight(32)
        for pid, pname in TTS_PROVIDERS:
            self.cb_tts_provider.addItem(pname, pid)
        row1.addWidget(self.cb_tts_provider, 1)
        
        row1.addSpacing(12)
        lbl = QLabel("Voice:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row1.addWidget(lbl)
        self.cb_voice = QComboBox()
        self.cb_voice.setMinimumHeight(32)
        row1.addWidget(self.cb_voice, 1)
        voice_layout.addLayout(row1)
        
        # Row 2: Style + Custom Voice ID
        row2 = QHBoxLayout()
        lbl = QLabel("Phong cách:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row2.addWidget(lbl)
        self.cb_speaking_style = QComboBox()
        self.cb_speaking_style.setMinimumHeight(32)
        if get_style_list:
            for key, name, desc in get_style_list():
                self.cb_speaking_style.addItem(name, key)
            self.cb_speaking_style.setCurrentIndex(2)
        row2.addWidget(self.cb_speaking_style, 1)
        
        row2.addSpacing(12)
        lbl = QLabel("Custom Voice ID:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row2.addWidget(lbl)
        self.ed_custom_voice = QLineEdit()
        self.ed_custom_voice.setMinimumHeight(32)
        self.ed_custom_voice.setPlaceholderText("Override voice ID")
        row2.addWidget(self.ed_custom_voice, 1)
        voice_layout.addLayout(row2)
        
        # Style description
        self.lbl_style_description = QLabel("Giọng sinh động, có cảm xúc")
        self.lbl_style_description.setStyleSheet("font-size: 11px; color: #666;")
        self.lbl_style_description.setWordWrap(True)
        voice_layout.addWidget(self.lbl_style_description)
        
        # Row 3: Rate + Pitch
        row3 = QHBoxLayout()
        lbl = QLabel("Tốc độ:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row3.addWidget(lbl)
        self.slider_rate = QSlider(Qt.Horizontal)
        self.slider_rate.setRange(50, 200)
        self.slider_rate.setValue(100)
        row3.addWidget(self.slider_rate, 1)
        self.lbl_rate = QLabel("1.0x")
        self.lbl_rate.setMinimumWidth(45)
        self.lbl_rate.setAlignment(Qt.AlignCenter)
        row3.addWidget(self.lbl_rate)
        
        row3.addSpacing(12)
        lbl = QLabel("Cao độ:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row3.addWidget(lbl)
        self.slider_pitch = QSlider(Qt.Horizontal)
        self.slider_pitch.setRange(-5, 5)
        self.slider_pitch.setValue(0)
        row3.addWidget(self.slider_pitch, 1)
        self.lbl_pitch = QLabel("0st")
        self.lbl_pitch.setMinimumWidth(45)
        self.lbl_pitch.setAlignment(Qt.AlignCenter)
        row3.addWidget(self.lbl_pitch)
        voice_layout.addLayout(row3)
        
        # Row 4: Expressiveness
        row4 = QHBoxLayout()
        lbl = QLabel("Biểu cảm:")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        row4.addWidget(lbl)
        self.slider_expressiveness = QSlider(Qt.Horizontal)
        self.slider_expressiveness.setRange(0, 100)
        self.slider_expressiveness.setValue(50)
        row4.addWidget(self.slider_expressiveness, 1)
        self.lbl_expressiveness = QLabel("0.5")
        self.lbl_expressiveness.setMinimumWidth(45)
        self.lbl_expressiveness.setAlignment(Qt.AlignCenter)
        row4.addWidget(self.lbl_expressiveness)
        voice_layout.addLayout(row4)
        
        self.cb_apply_voice_all = QCheckBox("Áp dụng tất cả cảnh")
        self.cb_apply_voice_all.setChecked(True)
        voice_layout.addWidget(self.cb_apply_voice_all)
        
        colL.addWidget(voice_group)
        
        # Hidden download settings
        self.cb_auto_download = QCheckBox()
        self.cb_auto_download.setChecked(True)
        self.cb_auto_download.setVisible(False)
        self.cb_quality = QComboBox()
        self.cb_quality.addItems(["1080p", "720p"])
        self.cb_quality.setVisible(False)
        self.lbl_download_folder = QLabel()
        self.lbl_download_folder.setVisible(False)
        self.btn_change_folder = QPushButton()
        self.btn_change_folder.setVisible(False)
        
        # BUTTONS
        hb = QHBoxLayout()
        self.btn_auto = QPushButton("⚡ Tạo video tự động (3 bước)")
        self.btn_auto.setMinimumHeight(48)
        self.btn_auto.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                border: none;
                border-radius: 24px;
                font-weight: 700;
                font-size: 15px;
            }
            QPushButton:hover { background: #FF8555; }
        """)
        hb.addWidget(self.btn_auto)
        
        self.btn_stop = QPushButton("⏹ Dừng")
        self.btn_stop.setMinimumHeight(48)
        self.btn_stop.setMaximumWidth(80)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background: #E0E0E0;
                color: #616161;
                border: none;
                border-radius: 24px;
                font-weight: 700;
            }
            QPushButton:disabled { background: #F5F5F5; color: #BDBDBD; }
        """)
        hb.addWidget(self.btn_stop)
        colL.addLayout(hb)
        
        self.btn_open_folder = QPushButton("📁 Mở thư mục dự án")
        self.btn_open_folder.setMinimumHeight(40)
        self.btn_open_folder.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        colL.addWidget(self.btn_open_folder)
        
        self.btn_clear_project = QPushButton("🔄 Tạo dự án mới")
        self.btn_clear_project.setMinimumHeight(40)
        self.btn_clear_project.setEnabled(False)
        self.btn_clear_project.setStyleSheet("""
            QPushButton {
                background: #E0E0E0;
                color: #616161;
                border: none;
                border-radius: 20px;
                font-weight: 700;
            }
            QPushButton:hover { background: #EEEEEE; }
            QPushButton:disabled { background: #F5F5F5; color: #BDBDBD; }
        """)
        colL.addWidget(self.btn_clear_project)
        
        # CONSOLE
        lbl = QLabel("Console:")
        lbl.setFont(FONT_H2)
        colL.addWidget(lbl)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(120)
        self.console.setMaximumHeight(150)
        self.console.setFont(QFont("Courier New", 11))
        self.console.setStyleSheet("""
            QTextEdit {
                background: #C8E6C9;
                color: #1B5E20;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        colL.addWidget(self.console, 0)
        
        # === RIGHT COLUMN (2/3) ===
        colR = QVBoxLayout()
        colR.setSpacing(8)
        
        # Hidden table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalHeaderLabels([
            "Cảnh", "Prompt (VI)", "Prompt (Đích)",
            "Tỉ lệ", "Thời lượng (s)", "Xem"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setHidden(True)
        colR.addWidget(self.table, 0)
        
        # RESULT TABS - OCEAN BLUE SELECTED
        self.result_tabs = QTabWidget()
        self.result_tabs.setFont(QFont("Segoe UI", 13, QFont.Bold))
        
        # Tab 1: Script
        script_widget = QWidget()
        script_layout = QVBoxLayout(script_widget)
        script_layout.setContentsMargins(8, 8, 8, 8)
        self.view_story = QTextEdit()
        self.view_story.setReadOnly(True)
        self.view_story.setPlaceholderText(
            "Kịch bản chi tiết sẽ hiển thị ở đây sau khi tạo"
        )
        script_layout.addWidget(self.view_story)
        self.result_tabs.addTab(script_widget, "📝 Chi tiết kịch bản")
        
        # Tab 2: Character Bible
        bible_widget = QWidget()
        bible_layout = QVBoxLayout(bible_widget)
        bible_layout.setContentsMargins(8, 8, 8, 8)
        
        bible_btn_row = QHBoxLayout()
        self.btn_generate_bible = QPushButton("✨ Tạo Character Bible")
        self.btn_generate_bible.setMinimumHeight(36)
        self.btn_generate_bible.setEnabled(False)
        self.btn_generate_bible.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 18px;
                font-weight: 700;
            }
            QPushButton:hover { background: #2196F3; }
            QPushButton:disabled { background: #CCCCCC; }
        """)
        bible_btn_row.addWidget(self.btn_generate_bible)
        bible_btn_row.addStretch()
        bible_layout.addLayout(bible_btn_row)
        
        self.view_bible = QTextEdit()
        self.view_bible.setReadOnly(False)
        self.view_bible.setAcceptRichText(False)
        self.view_bible.setPlaceholderText(
            "Character Bible sẽ hiển thị ở đây sau khi tạo..."
        )
        bible_layout.addWidget(self.view_bible)
        self.result_tabs.addTab(bible_widget, "📖 Character Bible")
        
        # Tab 3: Scene Results
        scenes_widget = QWidget()
        scenes_layout = QVBoxLayout(scenes_widget)
        scenes_layout.setContentsMargins(4, 4, 4, 4)
        self.cards = QListWidget()
        self.cards.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cards.setIconSize(QSize(240, 135))
        scenes_layout.addWidget(self.cards)
        self.result_tabs.addTab(scenes_widget, "🎬 Kết quả cảnh")
        
        # Tab 4: Thumbnail
        thumbnail_widget = QWidget()
        thumbnail_layout = QVBoxLayout(thumbnail_widget)
        thumbnail_layout.setContentsMargins(4, 4, 4, 4)
        self.thumbnail_display = QTextEdit()
        self.thumbnail_display.setReadOnly(True)
        self.thumbnail_display.setPlaceholderText(
            "Thumbnail preview sẽ hiển thị ở đây"
        )
        thumbnail_layout.addWidget(self.thumbnail_display)
        self.result_tabs.addTab(thumbnail_widget, "📺 Thumbnail")
        
        # Tab 5: Social
        social_widget = QWidget()
        social_layout = QVBoxLayout(social_widget)
        social_layout.setContentsMargins(4, 4, 4, 4)
        self.social_display = QTextEdit()
        self.social_display.setReadOnly(True)
        self.social_display.setPlaceholderText(
            "Social media content sẽ hiển thị ở đây"
        )
        social_layout.addWidget(self.social_display)
        self.result_tabs.addTab(social_widget, "📱 Social")
        
        # OCEAN BLUE STYLING
        self.result_tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 140px;
                padding: 12px 18px;
                font-weight: 700;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 3px;
            }
            QTabBar::tab:selected {
                background: #00ACC1;
                color: white;
                border-bottom: 4px solid #00838F;
            }
            QTabBar::tab:!selected {
                background: #F5F5F5;
                color: #616161;
            }
            QTabBar::tab:hover {
                background: #B2EBF2;
            }
        """)
        
        colR.addWidget(self.result_tabs, 1)
        
        root.addLayout(colL, 1)
        root.addLayout(colR, 2)
        
        # WIRE UP
        self.btn_auto.clicked.connect(self._on_auto_generate)
        self.btn_stop.clicked.connect(self.stop_processing)
        self.btn_open_folder.clicked.connect(self._open_project_dir)
        self.btn_generate_bible.clicked.connect(self._on_generate_bible)
        self.btn_clear_project.clicked.connect(self._clear_current_project)
        self.btn_change_folder.clicked.connect(self._on_change_folder)
        
        self.table.cellDoubleClicked.connect(self._open_prompt_view)
        self.cards.itemDoubleClicked.connect(self._open_card_prompt)
        
        self.cb_speaking_style.currentIndexChanged.connect(
            self._on_speaking_style_changed
        )
        self.slider_rate.valueChanged.connect(self._on_rate_changed)
        self.slider_pitch.valueChanged.connect(self._on_pitch_changed)
        self.slider_expressiveness.valueChanged.connect(
            self._on_expressiveness_changed
        )
        
        self.cb_tts_provider.currentIndexChanged.connect(
            self._load_voices_for_provider
        )
        self.cb_out_lang.currentIndexChanged.connect(
            self._load_voices_for_provider
        )
        
        self.cb_domain.currentIndexChanged.connect(self._on_domain_changed)
        self.cb_topic.currentIndexChanged.connect(self._on_topic_changed)
        
        shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut.activated.connect(self._clear_current_project)
        
        # Load initial voices
        self._load_voices_for_provider()
    
    def _apply_styles(self):
        groupbox_style = """
        QGroupBox {
            font-weight: bold;
            font-size: 13px;
            border: 1px solid #d0d0d0;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 10px;
            left: 10px;
            top: 0px;
        }
        """
        self.setStyleSheet(groupbox_style)
    
    def _append_log(self, msg):
        self.console.append(msg)
    
    # === CONTINUE IN NEXT PART (methods from original) ===
    # Methods: stop_processing, _on_auto_generate, _run_in_thread,
    # _on_story_ready, _on_job_card, _open_project_dir, etc.
    # ui/text2video_panel_v5_complete.py - PART 2: METHODS
# Tiếp tục từ Part 1...

    # === CORE METHODS (from original text2video_panel.py) ===
    
    def stop_processing(self):
        """Stop all workers"""
        if self.worker:
            self.worker.should_stop = True
            self._append_log("[INFO] Đang dừng xử lý...")
        
        self.btn_auto.setEnabled(True)
        self.btn_stop.setEnabled(False)
    
    def _on_auto_generate(self):
        """Auto-generate - 3 steps: script -> video -> download"""
        idea = self.ed_idea.toPlainText().strip()
        if not idea:
            QMessageBox.warning(self, "Thiếu thông tin", "Nhập ý tưởng trước.")
            return
        
        self.btn_auto.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        # Get settings
        tts_provider = self.cb_tts_provider.currentData()
        voice_id = self.ed_custom_voice.text().strip() or self.cb_voice.currentData()
        domain = self.cb_domain.currentData()
        topic = self.cb_topic.currentData()
        
        payload = dict(
            project=self.ed_project.text().strip(),
            idea=idea,
            style=self.cb_style.currentText(),
            duration=int(self.sp_duration.value()),
            provider="Gemini 2.5",
            out_lang_code=self.cb_out_lang.currentData(),
            tts_provider=tts_provider,
            voice_id=voice_id,
            domain=domain or None,
            topic=topic or None,
        )
        
        self._append_log("[INFO] Bước 1/3: Sinh kịch bản...")
        self._run_in_thread("script", payload)
    
    def _run_in_thread(self, task, payload):
        """Run task in background thread"""
        if not _Worker:
            self._append_log("[ERR] Worker not available")
            return
        
        self.thread = QThread(self)
        self.worker = _Worker(task, payload)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self._append_log)
        
        if task == "script":
            self.worker.story_done.connect(self._on_story_ready)
        else:
            self.worker.job_card.connect(self._on_job_card)
            self.worker.job_finished.connect(self._on_worker_finished)
        
        self.thread.start()
    
    def _on_worker_finished(self):
        """Re-enable buttons when worker completes"""
        self._append_log("[INFO] Worker hoàn tất.")
        self.btn_auto.setEnabled(True)
        self.btn_stop.setEnabled(False)
    
    def _on_story_ready(self, data, ctx):
        """Handle script generation completion"""
        self._ctx = ctx
        self._title = (
            self.ed_project.text().strip() or 
            data.get("title_vi") or 
            data.get("title_tgt") or 
            ctx.get("title")
        )
        
        # Display Bible + Outline + Screenplay
        parts = []
        cb = data.get("character_bible") or []
        if cb:
            parts.append("=== HỒ SƠ NHÂN VẬT ===")
            for c in cb:
                parts.append(
                    f"- {c.get('name','?')} [{c.get('role','?')}]: "
                    f"key_trait={c.get('key_trait','')}; "
                    f"motivation={c.get('motivation','')}; "
                    f"visual={c.get('visual_identity','')}"
                )
        
        ol_vi = data.get("outline_vi", "").strip()
        if ol_vi:
            parts.append("\n=== DÀN Ý ===\n" + ol_vi)
        
        sp_vi = data.get("screenplay_vi", "").strip()
        sp_tgt = data.get("screenplay_tgt", "").strip()
        if sp_vi or sp_tgt:
            parts.append(
                f"\n=== KỊCH BẢN (VI) ===\n{sp_vi}\n\n"
                f"=== SCREENPLAY ===\n{sp_tgt}"
            )
        
        self.view_story.setPlainText(
            "\n\n".join(parts) if parts else "(Không có dữ liệu)"
        )
        
        # Update cards
        self.cards.clear()
        self._cards_state = {}
        
        for i, sc in enumerate(data.get('scenes', []), 1):
            vi = sc.get('prompt_vi', '')
            tgt = sc.get('prompt_tgt', '')
            self._cards_state[i] = {
                'vi': vi, 'tgt': tgt, 'thumb': '', 'videos': {}
            }
            it = QListWidgetItem(self._render_card_text(i))
            it.setData(Qt.UserRole, ('scene', i))
            self.cards.addItem(it)
        
        # Fill table & save prompts
        self.table.setRowCount(0)
        prdir = ctx.get("dir_prompts", "")
        
        for i, sc in enumerate(data.get("scenes", []), 1):
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(i)))
            self.table.setItem(r, 1, QTableWidgetItem(sc.get("prompt_vi", "")))
            self.table.setItem(r, 2, QTableWidgetItem(sc.get("prompt_tgt", "")))
            self.table.setItem(r, 3, QTableWidgetItem(self.cb_ratio.currentText()))
            self.table.setItem(r, 4, QTableWidgetItem(str(sc.get("duration", 8))))
            
            btn = QPushButton("Xem")
            btn.clicked.connect(lambda _, row=r: self._open_prompt_view(row))
            self.table.setCellWidget(r, 5, btn)
            
            # Save prompt JSON per scene
            if build_prompt_json and prdir:
                try:
                    lang_code = self.cb_out_lang.currentData()
                    character_bible_basic = data.get("character_bible", [])
                    voice_settings = self.get_voice_settings()
                    location_ctx = extract_location_context(sc) if extract_location_context else None
                    
                    j = build_prompt_json(
                        i, sc.get("prompt_vi", ""), sc.get("prompt_tgt", ""),
                        lang_code, self.cb_ratio.currentText(),
                        self.cb_style.currentText(),
                        character_bible=character_bible_basic,
                        voice_settings=voice_settings,
                        location_context=location_ctx
                    )
                    
                    with open(
                        os.path.join(prdir, f"scene_{i:02d}.json"),
                        "w", encoding="utf-8"
                    ) as f:
                        json.dump(j, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    self._append_log(f"[WARN] Could not save prompt: {e}")
        
        self._append_log("[INFO] Kịch bản đã hiển thị & lưu file.")
        
        # Store script data and enable bible generation
        self._script_data = data
        self.btn_generate_bible.setEnabled(True)
        self.btn_clear_project.setEnabled(True)
        
        # Auto-generate character bible
        cb = data.get("character_bible") or []
        if cb:
            self._generate_character_bible_from_data(data)
        
        # Auto-generate social and thumbnail
        self._auto_generate_social_and_thumbnail(data)
        
        # If in auto mode, proceed to step 2
        if self.btn_stop.isEnabled():
            self._append_log("[INFO] Bước 2/3: Bắt đầu tạo video...")
            self._on_create_video_clicked()
        else:
            self.btn_auto.setEnabled(True)
    
    def _on_create_video_clicked(self):
        """Create videos from script"""
        if self.table.rowCount() <= 0:
            QMessageBox.information(
                self, "Chưa có kịch bản",
                "Hãy tạo kịch bản trước."
            )
            return
        
        lang_code = self.cb_out_lang.currentData()
        ratio_key = self.cb_ratio.currentText()
        ratio = _ASPECT_MAP.get(ratio_key, "VIDEO_ASPECT_RATIO_LANDSCAPE")
        style = self.cb_style.currentText()
        scenes = []
        
        character_bible_basic = (
            self._script_data.get("character_bible", [])
            if self._script_data else []
        )
        voice_settings = self.get_voice_settings()
        
        for r in range(self.table.rowCount()):
            vi = self.table.item(r, 1).text() if self.table.item(r, 1) else ""
            tgt = self.table.item(r, 2).text() if self.table.item(r, 2) else vi
            
            location_ctx = None
            if self._script_data and "scenes" in self._script_data:
                scene_list = self._script_data["scenes"]
                if r < len(scene_list) and extract_location_context:
                    location_ctx = extract_location_context(scene_list[r])
            
            if build_prompt_json:
                j = build_prompt_json(
                    r + 1, vi, tgt, lang_code, ratio_key, style,
                    character_bible=character_bible_basic,
                    enhanced_bible=self._character_bible,
                    voice_settings=voice_settings,
                    location_context=location_ctx
                )
                scenes.append({
                    "prompt": json.dumps(j, ensure_ascii=False, indent=2),
                    "aspect": ratio
                })
        
        model_display = self.cb_model.currentText()
        model_key = get_model_key_from_display(model_display) if get_model_key_from_display else model_display
        
        payload = dict(
            scenes=scenes,
            copies=self._t2v_get_copies(),
            model_key=model_key,
            title=self._title,
            dir_videos=self._ctx.get("dir_videos", ""),
            upscale_4k=self.cb_upscale.isChecked(),
            auto_download=self.cb_auto_download.isChecked(),
            quality=self.cb_quality.currentText()
        )
        
        if not payload["dir_videos"]:
            if cfg:
                st = cfg.load()
                root = st.get("download_dir") or ""
                if not root:
                    QMessageBox.warning(
                        self, "Thiếu cấu hình",
                        "Vào tab Cài đặt để chọn 'Thư mục tải về' trước."
                    )
                    return
                prj = os.path.join(root, self._title or "Project")
                os.makedirs(prj, exist_ok=True)
                payload["dir_videos"] = os.path.join(prj, "03_Videos")
                os.makedirs(payload["dir_videos"], exist_ok=True)
        
        self._append_log("[INFO] Bắt đầu tạo video...")
        self._run_in_thread("video", payload)
    
    def _render_card_text(self, scene: int):
        """Render card text for scene"""
        st = self._cards_state.get(scene, {})
        vi = st.get('vi', '').strip()
        tgt = st.get('tgt', '').strip()
        
        lines = [f'Cảnh {scene}']
        if tgt or vi:
            lines.append('— PROMPT (đích/VI) —')
            if tgt:
                lines.append(tgt)
            if vi:
                lines.append(vi)
        
        vids = st.get('videos', {})
        if vids:
            lines.append('— Video —')
            for copy, info in sorted(vids.items()):
                tag = f"Video {copy}: {info.get('status', '?')}"
                if info.get('completed_at'):
                    tag += f" — hoàn tất: {info['completed_at']}"
                if info.get('path'):
                    tag += f"\n📥 {info['path']}"
                elif info.get('url'):
                    tag += f"\n🔗 {info['url']}"
                lines.append(tag)
        
        return '\n'.join(lines)
    
    def _on_job_card(self, data: dict):
        """Update job card with video status"""
        scene = int(data.get('scene', 0) or 0)
        copy = int(data.get('copy', 0) or 0)
        if scene <= 0 or copy <= 0:
            return
        
        st = self._cards_state.setdefault(scene, {
            'vi': '', 'tgt': '', 'thumb': '', 'videos': {}
        })
        v = st['videos'].setdefault(copy, {})
        
        for k in ('status', 'url', 'path', 'thumb', 'completed_at'):
            if data.get(k):
                v[k] = data.get(k)
        
        if data.get('thumb') and os.path.isfile(data['thumb']):
            st['thumb'] = data['thumb']
        
        for i in range(self.cards.count()):
            it = self.cards.item(i)
            role = it.data(Qt.UserRole)
            if isinstance(role, tuple) and role == ('scene', scene):
                it.setText(self._render_card_text(scene))
                
                if st.get('thumb') and os.path.isfile(st['thumb']):
                    pix = QPixmap(st['thumb']).scaled(
                        self.cards.iconSize(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    it.setIcon(QIcon(pix))
                
                col = self._t2v_status_color(v.get('status'))
                if col:
                    it.setBackground(col)
                break
    
    def _t2v_status_color(self, status):
        """Get color for video status"""
        s = (status or "").upper()
        if s in ("QUEUED", "PROCESSING", "RENDERING", "DOWNLOADING"):
            return QColor("#36D1BE")
        if s in ("COMPLETED", "DOWNLOADED", "UPSCALED_4K"):
            return QColor("#3FD175")
        if s in ("ERROR", "FAILED"):
            return QColor("#ED6D6A")
        return None
    
    def _t2v_get_copies(self):
        """Get number of video copies"""
        try:
            return int(self.sp_copies.value())
        except:
            return 1
    
    def _open_project_dir(self):
        """Open project directory"""
        d = self._ctx.get("prj_dir")
        if d and os.path.isdir(d):
            QDesktopServices.openUrl(QUrl.fromLocalFile(d))
        else:
            QMessageBox.information(
                self, "Chưa có thư mục",
                "Hãy viết kịch bản trước để tạo cấu trúc dự án."
            )
    
    def _open_prompt_view(self, row):
        """Open prompt viewer for row"""
        if row < 0 or row >= self.table.rowCount():
            return
        
        vi = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        tgt = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
        lang_code = self.cb_out_lang.currentData()
        voice_settings = self.get_voice_settings()
        
        location_ctx = None
        if self._script_data and "scenes" in self._script_data:
            scene_list = self._script_data["scenes"]
            if row < len(scene_list) and extract_location_context:
                location_ctx = extract_location_context(scene_list[row])
        
        if build_prompt_json:
            j = build_prompt_json(
                row + 1, vi, tgt, lang_code,
                self.cb_ratio.currentText(),
                self.cb_style.currentText(),
                voice_settings=voice_settings,
                location_context=location_ctx
            )
            
            try:
                from ui.prompt_viewer import PromptViewer
                dlg = PromptViewer(
                    json.dumps(j, ensure_ascii=False, indent=2),
                    None, self
                )
                dlg.exec_()
            except ImportError:
                self._append_log("[WARN] PromptViewer not available")
    
    def _open_card_prompt(self, it):
        """Open prompt from card"""
        try:
            role = it.data(Qt.UserRole)
            scene = None
            if isinstance(role, tuple) and role[0] == 'scene':
                scene = int(role[1])
            if not scene:
                return
            
            st = self._cards_state.get(scene, {})
            txt = st.get('prompt_json', '')
            
            if not txt:
                pr = getattr(self, '_project_root', '')
                if pr:
                    p = os.path.join(pr, '02_Prompts', f'scene_{scene:02d}.json')
                    if os.path.isfile(p):
                        txt = open(p, 'r', encoding='utf-8').read()
            
            if txt:
                try:
                    from ui.prompt_viewer import PromptViewer
                    dlg = PromptViewer(txt, None, self)
                    dlg.exec_()
                except ImportError:
                    pass
        except Exception:
            pass
    
    def _on_generate_bible(self):
        """Generate detailed character bible"""
        if not self._script_data:
            QMessageBox.warning(
                self, "Chưa có kịch bản",
                "Hãy tạo kịch bản trước khi tạo Character Bible."
            )
            return
        
        self._append_log("[INFO] Đang tạo Character Bible chi tiết...")
        self._generate_character_bible_from_data(self._script_data)
        self._append_log("[INFO] Character Bible đã tạo xong.")
    
    def _generate_character_bible_from_data(self, data):
        """Generate character bible from script data"""
        try:
            from services.google.character_bible import (
                create_character_bible,
                format_character_bible_for_display,
            )
            
            video_concept = self.ed_idea.toPlainText().strip()
            screenplay = data.get("screenplay_tgt", "") or data.get("screenplay_vi", "")
            existing_bible = data.get("character_bible", [])
            
            self._character_bible = create_character_bible(
                video_concept, screenplay, existing_bible
            )
            
            formatted = format_character_bible_for_display(self._character_bible)
            self.view_bible.setPlainText(formatted)
            
            if self._ctx.get("dir_script"):
                bible_path = os.path.join(
                    self._ctx["dir_script"],
                    "character_bible_detailed.json"
                )
                try:
                    with open(bible_path, "w", encoding="utf-8") as f:
                        f.write(self._character_bible.to_json())
                    self._append_log(f"[INFO] Character Bible đã lưu: {bible_path}")
                except Exception as e:
                    self._append_log(f"[WARN] Không thể lưu: {e}")
        
        except Exception as e:
            self._append_log(f"[ERR] Lỗi tạo Character Bible: {e}")
            QMessageBox.warning(
                self, "Lỗi",
                f"Không thể tạo Character Bible: {e}"
            )
    
    def _auto_generate_social_and_thumbnail(self, script_data):
        """Auto-generate social media and thumbnail content"""
        try:
            # Generate social media
            self._append_log("[INFO] Đang tạo nội dung Social Media...")
            try:
                if generate_social_media:
                    social_data = generate_social_media(
                        script_data, provider="Gemini 2.5"
                    )
                    self._display_social_media(social_data)
                    self._append_log("[INFO] ✅ Social Media content đã tạo xong")
            except Exception as e:
                self._append_log(f"[WARN] Không thể tạo Social Media: {e}")
            
            # Generate thumbnail
            self._append_log("[INFO] Đang tạo Thumbnail design...")
            try:
                if generate_thumbnail_design:
                    thumbnail_data = generate_thumbnail_design(
                        script_data, provider="Gemini 2.5"
                    )
                    self._display_thumbnail_design(thumbnail_data)
                    self._append_log("[INFO] ✅ Thumbnail design đã tạo xong")
            except Exception as e:
                self._append_log(f"[WARN] Không thể tạo Thumbnail: {e}")
        
        except Exception as e:
            self._append_log(f"[ERR] Lỗi khi tạo Social/Thumbnail: {e}")
    
    def _display_social_media(self, social_data):
        """Display social media content"""
        if not social_data:
            return
        
        content_parts = []
        
        if "casual" in social_data:
            casual = social_data["casual"]
            content_parts.append("=" * 60)
            content_parts.append("📱 VERSION 1: CASUAL/FRIENDLY")
            content_parts.append("=" * 60)
            content_parts.append(f"\n🎯 Platform: {casual.get('platform', 'TikTok')}")
            content_parts.append(f"\n📝 Title:\n{casual.get('title', '')}")
            content_parts.append(f"\n📄 Description:\n{casual.get('description', '')}")
            if casual.get('hashtags'):
                content_parts.append(f"\n🏷️ Hashtags:\n{' '.join(casual['hashtags'])}")
            content_parts.append(f"\n📢 CTA:\n{casual.get('cta', '')}")
        
        if "professional" in social_data:
            prof = social_data["professional"]
            content_parts.append("\n\n" + "=" * 60)
            content_parts.append("💼 VERSION 2: PROFESSIONAL")
            content_parts.append("=" * 60)
            content_parts.append(f"\n🎯 Platform: {prof.get('platform', 'LinkedIn')}")
            content_parts.append(f"\n📝 Title:\n{prof.get('title', '')}")
            content_parts.append(f"\n📄 Description:\n{prof.get('description', '')}")
            if prof.get('hashtags'):
                content_parts.append(f"\n🏷️ Hashtags:\n{' '.join(prof['hashtags'])}")
            content_parts.append(f"\n📢 CTA:\n{prof.get('cta', '')}")
        
        if "funny" in social_data:
            funny = social_data["funny"]
            content_parts.append("\n\n" + "=" * 60)
            content_parts.append("😂 VERSION 3: FUNNY/ENGAGING")
            content_parts.append("=" * 60)
            content_parts.append(f"\n🎯 Platform: {funny.get('platform', 'TikTok')}")
            content_parts.append(f"\n📝 Title:\n{funny.get('title', '')}")
            content_parts.append(f"\n📄 Description:\n{funny.get('description', '')}")
            if funny.get('hashtags'):
                content_parts.append(f"\n🏷️ Hashtags:\n{' '.join(funny['hashtags'])}")
            content_parts.append(f"\n📢 CTA:\n{funny.get('cta', '')}")
        
        self.social_display.setPlainText("\n".join(content_parts))
    
    def _display_thumbnail_design(self, thumbnail_data):
        """Display thumbnail design"""
        if not thumbnail_data:
            return
        
        content_parts = []
        content_parts.append("=" * 60)
        content_parts.append("🖼️ THUMBNAIL DESIGN SPECIFICATIONS")
        content_parts.append("=" * 60)
        
        if "concept" in thumbnail_data:
            content_parts.append("\n💡 CONCEPT:")
            content_parts.append(thumbnail_data["concept"])
        
        if "color_palette" in thumbnail_data:
            content_parts.append("\n\n🎨 COLOR PALETTE:")
            for color in thumbnail_data["color_palette"]:
                content_parts.append(
                    f"  • {color.get('name', '')}: {color.get('hex', '')} - "
                    f"{color.get('usage', '')}"
                )
        
        if "typography" in thumbnail_data:
            typo = thumbnail_data["typography"]
            content_parts.append("\n\n✍️ TYPOGRAPHY:")
            content_parts.append(f"  • Main Text: {typo.get('main_text', '')}")
            content_parts.append(f"  • Font: {typo.get('font_family', '')}")
            content_parts.append(f"  • Size: {typo.get('font_size', '')}")
        
        if "layout" in thumbnail_data:
            layout = thumbnail_data["layout"]
            content_parts.append("\n\n📐 LAYOUT:")
            content_parts.append(f"  • Composition: {layout.get('composition', '')}")
            content_parts.append(f"  • Focal Point: {layout.get('focal_point', '')}")
        
        self.thumbnail_display.setPlainText("\n".join(content_parts))
    
    def _on_speaking_style_changed(self):
        """Handle speaking style change"""
        style_key = self.cb_speaking_style.currentData()
        if not style_key or not get_style_info:
            return
        
        style_info = get_style_info(style_key)
        self.lbl_style_description.setText(style_info["description"])
        
        if SPEAKING_STYLES and style_key in SPEAKING_STYLES:
            style_config = SPEAKING_STYLES[style_key]
            
            rate_map = {"slow": 75, "medium": 100, "fast": 125}
            preset_rate = rate_map.get(
                style_config["google_tts"]["rate"], 100
            )
            self.slider_rate.setValue(preset_rate)
            
            pitch_str = style_config["google_tts"]["pitch"]
            match = re.match(r'([+-]?\d+)st', pitch_str)
            preset_pitch = int(match.group(1)) if match else 0
            self.slider_pitch.setValue(preset_pitch)
            
            preset_expr = int(style_config["elevenlabs"]["style"] * 100)
            self.slider_expressiveness.setValue(preset_expr)
    
    def _on_rate_changed(self, value):
        """Handle rate slider change"""
        multiplier = value / 100.0
        self.lbl_rate.setText(f"{multiplier:.1f}x")
    
    def _on_pitch_changed(self, value):
        """Handle pitch slider change"""
        if value > 0:
            self.lbl_pitch.setText(f"+{value}st")
        elif value < 0:
            self.lbl_pitch.setText(f"{value}st")
        else:
            self.lbl_pitch.setText("0st")
    
    def _on_expressiveness_changed(self, value):
        """Handle expressiveness slider change"""
        decimal = value / 100.0
        self.lbl_expressiveness.setText(f"{decimal:.1f}")
    
    def _on_domain_changed(self):
        """Handle domain selection - load topics"""
        domain = self.cb_domain.currentData()
        self.cb_topic.clear()
        self.cb_topic.addItem("(Chọn lĩnh vực để load chủ đề)", "")
        
        if not domain:
            self.cb_topic.setEnabled(False)
            return
        
        try:
            if get_topics_for_domain:
                topics = get_topics_for_domain(domain)
                if topics:
                    self.cb_topic.clear()
                    self.cb_topic.addItem("(Chọn chủ đề)", "")
                    for topic in topics:
                        self.cb_topic.addItem(topic, topic)
                    self.cb_topic.setEnabled(True)
                    self._append_log(f"[INFO] Loaded {len(topics)} topics")
        except Exception as e:
            self._append_log(f"[ERR] {e}")
            self.cb_topic.setEnabled(False)
    
    def _on_topic_changed(self):
        """Handle topic selection"""
        pass  # Preview removed
    
    def _load_voices_for_provider(self):
        """Load voices for selected provider"""
        try:
            provider = self.cb_tts_provider.currentData()
            language = self.cb_out_lang.currentData()
            
            if not provider or not get_voices_for_provider:
                return
            
            voices = get_voices_for_provider(provider, language)
            
            self.cb_voice.blockSignals(True)
            self.cb_voice.clear()
            
            for voice in voices:
                display_name = voice.get("name", voice.get("id", "Unknown"))
                voice_id = voice.get("id")
                self.cb_voice.addItem(display_name, voice_id)
            
            self.cb_voice.blockSignals(False)
            
            if voices:
                self._append_log(f"[INFO] Loaded {len(voices)} voices")
        
        except Exception as e:
            self._append_log(f"[ERR] Failed to load voices: {e}")
    
    def get_voice_settings(self):
        """Get current voice settings"""
        style_key = self.cb_speaking_style.currentData() or "storytelling"
        rate_multiplier = self.slider_rate.value() / 100.0
        pitch_adjust = self.slider_pitch.value()
        expressiveness = self.slider_expressiveness.value() / 100.0
        apply_all = self.cb_apply_voice_all.isChecked()
        
        return {
            "speaking_style": style_key,
            "rate_multiplier": rate_multiplier,
            "pitch_adjust": pitch_adjust,
            "expressiveness": expressiveness,
            "apply_to_all_scenes": apply_all
        }
    
    def _on_change_folder(self):
        """Change download folder"""
        if not cfg:
            return
        
        st = cfg.load()
        current_dir = st.get("download_root") or os.path.expanduser("~/Downloads")
        
        folder = QFileDialog.getExistingDirectory(
            self, "Chọn thư mục tải video", current_dir
        )
        
        if folder:
            st["download_root"] = folder
            cfg.save(st)
            self._update_folder_label(folder)
            self._append_log(f"[INFO] Đã đổi thư mục: {folder}")
    
    def _update_folder_label(self, folder_path=None):
        """Update folder label"""
        if not folder_path and cfg:
            st = cfg.load()
            folder_path = st.get("download_root") or "Chưa đặt"
        
        if folder_path and len(folder_path) > 40:
            folder_path = "..." + folder_path[-37:]
        
        self.lbl_download_folder.setText(f"Thư mục: {folder_path}")
    
    def _clear_current_project(self):
        """Clear current project workspace"""
        reply = QMessageBox.question(
            self, 'Xác nhận xóa dự án',
            'Bạn có chắc muốn xóa dự án hiện tại?\n\n'
            '⚠️ Files đã tải về sẽ KHÔNG bị xóa.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Check if video generating
        if self.btn_stop.isEnabled():
            reply_stop = QMessageBox.warning(
                self, 'Video đang tạo',
                'Bạn có chắc muốn dừng và xóa?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply_stop == QMessageBox.No:
                return
            self.stop_processing()
        
        # Clear UI
        self.ed_project.clear()
        self.ed_idea.clear()
        
        if hasattr(self, 'cb_domain'):
            self.cb_domain.setCurrentIndex(0)
        if hasattr(self, 'cb_topic'):
            self.cb_topic.clear()
            self.cb_topic.addItem("(Chọn lĩnh vực để load chủ đề)", "")
            self.cb_topic.setEnabled(False)
        
        self.view_story.clear()
        if hasattr(self, 'view_bible'):
            self.view_bible.clear()
        
        if hasattr(self, 'table'):
            self.table.setRowCount(0)
        
        self.cards.clear()
        
        if hasattr(self, 'social_display'):
            self.social_display.clear()
        if hasattr(self, 'thumbnail_display'):
            self.thumbnail_display.clear()
        
        # Reset state
        self._ctx = {}
        self._title = "Project"
        self._character_bible = None
        self._script_data = None
        self._cards_state = {}
        
        self.btn_generate_bible.setEnabled(False)
        self.btn_clear_project.setEnabled(False)
        
        self._append_log("[INFO] ✅ Đã xóa dự án hiện tại.")
        
        if hasattr(self, 'result_tabs'):
            self.result_tabs.setCurrentIndex(0)