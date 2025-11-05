# -*- coding: utf-8 -*-
"""
Video Ads Panel V2 - Complete Redesign
- Compact left sidebar (250px instead of 400px)
- Horizontal action buttons
- Better balance
- Responsive design
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QGroupBox, QGridLayout, QScrollArea, QFrame, QTabWidget,
    QPushButton, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.widgets.compact_button import CompactButton, create_button_row

# Typography
FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)
FONT_SMALL = QFont("Segoe UI", 12)

class VideoAdsLeftPanel(QWidget):
    """Compact left sidebar for video ads"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        # Scroll for long content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # === Project Info ===
        project_group = QGroupBox("📁 Project")
        project_group.setFont(FONT_H2)
        proj_layout = QVBoxLayout(project_group)
        proj_layout.setSpacing(8)
        
        proj_layout.addWidget(QLabel("Project Name:"))
        self.ed_project = QLineEdit("2025-11-04-1")
        self.ed_project.setMinimumHeight(32)
        proj_layout.addWidget(self.ed_project)
        
        layout.addWidget(project_group)
        
        # === Video Idea ===
        idea_group = QGroupBox("💡 Idea")
        idea_group.setFont(FONT_H2)
        idea_layout = QVBoxLayout(idea_group)
        idea_layout.setSpacing(8)
        
        idea_layout.addWidget(QLabel("Main Concept:"))
        self.txt_idea = QTextEdit()
        self.txt_idea.setMinimumHeight(80)
        self.txt_idea.setMaximumHeight(120)
        self.txt_idea.setPlaceholderText("Enter video concept...")
        idea_layout.addWidget(self.txt_idea)
        
        layout.addWidget(idea_group)
        
        # === Content Settings ===
        content_group = QGroupBox("⚙️ Settings")
        content_group.setFont(FONT_H2)
        content_layout = QVBoxLayout(content_group)
        content_layout.setSpacing(8)
        
        self.chk_persona = QCheckBox("👤 Persona Info")
        self.chk_persona.setFont(FONT_BODY)
        content_layout.addWidget(self.chk_persona)
        
        self.chk_product = QCheckBox("📦 Product Cover")
        self.chk_product.setFont(FONT_BODY)
        content_layout.addWidget(self.chk_product)
        
        self.chk_video_gen = QCheckBox("🎬 Generate Video")
        self.chk_video_gen.setFont(FONT_BODY)
        content_layout.addWidget(self.chk_video_gen)
        
        layout.addWidget(content_group)
        
        # === Action Buttons (HORIZONTAL) ===
        btn_write = CompactButton("📝 Write Script")
        btn_write.setObjectName("btn_warning")
        btn_write.setMinimumHeight(36)
        layout.addWidget(btn_write)
        
        btn_image = CompactButton("🖼 Generate Image")
        btn_image.setObjectName("btn_primary")
        btn_image.setMinimumHeight(36)
        layout.addWidget(btn_image)
        
        btn_video = CompactButton("🎬 Create Video")
        btn_video.setObjectName("btn_success")
        btn_video.setMinimumHeight(40)
        btn_video.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(btn_video)
        
        # Run all actions (HORIZONTAL row)
        run_row = create_button_row(
            ("🔥 Run All (3 steps)", "btn_success")
        )
        run_row.buttons[0].setMinimumHeight(40)
        run_row.buttons[0].setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(run_row)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

class VideoAdsRightPanel(QWidget):
    """Right panel with tabs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setFont(FONT_BODY)
        
        # Tab 1: Script
        tab_script = QWidget()
        script_layout = QVBoxLayout(tab_script)
        script_layout.setContentsMargins(12, 12, 12, 12)
        
        script_hint = QLabel("📝 AI-generated script will appear here")
        script_hint.setFont(FONT_SMALL)
        script_hint.setStyleSheet("color: #757575; font-style: italic;")
        script_layout.addWidget(script_hint)
        
        self.txt_script = QTextEdit()
        self.txt_script.setPlaceholderText("Script content...")
        script_layout.addWidget(self.txt_script)
        
        self.tabs.addTab(tab_script, "📝 Script")
        
        # Tab 2: Character Bible
        tab_char = QWidget()
        char_layout = QVBoxLayout(tab_char)
        char_layout.setContentsMargins(12, 12, 12, 12)
        
        self.txt_char = QTextEdit()
        self.txt_char.setPlaceholderText("Character descriptions...")
        char_layout.addWidget(self.txt_char)
        
        self.tabs.addTab(tab_char, "📖 Character")
        
        # Tab 3: Results
        tab_results = QWidget()
        results_layout = QVBoxLayout(tab_results)
        results_layout.setContentsMargins(12, 12, 12, 12)
        
        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        self.txt_results.setPlaceholderText("Execution results...")
        results_layout.addWidget(self.txt_results)
        
        self.tabs.addTab(tab_results, "✅ Results")
        
        # Tab 4: Social
        tab_social = QWidget()
        social_layout = QVBoxLayout(tab_social)
        social_layout.setContentsMargins(12, 12, 12, 12)
        
        self.txt_social = QTextEdit()
        self.txt_social.setPlaceholderText("Social media content...")
        social_layout.addWidget(self.txt_social)
        
        self.tabs.addTab(tab_social, "📱 Social")
        
        layout.addWidget(self.tabs)

class VideoAdsPanelV2(QWidget):
    """Video Ads Panel V2 - Redesigned"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (250px, compact)
        self.left_panel = VideoAdsLeftPanel()
        self.left_panel.setMinimumWidth(200)
        self.left_panel.setMaximumWidth(350)
        splitter.addWidget(self.left_panel)
        
        # Right panel (takes remaining space)
        self.right_panel = VideoAdsRightPanel()
        splitter.addWidget(self.right_panel)
        
        # Set initial sizes (250px left, rest right)
        splitter.setSizes([250, 800])
        
        layout.addWidget(splitter)