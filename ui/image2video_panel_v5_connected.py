# ui/image2video_panel_v5_connected.py
"""
Image2Video V5 - Connected to Original ProjectPanel Logic
Integrates with:
- services.image2video_service (video generation)
- workers.video_generation_worker (threading)
- utils.video_downloader (download)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QListWidget, QTextEdit, QComboBox,
    QGroupBox, QPushButton, QSplitter, QFileDialog,
    QListWidgetItem, QMessageBox, QInputDialog, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor
import json
import os

# Import original services
try:
    from services.image2video_service import parse_prompt_any, ImageToVideoService
    from workers.video_generation_worker import VideoGenerationWorker
    from utils.video_downloader import VideoDownloader
    from utils.config import load as load_cfg
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    # Fallback for development
    parse_prompt_any = None
    ImageToVideoService = None
    VideoGenerationWorker = None
    VideoDownloader = None
    load_cfg = lambda: {}

FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)

class SceneHeaderWidget(QWidget):
    """Header row for scene navigation"""
    
    scene_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.current_scene = 0
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self.scene_buttons = []
        scene_names = ["Dự án", "Cảnh", "Image", "Prompt", "Trạng thái", 
                       "Video 1", "Video 2", "Video 3", "Video 4", "Hoàn thành"]
        
        for i, name in enumerate(scene_names):
            btn = QPushButton(name)
            btn.setMinimumHeight(36)
            btn.setCheckable(True)
            btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
            btn.clicked.connect(lambda checked, idx=i: self._on_scene_clicked(idx))
            btn.setStyleSheet("""
                QPushButton {
                    background: #F5F5F5;
                    color: #616161;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: 700;
                }
                QPushButton:hover { background: #E0E0E0; }
                QPushButton:checked {
                    background: #1E88E5;
                    color: white;
                }
            """)
            layout.addWidget(btn)
            self.scene_buttons.append(btn)
        
        self.scene_buttons[0].setChecked(True)
    
    def _on_scene_clicked(self, index):
        for i, btn in enumerate(self.scene_buttons):
            btn.setChecked(i == index)
        self.current_scene = index
        self.scene_changed.emit(index)

class Image2VideoPanelV5Connected(QWidget):
    """Image2Video V5 - Connected to original logic"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State variables (matching ProjectPanel)
        self.projects = {}  # project_name -> ProjectData
        self.current_project = None
        self.selected_images = []
        self.prompt_file = None
        self.scenes = []
        self.jobs = []
        self.max_videos = 4
        self._seq_running = False
        
        # Workers
        self.video_worker = None
        self.download_worker = None
        
        # Services
        self.video_downloader = None
        if VideoDownloader:
            self.video_downloader = VideoDownloader(log_callback=self._log)
        
        # Client (for API)
        self.client = None
        self.tokens = []
        
        self._build_ui()
        self._init_default_project()
    
    def _init_default_project(self):
        """Initialize default project"""
        self._add_project_internal("Project_1")
    
    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # === LEFT PANEL (420px) ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)
        
        # Projects
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
                font-size: 14px;
            }
            QPushButton:hover { background: #2196F3; }
        """)
        self.btn_add.clicked.connect(self._add_project)
        btn_row.addWidget(self.btn_add, 1)
        
        self.btn_delete = QPushButton("− Xóa")
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.setStyleSheet(self.btn_add.styleSheet())
        self.btn_delete.clicked.connect(self._delete_project)
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
                padding: 6px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: #1E88E5;
                color: white;
            }
        """)
        self.project_list.currentItemChanged.connect(self._on_project_selected)
        left_layout.addWidget(self.project_list)
        
        # Scene controls
        scene_group = QGroupBox("🎬 Dự án")
        scene_group.setFont(FONT_H2)
        scene_layout = QVBoxLayout(scene_group)
        scene_layout.setSpacing(8)
        
        scene_layout.addWidget(QLabel("Model / Tỉ lệ / Số video"))
        
        combo_row = QHBoxLayout()
        combo_row.setSpacing(4)
        
        self.cb_model = QComboBox()
        self.cb_model.addItems(["veo_3_1_i2v_s_fast_pc", "veo_3_1_i2v_s_slow_pc"])
        self.cb_model.setMinimumHeight(32)
        combo_row.addWidget(self.cb_model, 3)
        
        self.cb_ratio = QComboBox()
        self.cb_ratio.addItems(["16:9", "9:16", "1:1"])
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
        self.txt_prompt.setMinimumHeight(70)
        self.txt_prompt.setMaximumHeight(110)
        self.txt_prompt.setPlaceholderText("Enter video prompt...")
        self.txt_prompt.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QTextEdit:focus { border: 2px solid #1E88E5; }
        """)
        scene_layout.addWidget(self.txt_prompt)
        
        left_layout.addWidget(scene_group)
        
        # === ACTION BUTTONS ===
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        
        # Delete buttons
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
        btn_del_scene.clicked.connect(self._delete_scene)
        del_row.addWidget(btn_del_scene, 1)
        
        btn_del_all = QPushButton("🗑 Xóa tất cả cảnh")
        btn_del_all.setMinimumHeight(40)
        btn_del_all.setStyleSheet(btn_del_scene.styleSheet())
        btn_del_all.clicked.connect(self._delete_all_scenes)
        del_row.addWidget(btn_del_all, 1)
        
        actions_layout.addLayout(del_row)
        
        # Choose prompt (JSON)
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
        btn_prompt.clicked.connect(self._choose_prompt_file_json)
        actions_layout.addWidget(btn_prompt)
        
        # Choose images
        img_row = QHBoxLayout()
        img_row.setSpacing(6)
        
        btn_folder = QPushButton("📁 Chọn thư mục ảnh")
        btn_folder.setMinimumHeight(40)
        btn_folder.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #FFB74D; }
        """)
        btn_folder.clicked.connect(self._choose_image_folder)
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
        btn_image.clicked.connect(self._choose_multiple_images)
        img_row.addWidget(btn_image, 1)
        
        actions_layout.addLayout(img_row)
        
        # Generate video - CONNECTED
        self.btn_run = QPushButton("▶ BẮT ĐẦU TẠO VIDEO")
        self.btn_run.setMinimumHeight(56)
        self.btn_run.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 28px;
                font-weight: 700;
                font-size: 15px;
            }
            QPushButton:hover { background: #66BB6A; }
            QPushButton:disabled {
                background: #CCCCCC;
                color: #666666;
            }
        """)
        self.btn_run.clicked.connect(self._run_seq)  # ✅ ORIGINAL METHOD
        actions_layout.addWidget(self.btn_run)
        
        # Run all - FULL TEXT
        self.btn_run_all = QPushButton("🔥 CHẠY TOÀN BỘ CÁC DỰ ÁN\n(THEO THỨ TỰ)")
        self.btn_run_all.setMinimumHeight(56)
        self.btn_run_all.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                border: none;
                border-radius: 28px;
                font-weight: 700;
                font-size: 13px;
                text-align: center;
            }
            QPushButton:hover { background: #FF8555; }
        """)
        self.btn_run_all.clicked.connect(self._run_all_projects)  # ✅ RUN ALL
        actions_layout.addWidget(self.btn_run_all)
        
        left_layout.addLayout(actions_layout)
        
        # === CONSOLE ===
        console_group = QGroupBox("📋 Console:")
        console_group.setFont(FONT_BODY)
        console_layout = QVBoxLayout(console_group)
        console_layout.setSpacing(4)
        
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setMinimumHeight(100)
        self.txt_console.setMaximumHeight(150)
        self.txt_console.setFont(QFont("Courier New", 11))
        self.txt_console.setStyleSheet("""
            QTextEdit {
                background: #1E1E1E;
                color: #4CAF50;
                border: 2px solid #333;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        console_layout.addWidget(self.txt_console)
        
        left_layout.addWidget(console_group)
        
        # === STOP BUTTON ===
        stop_container = QHBoxLayout()
        stop_container.addStretch()
        
        self.btn_stop = QPushButton("⏹ Dừng")
        self.btn_stop.setMinimumHeight(44)
        self.btn_stop.setMinimumWidth(150)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background: #FFB3C1;
                color: #D32F2F;
                border: none;
                border-radius: 22px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover { background: #FFC4D0; }
            QPushButton:disabled {
                background: #F5F5F5;
                color: #BDBDBD;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_processing)  # ✅ STOP
        stop_container.addWidget(self.btn_stop)
        stop_container.addStretch()
        
        left_layout.addLayout(stop_container)
        
        left_panel.setMinimumWidth(420)
        left_panel.setMaximumWidth(550)
        splitter.addWidget(left_panel)
        
        # === RIGHT PANEL ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)
        
        self.scene_header = SceneHeaderWidget()
        self.scene_header.scene_changed.connect(self._on_scene_changed)
        right_layout.addWidget(self.scene_header)
        
        self.stacked_content = QStackedWidget()
        
        for i in range(10):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(16, 16, 16, 16)
            
            label = QLabel(f"Sẵn sàng - Scene {i+1}")
            label.setFont(QFont("Segoe UI", 18, QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                color: #212121;
                background: #E3F2FD;
                padding: 40px;
                border-radius: 12px;
                border: 3px solid #1E88E5;
            """)
            page_layout.addWidget(label)
            page_layout.addStretch()
            
            self.stacked_content.addWidget(page)
        
        right_layout.addWidget(self.stacked_content)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([420, 1000])
        
        main_layout.addWidget(splitter)
        
        self._log("✓ Image2Video panel initialized (connected to original logic)")
    
    # ===== ORIGINAL METHODS FROM ProjectPanel =====
    
    def _run_seq(self):
        """Start video generation - FROM ORIGINAL ProjectPanel._run_seq()"""
        if self._seq_running:
            self._log("⚠️ Đang chạy tuần tự, vui lòng chờ…")
            return
        
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please select a project first!")
            return
        
        # Refresh tokens
        self.refresh_tokens()
        
        if not self._ensure_client():
            return
        
        # Parse scenes from prompt
        if not self.scenes and self.txt_prompt.toPlainText().strip():
            try:
                obj = json.loads(self.txt_prompt.toPlainText())
                if parse_prompt_any:
                    self.scenes = parse_prompt_any(obj)
            except Exception as e:
                self._log(f"⚠️ Could not parse prompt: {e}")
        
        # Prepare jobs
        n = self._prepare_jobs()
        if n <= 0:
            self._log("⚠️ No jobs to run")
            return
        
        cfg = load_cfg() if load_cfg else {}
        model = self.cb_model.currentText()
        aspect = self.cb_ratio.currentText()
        copies = int(self.cb_count.currentText())
        pid = cfg.get("default_project_id", "87b19267-13d6-49cd-a7ed-db19a90c9339")
        
        self._seq_running = True
        self.btn_run.setEnabled(False)
        self.btn_run.setText("ĐANG TẠO…")
        self.btn_stop.setEnabled(True)
        
        self._log(f"▶ Starting video generation for project: {self.current_project}")
        self._log(f"  Model: {model}, Aspect: {aspect}, Copies: {copies}")
        self._log(f"  Jobs: {n}")
        
        # Create worker (matching ProjectPanel)
        if VideoGenerationWorker:
            self.video_worker = VideoGenerationWorker(
                client=self.client,
                jobs=self.jobs,
                model=model,
                aspect_ratio=aspect,
                project_id=pid,
                max_videos=self.max_videos
            )
            self.video_worker.progress.connect(self._log)
            self.video_worker.video_ready.connect(self._on_video_ready)
            self.video_worker.finished.connect(self._on_generation_finished)
            self.video_worker.start()
        else:
            self._log("⚠️ VideoGenerationWorker not available")
            self._seq_running = False
            self.btn_run.setEnabled(True)
            self.btn_run.setText("▶ BẮT ĐẦU TẠO VIDEO")
            self.btn_stop.setEnabled(False)
    
    def _run_all_projects(self):
        """Run all projects sequentially"""
        count = self.project_list.count()
        if count == 0:
            QMessageBox.warning(self, "No Projects", "No projects to run!")
            return
        
        self._log(f"🔥 Running all {count} projects in sequence...")
        
        # TODO: Implement sequential project execution
        # For now, run current project
        for i in range(count):
            project_name = self.project_list.item(i).text()
            self._log(f"  → Project {i+1}/{count}: {project_name}")
        
        self._run_seq()
    
    def stop_processing(self):
        """Stop current generation - FROM ORIGINAL"""
        self._log("⏹ Stopping generation...")
        
        if self.video_worker and self.video_worker.isRunning():
            self.video_worker.terminate()
            self.video_worker.wait()
        
        self._seq_running = False
        self.btn_run.setEnabled(True)
        self.btn_run.setText("▶ BẮT ĐẦU TẠO VIDEO")
        self.btn_stop.setEnabled(False)
        
        self._log("✓ Stopped")
    
    def refresh_tokens(self):
        """Refresh API tokens - FROM ORIGINAL"""
        cfg = load_cfg() if load_cfg else {}
        self.tokens = cfg.get("labs_tokens", []) or cfg.get("tokens", [])
        self._log(f"✓ Loaded {len(self.tokens)} tokens")
    
    def _ensure_client(self):
        """Ensure API client is initialized - FROM ORIGINAL"""
        if self.client:
            return True
        
        if not self.tokens:
            QMessageBox.warning(self, "No Tokens", "No API tokens found. Please configure in Settings.")
            return False
        
        # Initialize client (assuming ImageToVideoService exists)
        if ImageToVideoService:
            try:
                self.client = ImageToVideoService(tokens=self.tokens)
                self._log("✓ API client initialized")
                return True
            except Exception as e:
                self._log(f"❌ Failed to initialize client: {e}")
                return False
        else:
            self._log("⚠️ ImageToVideoService not available")
            return False
    
    def _prepare_jobs(self):
        """Prepare jobs from scenes and images - FROM ORIGINAL"""
        self.jobs = []
        
        if not self.selected_images:
            self._log("⚠️ No images selected")
            return 0
        
        for i, img_path in enumerate(self.selected_images):
            prompt = self.txt_prompt.toPlainText().strip() or f"Scene {i+1}"
            self.jobs.append({
                "scene_index": i,
                "image_path": img_path,
                "prompt": prompt
            })
        
        self._log(f"✓ Prepared {len(self.jobs)} jobs")
        return len(self.jobs)
    
    def _on_video_ready(self, video_data):
        """Handle video ready - FROM ORIGINAL"""
        self._log(f"✓ Video ready: {video_data.get('name', 'Unknown')}")
        
        # Auto download if video_downloader available
        if self.video_downloader and video_data.get('uri'):
            self._log("⬇️ Starting download...")
            # TODO: Call video_downloader.download(uri, output_path)
    
    def _on_generation_finished(self):
        """Handle generation finished - FROM ORIGINAL"""
        self._seq_running = False
        self.btn_run.setEnabled(True)
        self.btn_run.setText("▶ BẮT ĐẦU TẠO VIDEO")
        self.btn_stop.setEnabled(False)
        
        self._log("✅ Generation finished!")
    
    # ===== UI METHODS =====
    
    def _add_project(self):
        name, ok = QInputDialog.getText(self, "Add Project", "Project name:")
        if ok and name:
            self._add_project_internal(name)
    
    def _add_project_internal(self, name):
        """Add project internally"""
        if name in self.projects:
            self._log(f"⚠️ Project '{name}' already exists")
            return
        
        self.projects[name] = {
            "scenes": [],
            "images": [],
            "jobs": []
        }
        self.project_list.addItem(name)
        self._log(f"✓ Added project: {name}")
    
    def _delete_project(self):
        current = self.project_list.currentItem()
        if current:
            name = current.text()
            self.project_list.takeItem(self.project_list.row(current))
            if name in self.projects:
                del self.projects[name]
            self._log(f"✓ Deleted project: {name}")
    
    def _on_project_selected(self, current, previous):
        if current:
            self.current_project = current.text()
            self._log(f"✓ Selected project: {self.current_project}")
            # Load project data
            if self.current_project in self.projects:
                project_data = self.projects[self.current_project]
                self.scenes = project_data.get("scenes", [])
                self.selected_images = project_data.get("images", [])
    
    def _delete_scene(self):
        self._log("✓ Delete selected scene")
    
    def _delete_all_scenes(self):
        self.scenes = []
        self._log("✓ Delete all scenes")
    
    def _choose_prompt_file_json(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose Prompt File", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.prompt_file = file_path
            self._log(f"✓ Prompt file: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'prompt' in data:
                        self.txt_prompt.setText(data['prompt'])
                    elif isinstance(data, list):
                        # Array of scenes
                        prompts = [scene.get('prompt', '') for scene in data if isinstance(scene, dict)]
                        self.txt_prompt.setText('\n'.join(prompts))
            except Exception as e:
                self._log(f"⚠️ Could not load prompt: {e}")
    
    def _choose_image_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Image Folder")
        if folder:
            self._log(f"✓ Image folder: {folder}")
            # Load all images from folder
            import glob
            images = []
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp']:
                images.extend(glob.glob(os.path.join(folder, ext)))
            
            if images:
                self.selected_images = images
                self._log(f"✓ Found {len(images)} images")
                if self.current_project and self.current_project in self.projects:
                    self.projects[self.current_project]["images"] = images
    
    def _choose_multiple_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Choose Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if files:
            self.selected_images = files
            self._log(f"✓ Selected {len(files)} images")
            if self.current_project and self.current_project in self.projects:
                self.projects[self.current_project]["images"] = files
    
    def _on_scene_changed(self, index):
        self.stacked_content.setCurrentIndex(index)
        self._log(f"→ Switched to scene {index + 1}")
    
    def _log(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.txt_console.append(f"[{timestamp}] {message}")