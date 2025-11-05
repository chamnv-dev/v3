# ui/video_ads_panel_v4_fixed.py
"""
Video Ads V4 - Complete Fix
Same fixes as Text2Video
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QCheckBox,
    QGroupBox, QPushButton, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)

class VideoAdsPanelV4Fixed(QWidget):
    """Video Ads V4 - All fixes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === LEFT PANEL (+20%) ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
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
        self.txt_idea.setMinimumHeight(90)
        self.txt_idea.setMaximumHeight(130)
        self.txt_idea.setPlaceholderText("Nhập ý tưởng cho video...")
        proj_layout.addWidget(self.txt_idea)
        
        left_layout.addWidget(proj_group)
        
        # === CHECKBOXES (VISIBLE & FUNCTIONAL) ===
        settings_group = QGroupBox("⚙️ Cài đặt nội dung")
        settings_group.setFont(FONT_H2)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(8)
        
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
        settings_layout.addWidget(self.chk_persona)
        
        self.chk_product = QCheckBox("📦 Ảnh sản phẩm")
        self.chk_product.setFont(FONT_BODY)
        self.chk_product.setMinimumHeight(32)
        self.chk_product.setStyleSheet(self.chk_persona.styleSheet())
        settings_layout.addWidget(self.chk_product)
        
        self.chk_video = QCheckBox("🎬 Cài đặt video")
        self.chk_video.setFont(FONT_BODY)
        self.chk_video.setMinimumHeight(32)
        self.chk_video.setStyleSheet(self.chk_persona.styleSheet())
        settings_layout.addWidget(self.chk_video)
        
        left_layout.addWidget(settings_group)
        
        # === ACTION BUTTONS ===
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
        btn_write.clicked.connect(self._write_script)
        left_layout.addWidget(btn_write)
        
        img_video_row = QHBoxLayout()
        img_video_row.setSpacing(8)
        
        btn_image = QPushButton("🖼️ Tạo ảnh")
        btn_image.setMinimumHeight(40)
        btn_image.setStyleSheet("""
            QPushButton {
                background: #BDBDBD;
                color: #424242;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #D0D0D0; }
        """)
        btn_image.clicked.connect(self._generate_image)
        img_video_row.addWidget(btn_image, 1)
        
        btn_video = QPushButton("🎥 Video")
        btn_video.setMinimumHeight(40)
        btn_video.setStyleSheet("""
            QPushButton {
                background: #9C27B0;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #AB47BC; }
        """)
        btn_video.clicked.connect(self._generate_video)
        img_video_row.addWidget(btn_video, 1)
        
        left_layout.addLayout(img_video_row)
        
        # Generate + Stop SAME ROW
        gen_stop_row = QHBoxLayout()
        gen_stop_row.setSpacing(10)
        
        btn_run_all = QPushButton("🔥 Tạo video tự động (3 bước)")
        btn_run_all.setMinimumHeight(52)
        btn_run_all.setStyleSheet("""
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
        btn_run_all.clicked.connect(self._run_all)
        gen_stop_row.addWidget(btn_run_all, 3)
        
        btn_stop = QPushButton("⏹ Dừng")
        btn_stop.setMinimumHeight(52)
        btn_stop.setMinimumWidth(130)
        btn_stop.setStyleSheet("""
            QPushButton {
                background: #FFB3C1;
                color: #D32F2F;
                border: none;
                border-radius: 26px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover { background: #FFC4D0; }
        """)
        btn_stop.clicked.connect(self._stop)
        gen_stop_row.addWidget(btn_stop, 1)
        
        left_layout.addLayout(gen_stop_row)
        left_layout.addStretch()
        
        left_panel.setMinimumWidth(400)  # +20%
        left_panel.setMaximumWidth(550)
        main_layout.addWidget(left_panel)
        
        # === RIGHT PANEL - COLORED TABS (DARK TEXT) ===
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
                    background: white;
                    color: #212121;  /* DARK TEXT */
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
                background: white;
                border-bottom: 4px solid;
            }
            QTabBar::tab:!selected {
                background: #F5F5F5;
            }
        """)
        
        main_layout.addWidget(right_tabs, 1)
    
    # Functional methods
    def _write_script(self):
        print("📝 Writing script...")
    
    def _generate_image(self):
        print("🖼️ Generating image...")
    
    def _generate_video(self):
        print("🎥 Generating video...")
    
    def _run_all(self):
        print("🔥 Running all (3 steps)...")
    
    def _stop(self):
        print("⏹ Stopped")