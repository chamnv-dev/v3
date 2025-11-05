# -*- coding: utf-8 -*-
"""
Image2Video Panel V3 Merged - Projects + Controls in ONE column
Rounded buttons like design mockup
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QTextEdit, QComboBox,
    QGroupBox, QPushButton, QTabWidget, QSplitter,
    QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

# Typography
FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)

class Image2VideoPanelV3Merged(QWidget):
    """Image2Video V3 - Merged left panel with rounded buttons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # === LEFT PANEL (250-350px) - All controls ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)
        
        # Projects section
        proj_label = QLabel("📁 Dự án")
        proj_label.setFont(FONT_H2)
        left_layout.addWidget(proj_label)
        
        # Add/Delete buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        
        self.btn_add = QPushButton("+ Thêm")
        self.btn_add.setMinimumHeight(36)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 18px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        btn_row.addWidget(self.btn_add, 1)
        
        self.btn_delete = QPushButton("− Xóa")
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 18px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        btn_row.addWidget(self.btn_delete, 1)
        
        left_layout.addLayout(btn_row)
        
        # Project list
        self.project_list = QListWidget()
        self.project_list.setMaximumHeight(150)
        self.project_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: #1E88E5;
                color: white;
            }
        """)
        self.project_list.addItem("Project_1")
        left_layout.addWidget(self.project_list)
        
        # === Scene Controls (same column) ===
        scene_group = QGroupBox("🎬 Dự án")
        scene_group.setFont(FONT_H2)
        scene_layout = QVBoxLayout(scene_group)
        scene_layout.setSpacing(6)
        
        # Model / Ratio / Count
        scene_layout.addWidget(QLabel("Model / Tỉ lệ / Số video"))
        
        combo_row = QHBoxLayout()
        combo_row.setSpacing(4)
        
        self.cb_model = QComboBox()
        self.cb_model.addItems(["veo_3_1_i2v_s_fast_pc", "veo_3_1_i2v_s_slow_pc"])
        self.cb_model.setMinimumHeight(32)
        combo_row.addWidget(self.cb_model, 3)
        
        self.cb_ratio = QComboBox()
        self.cb_ratio.addItems(["VIDEO_ASPECT_RATIO_16_9", "VIDEO_ASPECT_RATIO_9_16", "VIDEO_ASPECT_RATIO_1_1"])
        self.cb_ratio.setMinimumHeight(32)
        combo_row.addWidget(self.cb_ratio, 2)
        
        self.cb_count = QComboBox()
        self.cb_count.addItems(["4", "2", "1"])
        self.cb_count.setMinimumHeight(32)
        combo_row.addWidget(self.cb_count, 1)
        
        scene_layout.addLayout(combo_row)
        
        # Prompt
        scene_layout.addWidget(QLabel("Prompt (nhập hoặc hiển thị từ file)"))
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setMinimumHeight(60)
        self.txt_prompt.setMaximumHeight(100)
        self.txt_prompt.setPlaceholderText("Enter video prompt...")
        self.txt_prompt.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #1E88E5;
            }
        """)
        scene_layout.addWidget(self.txt_prompt)
        
        left_layout.addWidget(scene_group)
        
        # === ACTION BUTTONS (ROUNDED) ===
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        
        # Delete scene buttons
        del_row = QHBoxLayout()
        del_row.setSpacing(6)
        
        btn_del_scene = QPushButton("🗑 Xóa cảnh đã chọn")
        btn_del_scene.setMinimumHeight(40)
        btn_del_scene.setStyleSheet("""
            QPushButton {
                background: #F44336;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #E57373; }
        """)
        del_row.addWidget(btn_del_scene, 1)
        
        btn_del_all = QPushButton("🗑 Xóa tất cả cảnh")
        btn_del_all.setMinimumHeight(40)
        btn_del_all.setStyleSheet("""
            QPushButton {
                background: #F44336;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #E57373; }
        """)
        del_row.addWidget(btn_del_all, 1)
        
        actions_layout.addLayout(del_row)
        
        # Choose prompt file
        btn_prompt = QPushButton("📄 Chọn file prompt")
        btn_prompt.setMinimumHeight(48)
        btn_prompt.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 24px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        actions_layout.addWidget(btn_prompt)
        
        # Choose images
        img_row = QHBoxLayout()
        img_row.setSpacing(6)
        
        btn_folder = QPushButton("📁 Chọn thư mục ảnh")
        btn_folder.setMinimumHeight(40)
        btn_folder.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        img_row.addWidget(btn_folder, 1)
        
        btn_image = QPushButton("🖼 Chọn ảnh lẻ")
        btn_image.setMinimumHeight(40)
        btn_image.setStyleSheet("""
            QPushButton {
                background: #1E88E5;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        img_row.addWidget(btn_image, 1)
        
        actions_layout.addLayout(img_row)
        
        # Generate video - BIG GREEN BUTTON
        btn_generate = QPushButton("▶ BẮT ĐẦU TẠO VIDEO")
        btn_generate.setMinimumHeight(56)
        btn_generate.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 28px;
                font-weight: 700;
                font-size: 15px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover { background: #66BB6A; }
            QPushButton:pressed { background: #388E3C; }
        """)
        actions_layout.addWidget(btn_generate)
        
        # Stop button - RIGHT ALIGNED
        stop_row = QHBoxLayout()
        stop_row.addStretch()
        
        btn_stop = QPushButton("⏹ Dừng")
        btn_stop.setMinimumHeight(40)
        btn_stop.setMinimumWidth(120)
        btn_stop.setStyleSheet("""
            QPushButton {
                background: #FFB3C1;
                color: #D32F2F;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover { background: #FFC4D0; }
        """)
        stop_row.addWidget(btn_stop)
        
        actions_layout.addLayout(stop_row)
        
        # Run all projects - BIG ORANGE BUTTON
        btn_run_all = QPushButton("🔥 CHẠY TOÀN BỘ CÁC DỰ ÁN (THEO THỨ TỰ)")
        btn_run_all.setMinimumHeight(48)
        btn_run_all.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                border: none;
                border-radius: 24px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover { background: #FF8555; }
        """)
        actions_layout.addWidget(btn_run_all)
        
        left_layout.addLayout(actions_layout)
        left_layout.addStretch()
        
        left_panel.setMinimumWidth(250)
        left_panel.setMaximumWidth(400)
        splitter.addWidget(left_panel)
        
        # === RIGHT PANEL - Scene Tabs with COLORS ===
        right_tabs = QTabWidget()
        right_tabs.setFont(QFont("Segoe UI", 13, QFont.Bold))
        
        # Tab data with colors
        tab_data = [
            ("Dự án", "#1E88E5"),
            ("Cảnh", "#4CAF50"),
            ("Image", "#FF9800"),
            ("Prompt", "#9C27B0"),
            ("Trạng thái", "#F44336"),
            ("Video 1", "#00BCD4"),
            ("Video 2", "#FFC107"),
            ("Video 3", "#E91E63"),
            ("Video 4", "#3F51B5"),
            ("Hoàn thành", "#4CAF50")
        ]
        
        for i, (tab_name, color) in enumerate(tab_data):
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(12, 12, 12, 12)
            
            # Content label
            content_label = QLabel(f"Sẵn sàng - {tab_name}")
            content_label.setFont(QFont("Segoe UI", 14))
            content_label.setAlignment(Qt.AlignCenter)
            content_label.setStyleSheet(f"color: {color}; padding: 20px;")
            tab_layout.addWidget(content_label)
            tab_layout.addStretch()
            
            right_tabs.addTab(tab_widget, tab_name)
            
            # Set tab text color
            right_tabs.tabBar().setTabTextColor(i, QColor(color))
        
        # Tab styling
        right_tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 70px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 700;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
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
        
        splitter.addWidget(right_tabs)
        
        # Set splitter sizes
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)