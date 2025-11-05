# -*- coding: utf-8 -*-
"""
Text2Video Panel V2 - Complete Redesign
- Compact left panel
- Better form layout
- Prominent inputs
- Responsive design
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QGroupBox, QGridLayout, QScrollArea, QFrame,
    QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.widgets.compact_button import CompactButton, create_button_row

# Typography
FONT_H1 = QFont("Segoe UI", 16, QFont.Bold)
FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)
FONT_SMALL = QFont("Segoe UI", 12)

def _prominent_input(placeholder="", multiline=False):
    """Create prominent input field"""
    if multiline:
        widget = QTextEdit()
        widget.setMinimumHeight(100)
        widget.setMaximumHeight(150)
    else:
        widget = QLineEdit()
        widget.setMinimumHeight(36)
    
    widget.setFont(FONT_BODY)
    if hasattr(widget, 'setPlaceholderText'):
        widget.setPlaceholderText(placeholder)
    
    widget.setStyleSheet("""
        QLineEdit, QTextEdit {
            background: white;
            border: 2px solid #BDBDBD;
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 13px;
            font-weight: 500;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #1E88E5;
            background: #F8FCFF;
        }
    """)
    
    return widget

class Text2VideoPanelV2(QWidget):
    """Text2Video Panel V2 - Redesigned"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # === Project Info ===
        project_group = QGroupBox("📁 Project Information")
        project_group.setFont(FONT_H2)
        proj_layout = QGridLayout(project_group)
        proj_layout.setVerticalSpacing(12)
        proj_layout.setHorizontalSpacing(12)
        
        # Project name
        proj_layout.addWidget(QLabel("Project Name:"), 0, 0)
        self.ed_project_name = _prominent_input("Enter project name...")
        proj_layout.addWidget(self.ed_project_name, 0, 1, 1, 2)
        
        # Idea/Paragraph
        proj_layout.addWidget(QLabel("Main Idea:"), 1, 0, Qt.AlignTop)
        self.txt_idea = _prominent_input("Enter your video concept (max 10 sentences)", multiline=True)
        proj_layout.addWidget(self.txt_idea, 1, 1, 1, 2)
        
        layout.addWidget(project_group)
        
        # === Video Settings ===
        settings_group = QGroupBox("⚙️ Video Settings")
        settings_group.setFont(FONT_H2)
        settings_layout = QGridLayout(settings_group)
        settings_layout.setVerticalSpacing(12)
        settings_layout.setHorizontalSpacing(12)
        
        # Domain
        settings_layout.addWidget(QLabel("Domain:"), 0, 0)
        self.cb_domain = QComboBox()
        self.cb_domain.addItems(["(Select domain)", "Technology", "Health", "Education", "Entertainment"])
        self.cb_domain.setMinimumHeight(36)
        settings_layout.addWidget(self.cb_domain, 0, 1)
        
        # Topic
        settings_layout.addWidget(QLabel("Topic:"), 0, 2)
        self.cb_topic = QComboBox()
        self.cb_topic.addItems(["(Select topic after domain)"])
        self.cb_topic.setMinimumHeight(36)
        settings_layout.addWidget(self.cb_topic, 0, 3)
        
        layout.addWidget(settings_group)
        
        # === Optional Features ===
        features_group = QGroupBox("🎯 Optional Features")
        features_group.setFont(FONT_H2)
        features_layout = QVBoxLayout(features_group)
        features_layout.setSpacing(8)
        
        self.chk_video = QCheckBox("🎬 Generate Video")
        self.chk_video.setFont(FONT_BODY)
        features_layout.addWidget(self.chk_video)
        
        self.chk_voice = QCheckBox("🎤 Generate Voice")
        self.chk_voice.setFont(FONT_BODY)
        features_layout.addWidget(self.chk_voice)
        
        layout.addWidget(features_group)
        
        # === Actions ===
        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)
        
        self.btn_generate = CompactButton("🚀 Generate Video (3 steps)")
        self.btn_generate.setObjectName("btn_success")
        self.btn_generate.setMinimumHeight(48)
        self.btn_generate.setFont(QFont("Segoe UI", 15, QFont.Bold))
        actions_row.addWidget(self.btn_generate, 2)
        
        self.btn_stop = CompactButton("⏹ Stop")
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setMinimumHeight(48)
        self.btn_stop.setFont(QFont("Segoe UI", 14, QFont.Bold))
        actions_row.addWidget(self.btn_stop, 1)
        
        layout.addLayout(actions_row)
        
        # Quick actions
        quick_row = create_button_row(
            ("📂 Open Project Folder", "btn_warning"),
            ("➕ New Project", "btn_primary")
        )
        layout.addWidget(quick_row)
        
        # === Console ===
        console_group = QGroupBox("📋 Console Output")
        console_group.setFont(FONT_H2)
        console_layout = QVBoxLayout(console_group)
        
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setMinimumHeight(150)
        self.txt_console.setFont(QFont("Courier New", 11))
        self.txt_console.setStyleSheet("""
            QTextEdit {
                background: #1E1E1E;
                color: #D4D4D4;
                border: 2px solid #333;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self.txt_console.setPlaceholderText("[INFO] Console output will appear here...")
        console_layout.addWidget(self.txt_console)
        
        layout.addWidget(console_group)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)