# -*- coding: utf-8 -*-
"""
Image2Video Panel V2 - Complete Redesign
- Compact project sidebar (250px instead of 350px)
- Better scene tab layout
- Responsive design
- 8px spacing grid
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QPushButton, QTabWidget, QLabel,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QGroupBox, QGridLayout, QScrollArea, QFrame,
    QListWidgetItem, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from ui.widgets.compact_button import CompactButton, create_button_row

# Typography
FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)
FONT_SMALL = QFont("Segoe UI", 12)

class ProjectListWidget(QWidget):
    """Compact project list sidebar"""
    
    project_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("📁 Projects")
        title.setFont(FONT_H2)
        layout.addWidget(title)
        
        # Action buttons (horizontal)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        
        self.btn_add = CompactButton("➕")
        self.btn_add.setObjectName("btn_success")
        self.btn_add.setFixedSize(36, 36)
        self.btn_add.setToolTip("Add Project")
        btn_row.addWidget(self.btn_add)
        
        self.btn_delete = CompactButton("🗑")
        self.btn_delete.setObjectName("btn_danger")
        self.btn_delete.setFixedSize(36, 36)
        self.btn_delete.setToolTip("Delete Project")
        btn_row.addWidget(self.btn_delete)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # Project list
        self.list_widget = QListWidget()
        self.list_widget.setFont(FONT_BODY)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: white;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background: #F5F5F5;
            }
            QListWidget::item:selected {
                background: #1E88E5;
                color: white;
            }
        """)
        self.list_widget.itemClicked.connect(
            lambda item: self.project_selected.emit(item.text())
        )
        layout.addWidget(self.list_widget)
        
        # Run all button
        self.btn_run_all = CompactButton("▶ Run All")
        self.btn_run_all.setObjectName("btn_success")
        self.btn_run_all.setMinimumHeight(36)
        self.btn_run_all.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(self.btn_run_all)
    
    def add_project(self, name):
        """Add project to list"""
        item = QListWidgetItem(name)
        self.list_widget.addItem(item)
    
    def get_selected_project(self):
        """Get selected project name"""
        item = self.list_widget.currentItem()
        return item.text() if item else None

class SceneTab(QWidget):
    """Individual scene tab with compact layout"""
    
    def __init__(self, scene_num, parent=None):
        super().__init__(parent)
        self.scene_num = scene_num
        self._build_ui()
    
    def _build_ui(self):
        # Scroll area for responsiveness
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # === Scene Controls Group ===
        controls_group = QGroupBox("🎬 Scene Controls")
        controls_group.setFont(FONT_H2)
        controls_layout = QGridLayout(controls_group)
        controls_layout.setVerticalSpacing(8)
        controls_layout.setHorizontalSpacing(12)
        
        # Model selector
        controls_layout.addWidget(QLabel("Model:"), 0, 0)
        self.cb_model = QComboBox()
        self.cb_model.addItems(["veo_3_1_i2v_s_fast_pc", "veo_3_1_i2v_s_slow_pc"])
        self.cb_model.setMinimumHeight(32)
        controls_layout.addWidget(self.cb_model, 0, 1, 1, 2)
        
        # Aspect ratio
        controls_layout.addWidget(QLabel("Aspect Ratio:"), 1, 0)
        self.cb_ratio = QComboBox()
        self.cb_ratio.addItems(["VIDEO_ASPECT_RATIO_16_9", "VIDEO_ASPECT_RATIO_9_16", "VIDEO_ASPECT_RATIO_1_1"])
        self.cb_ratio.setMinimumHeight(32)
        controls_layout.addWidget(self.cb_ratio, 1, 1, 1, 2)
        
        # Video count
        controls_layout.addWidget(QLabel("Videos:"), 2, 0)
        self.cb_count = QComboBox()
        self.cb_count.addItems(["1", "2", "3", "4"])
        self.cb_count.setMinimumHeight(32)
        controls_layout.addWidget(self.cb_count, 2, 1)
        
        layout.addWidget(controls_group)
        
        # === Prompt Group ===
        prompt_group = QGroupBox("✍️ Prompt")
        prompt_group.setFont(FONT_H2)
        prompt_layout = QVBoxLayout(prompt_group)
        prompt_layout.setSpacing(8)
        
        hint = QLabel("Describe the video motion and action")
        hint.setFont(FONT_SMALL)
        hint.setStyleSheet("color: #757575; font-style: italic;")
        prompt_layout.addWidget(hint)
        
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setMinimumHeight(100)
        self.txt_prompt.setMaximumHeight(150)
        self.txt_prompt.setFont(FONT_BODY)
        self.txt_prompt.setPlaceholderText("Enter video prompt here...")
        self.txt_prompt.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #1E88E5;
                background: #F8FCFF;
            }
        """)
        prompt_layout.addWidget(self.txt_prompt)
        
        layout.addWidget(prompt_group)
        
        # === Reference Image Group ===
        image_group = QGroupBox("🖼️ Reference Image")
        image_group.setFont(FONT_H2)
        image_layout = QVBoxLayout(image_group)
        image_layout.setSpacing(8)
        
        image_buttons = create_button_row(
            ("📁 Choose Folder", "btn_warning"),
            ("🖼️ Choose Image", "btn_primary")
        )
        image_layout.addWidget(image_buttons)
        
        self.lbl_image = QLabel("No image selected")
        self.lbl_image.setFont(FONT_SMALL)
        self.lbl_image.setStyleSheet("color: #757575; padding: 8px; background: #F5F5F5; border-radius: 4px;")
        self.lbl_image.setWordWrap(True)
        image_layout.addWidget(self.lbl_image)
        
        layout.addWidget(image_group)
        
        # === Actions ===
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)
        
        self.btn_generate = CompactButton("🎬 Generate Video")
        self.btn_generate.setObjectName("btn_success")
        self.btn_generate.setMinimumHeight(40)
        self.btn_generate.setFont(QFont("Segoe UI", 14, QFont.Bold))
        actions_row.addWidget(self.btn_generate, 1)
        
        self.btn_stop = CompactButton("⏹ Stop")
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setMinimumHeight(40)
        actions_row.addWidget(self.btn_stop)
        
        layout.addLayout(actions_row)
        
        # Status
        self.lbl_status = QLabel("")
        self.lbl_status.setFont(FONT_SMALL)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("padding: 8px; background: #F5F5F5; border-radius: 4px;")
        layout.addWidget(self.lbl_status)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

class Image2VideoPanelV2(QWidget):
    """Image2Video Panel V2 - Redesigned"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Project list (250px default, compact)
        self.project_list = ProjectListWidget()
        self.project_list.setMinimumWidth(200)
        self.project_list.setMaximumWidth(350)
        splitter.addWidget(self.project_list)
        
        # Right: Scene tabs
        self.scene_tabs = QTabWidget()
        self.scene_tabs.setFont(FONT_BODY)
        self.scene_tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 80px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        
        # Add 4 scene tabs
        for i in range(1, 5):
            scene_tab = SceneTab(i)
            self.scene_tabs.addTab(scene_tab, f"Scene {i}")
        
        splitter.addWidget(self.scene_tabs)
        
        # Set splitter sizes (250px left, rest right)
        splitter.setSizes([250, 800])
        
        layout.addWidget(splitter)
        
        # Load sample projects
        self._load_sample_projects()
    
    def _load_sample_projects(self):
        """Load sample projects"""
        self.project_list.add_project("Project_1")
        self.project_list.add_project("My Video Project")
        self.project_list.add_project("Test Scene")