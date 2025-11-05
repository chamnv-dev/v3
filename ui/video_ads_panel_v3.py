# ui/video_ads_panel_v3.py
"""
Video Ads V3 - Same design as Text2Video
- Rounded buttons
- Colored tabs
- Compact left panel
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QGroupBox, QGridLayout, QScrollArea, QFrame, QTabWidget,
    QPushButton, QRadioButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)

class VideoAdsPanelV3(QWidget):
    """Video Ads V3 - Matching Text2Video style"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # === LEFT PANEL ===
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setMinimumWidth(300)
        left_scroll.setMaximumWidth(450)
        
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
        proj_layout.addWidget(self.ed_project)
        
        proj_layout.addWidget(QLabel("Ý tưởng:"))
        self.txt_idea = QTextEdit()
        self.txt_idea.setMinimumHeight(80)
        self.txt_idea.setMaximumHeight(120)
        self.txt_idea.setPlaceholderText("Nhập ý tưởng cho video...")
        proj_layout.addWidget(self.txt_idea)
        
        left_layout.addWidget(proj_group)
        
        # Settings
        settings_group = QGroupBox("⚙️ Cài đặt nội dung")
        settings_group.setFont(FONT_H2)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(6)
        
        self.chk_persona = QCheckBox("👤 Thông tin người mẫu")
        settings_layout.addWidget(self.chk_persona)
        
        self.chk_product = QCheckBox("📦 Ảnh sản phẩm")
        settings_layout.addWidget(self.chk_product)
        
        self.chk_video = QCheckBox("🎬 Cài đặt video")
        settings_layout.addWidget(self.chk_video)
        
        left_layout.addWidget(settings_group)
        
        # === ACTION BUTTONS (ROUNDED like image) ===
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        
        # Row 1: Write script + Generate image + Video
        row1 = QHBoxLayout()
        row1.setSpacing(6)
        
        btn_write = QPushButton("📝 Viết kịch bản")
        btn_write.setMinimumHeight(44)
        btn_write.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                border-radius: 22px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #FF8555; }
        """)
        row1.addWidget(btn_write, 1)
        
        actions_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.setSpacing(6)
        
        btn_image = QPushButton("🖼️ Tạo ảnh")
        btn_image.setMinimumHeight(44)
        btn_image.setStyleSheet("""
            QPushButton {
                background: #BDBDBD;
                color: #424242;
                border-radius: 22px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #D0D0D0; }
        """)
        row2.addWidget(btn_image, 1)
        
        btn_video = QPushButton("🎥 Video")
        btn_video.setMinimumHeight(44)
        btn_video.setStyleSheet("""
            QPushButton {
                background: #9C27B0;
                color: white;
                border-radius: 22px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #AB47BC; }
        """)
        row2.addWidget(btn_video, 1)
        
        actions_layout.addLayout(row2)
        
        # Big button: Run all
        btn_run_all = QPushButton("🔥 Tạo video tự động (3 bước)")
        btn_run_all.setMinimumHeight(56)
        btn_run_all.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                border-radius: 28px;
                font-weight: 700;
                font-size: 15px;
            }
            QPushButton:hover { background: #FF8555; }
        """)
        actions_layout.addWidget(btn_run_all)
        
        # Stop button
        stop_row = QHBoxLayout()
        stop_row.addStretch()
        btn_stop = QPushButton("⏹ Dừng")
        btn_stop.setMinimumHeight(44)
        btn_stop.setMinimumWidth(140)
        btn_stop.setStyleSheet("""
            QPushButton {
                background: #FFB3C1;
                color: #D32F2F;
                border-radius: 22px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover { background: #FFC4D0; }
        """)
        stop_row.addWidget(btn_stop)
        stop_row.addStretch()
        actions_layout.addLayout(stop_row)
        
        left_layout.addLayout(actions_layout)
        left_layout.addStretch()
        
        left_scroll.setWidget(left_container)
        layout.addWidget(left_scroll)
        
        # === RIGHT PANEL - COLORED TABS ===
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
            tab_layout.setContentsMargins(12, 12, 12, 12)
            
            content = QTextEdit()
            content.setPlaceholderText(f"{tab_name} content...")
            content.setStyleSheet(f"""
                QTextEdit {{
                    background: white;
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            tab_layout.addWidget(content)
            
            right_tabs.addTab(tab_widget, tab_name)
            right_tabs.tabBar().setTabTextColor(i, QColor(color))
        
        right_tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 100px;
                padding: 10px 16px;
                font-weight: 700;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 3px solid;
            }
            QTabBar::tab:!selected {
                background: #F5F5F5;
            }
        """)
        
        layout.addWidget(right_tabs, 1)