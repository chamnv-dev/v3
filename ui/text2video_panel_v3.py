# ui/text2video_panel_v3.py
"""
Text2Video V3 - Complete Redesign
- "Bạn là chuyên gia trong" prefix
- Larger font for domain/topic (+2px)
- Stop button full text
- Colored scene tabs
- Rounded buttons
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QGroupBox, QGridLayout, QScrollArea, QFrame, QTabWidget,
    QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

# Typography
FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)
FONT_LARGE = QFont("Segoe UI", 15)  # +2px for domain/topic

def _prominent_input(placeholder="", multiline=False, height=36):
    """Create prominent input"""
    if multiline:
        widget = QTextEdit()
        widget.setMinimumHeight(100)
        widget.setMaximumHeight(150)
    else:
        widget = QLineEdit()
        widget.setMinimumHeight(height)
        widget.setMaximumHeight(height)
    
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

class Text2VideoPanelV3(QWidget):
    """Text2Video Panel V3 - Full Redesign"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        # Main horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # === LEFT PANEL (400px) ===
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setMinimumWidth(350)
        left_scroll.setMaximumWidth(500)
        
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(12)
        
        # Project section
        proj_group = QGroupBox("📁 Dự án")
        proj_group.setFont(FONT_H2)
        proj_layout = QVBoxLayout(proj_group)
        proj_layout.setSpacing(8)
        
        proj_layout.addWidget(QLabel("Tên dự án:"))
        self.ed_project_name = _prominent_input("Nhập tên dự án (để trống sẽ tự tạo)")
        proj_layout.addWidget(self.ed_project_name)
        
        proj_layout.addWidget(QLabel("Ý tưởng (đoạn văn):"))
        self.txt_idea = _prominent_input("Nhập ý tưởng thô (<10 tự)...", multiline=True)
        proj_layout.addWidget(self.txt_idea)
        
        left_layout.addWidget(proj_group)
        
        # Domain & Topic with PREFIX
        domain_group = QGroupBox("🎯 Lĩnh vực và Chủ đề")
        domain_group.setFont(FONT_H2)
        domain_layout = QVBoxLayout(domain_group)
        domain_layout.setSpacing(8)
        
        # Domain with prefix
        domain_row = QHBoxLayout()
        domain_row.setSpacing(8)
        prefix_label = QLabel("Bạn là chuyên gia trong")
        prefix_label.setFont(FONT_LARGE)  # +2px
        prefix_label.setStyleSheet("color: #1E88E5; font-weight: 600;")
        domain_row.addWidget(prefix_label)
        
        self.cb_domain = QComboBox()
        self.cb_domain.setFont(FONT_LARGE)  # +2px
        self.cb_domain.addItems(["(Không chọn)", "Technology", "Health", "Education", "Business", "Entertainment"])
        self.cb_domain.setMinimumHeight(40)  # Taller
        self.cb_domain.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #1E88E5;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
                font-weight: 600;
                color: #1565C0;
            }
        """)
        domain_row.addWidget(self.cb_domain, 1)
        domain_layout.addLayout(domain_row)
        
        # Topic
        topic_row = QHBoxLayout()
        topic_row.setSpacing(8)
        topic_label = QLabel("Chủ đề:")
        topic_label.setFont(FONT_LARGE)  # +2px
        topic_row.addWidget(topic_label)
        
        self.cb_topic = QComboBox()
        self.cb_topic.setFont(FONT_LARGE)  # +2px
        self.cb_topic.addItems(["(Chọn lĩnh vực để load chủ đề)"])
        self.cb_topic.setMinimumHeight(40)
        self.cb_topic.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
                font-weight: 600;
            }
        """)
        topic_row.addWidget(self.cb_topic, 1)
        domain_layout.addLayout(topic_row)
        
        left_layout.addWidget(domain_group)
        
        # Optional features
        features_group = QGroupBox("⚙️ Tùy chọn")
        features_group.setFont(FONT_H2)
        features_layout = QVBoxLayout(features_group)
        features_layout.setSpacing(6)
        
        self.chk_video = QCheckBox("🎬 Cài đặt video")
        self.chk_video.setFont(FONT_BODY)
        features_layout.addWidget(self.chk_video)
        
        self.chk_voice = QCheckBox("🎤 Cài đặt voice")
        self.chk_voice.setFont(FONT_BODY)
        features_layout.addWidget(self.chk_voice)
        
        left_layout.addWidget(features_group)
        
        # === ACTION BUTTONS (ROUNDED like image) ===
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)
        
        # Generate video (3 steps) - BIG ROUNDED BUTTON
        btn_generate = QPushButton("🔥 Tạo video tự động (3 bước)")
        btn_generate.setObjectName("btn_generate_tao")
        btn_generate.setMinimumHeight(56)
        btn_generate.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                border: none;
                border-radius: 28px;
                font-weight: 700;
                font-size: 15px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: #FF8555;
            }
        """)
        actions_layout.addWidget(btn_generate)
        
        # Stop button - FULL TEXT VISIBLE
        stop_row = QHBoxLayout()
        stop_row.addStretch()
        btn_stop = QPushButton("⏹ Dừng")
        btn_stop.setObjectName("btn_stop_dung")
        btn_stop.setMinimumHeight(44)
        btn_stop.setMinimumWidth(140)  # Wide enough for full text
        btn_stop.setStyleSheet("""
            QPushButton {
                background: #FFB3C1;
                color: #D32F2F;
                border: none;
                border-radius: 22px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #FFC4D0;
            }
        """)
        stop_row.addWidget(btn_stop)
        stop_row.addStretch()
        actions_layout.addLayout(stop_row)
        
        # Open folder
        btn_open = QPushButton("📂 Mở thư mục dự án")
        btn_open.setMinimumHeight(44)
        btn_open.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 22px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #2196F3;
            }
        """)
        actions_layout.addWidget(btn_open)
        
        # New project
        btn_new = QPushButton("➕ Tạo dự án mới")
        btn_new.setMinimumHeight(44)
        btn_new.setStyleSheet("""
            QPushButton {
                background: #E0E0E0;
                color: #424242;
                border: none;
                border-radius: 22px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #EEEEEE;
            }
        """)
        actions_layout.addWidget(btn_new)
        
        left_layout.addLayout(actions_layout)
        
        # Console
        console_group = QGroupBox("📋 Console:")
        console_group.setFont(FONT_BODY)
        console_layout = QVBoxLayout(console_group)
        console_layout.setSpacing(4)
        
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setMinimumHeight(120)
        self.txt_console.setFont(QFont("Courier New", 11))
        self.txt_console.setStyleSheet("""
            QTextEdit {
                background: #1E1E1E;
                color: #D4D4D4;
                border: 2px solid #333;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self.txt_console.setPlaceholderText("[INFO] Loaded 6 voices for google")
        console_layout.addWidget(self.txt_console)
        
        left_layout.addWidget(console_group)
        left_layout.addStretch()
        
        left_scroll.setWidget(left_container)
        layout.addWidget(left_scroll)
        
        # === RIGHT PANEL - COLORED TABS ===
        right_tabs = QTabWidget()
        right_tabs.setFont(QFont("Segoe UI", 13, QFont.Bold))
        
        # Tab colors matching image
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
            tab_layout.setContentsMargins(12, 12, 12, 12)
            
            # Content area
            content = QTextEdit()
            content.setPlaceholderText(f"{tab_name} content will appear here...")
            content.setStyleSheet(f"""
                QTextEdit {{
                    background: white;
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 13px;
                }}
            """)
            tab_layout.addWidget(content)
            
            right_tabs.addTab(tab_widget, tab_name)
            
            # Set tab color
            right_tabs.tabBar().setTabTextColor(i, QColor(color))
        
        # Tab bar styling
        right_tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 120px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 700;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 3px solid;
            }
            QTabBar::tab:!selected {
                background: #F5F5F5;
                margin-top: 2px;
            }
        """)
        
        layout.addWidget(right_tabs, 1)