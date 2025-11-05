# -*- coding: utf-8 -*-
"""
Settings Panel V2 - COMPLETE FIX
- Fixed text height issues
- Fixed button visibility
- Improved input prominence
- Better spacing
"""

import datetime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QGroupBox, QFileDialog, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt

from ui.widgets.accordion import Accordion
from ui.widgets.compact_button import CompactButton, create_button_row
from ui.widgets.responsive_utils import ElidedLabel, ResponsiveLineEdit
from ui.widgets.key_list_v2 import KeyListV2
from utils import config as cfg
from utils.version import get_version

# Typography System
FONT_H1 = QFont("Segoe UI", 18, QFont.Bold)
FONT_H2 = QFont("Segoe UI", 15, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)
FONT_SMALL = QFont("Segoe UI", 12)
FONT_MONO = QFont("Courier New", 11)

def _ts():
    """Current timestamp"""
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

def _line(placeholder='', read_only=False):
    """Create prominent line edit - FIXED HEIGHT"""
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setFont(QFont("Segoe UI", 13))
    e.setMinimumHeight(36)  # FIXED: 36px minimum
    e.setMaximumHeight(36)  # FIXED: consistent height
    e.setReadOnly(read_only)
    e.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    # Prominent styling
    if not read_only:
        e.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                color: #212121;
            }
            QLineEdit:focus {
                border: 2px solid #1E88E5;
                background: #F8FCFF;
            }
            QLineEdit::placeholder {
                color: #9E9E9E;
                font-style: italic;
            }
        """)
    else:
        e.setStyleSheet("""
            QLineEdit {
                background: #F5F5F5;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px 12px;
                color: #616161;
            }
        """)
    
    return e

def _label(text, bold=False):
    """Create label - FIXED HEIGHT"""
    l = QLabel(text)
    font = QFont("Segoe UI", 13, QFont.Bold if bold else QFont.Normal)
    l.setFont(font)
    l.setMinimumHeight(36)  # FIXED: match input height
    l.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
    return l

class SettingsPanelV2(QWidget):
    """Settings Panel V2 - Complete Fix"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = cfg.load()
        self._build_ui()
    
    def _build_ui(self):
        """Build complete UI with fixes"""
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Container
        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        
        # === ACCOUNT INFO - FIXED ===
        acc_group = QGroupBox("👤 Account Information")
        acc_group.setFont(FONT_H2)
        acc_layout = QGridLayout(acc_group)
        acc_layout.setVerticalSpacing(12)  # More space
        acc_layout.setHorizontalSpacing(16)
        acc_layout.setRowMinimumHeight(0, 40)  # FIXED row height
        acc_layout.setRowMinimumHeight(1, 40)
        acc_layout.setColumnStretch(1, 1)
        acc_layout.setColumnStretch(3, 1)
        
        # Email
        self.ed_email = _line('Email', read_only=True)
        self.ed_email.setText(self.state.get('account_email', ''))
        
        # Hardware ID
        hwid_text = self.state.get('hardware_id', '')
        self.lb_hwid = _label(hwid_text)
        self.lb_hwid.setFont(FONT_MONO)
        self.lb_hwid.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lb_hwid.setStyleSheet("background: #F5F5F5; padding: 8px; border-radius: 4px; border: 1px solid #E0E0E0;")
        
        # Status
        status_text = self.state.get('license_status', 'active')
        self.lb_status = _label(status_text.title())
        if 'active' in status_text.lower() or 'kích' in status_text.lower():
            self.lb_status.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
        else:
            self.lb_status.setStyleSheet("color: #F44336; font-weight: bold; font-size: 14px;")
        
        # Expiry
        expiry_text = self.state.get('license_expiry', 'Không có hạn sử dụng')
        self.lb_expiry = _label(expiry_text)
        
        # Grid layout
        acc_layout.addWidget(_label("Email:", bold=True), 0, 0)
        acc_layout.addWidget(self.ed_email, 0, 1)
        acc_layout.addWidget(_label("Hardware ID:", bold=True), 0, 2)
        acc_layout.addWidget(self.lb_hwid, 0, 3)
        
        acc_layout.addWidget(_label("Status:", bold=True), 1, 0)
        acc_layout.addWidget(self.lb_status, 1, 1)
        acc_layout.addWidget(_label("Expires:", bold=True), 1, 2)
        acc_layout.addWidget(self.lb_expiry, 1, 3)
        
        root.addWidget(acc_group)
        
        # === API CREDENTIALS - FIXED WITH KeyListV2 ===
        api_group = QGroupBox("🔑 API Credentials")
        api_group.setFont(FONT_H2)
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(8)
        
        hint = _label("💡 Click sections to expand. Keys are displayed compactly.")
        hint.setFont(FONT_SMALL)
        hint.setStyleSheet("color: #757575; font-style: italic;")
        hint.setMinimumHeight(24)
        api_layout.addWidget(hint)
        
        self.accordion = Accordion(single_expand=False)
        
        # Google Labs
        labs_section = self.accordion.create_section("Google Labs Token (OAuth)")
        labs_init = self.state.get('labs_tokens') or self.state.get('tokens') or []
        self.w_labs = KeyListV2(title='', kind='google-labs', initial=labs_init)
        labs_section.add_content_widget(self.w_labs)
        
        self.ed_project = _line('Project ID for Flow')
        self.ed_project.setText(self.state.get('flow_project_id', '87b19267-13d6-49cd-a7ed-db19a90c9339'))
        proj_row = QHBoxLayout()
        proj_row.setSpacing(8)
        proj_row.addWidget(_label("Project ID:"))
        proj_row.addWidget(self.ed_project, 1)
        labs_section.add_content_layout(proj_row)
        
        # Elevenlabs
        eleven_section = self.accordion.create_section("Elevenlabs API Keys")
        self.w_eleven = KeyListV2(title='', kind='elevenlabs', 
                                  initial=self.state.get('elevenlabs_api_keys') or [])
        eleven_section.add_content_widget(self.w_eleven)
        
        self.ed_voice = _line('Voice ID')
        self.ed_voice.setText(self.state.get('default_voice_id', '3VnrjnYrskPMDsapTr8X'))
        voice_row = QHBoxLayout()
        voice_row.setSpacing(8)
        voice_row.addWidget(_label("Voice ID:"))
        voice_row.addWidget(self.ed_voice, 1)
        eleven_section.add_content_layout(voice_row)
        
        # Google API
        google_section = self.accordion.create_section("Google API Keys")
        g_list = self.state.get('google_api_keys') or []
        self.w_google = KeyListV2(title='', kind='google', initial=g_list)
        google_section.add_content_widget(self.w_google)
        
        # OpenAI
        openai_section = self.accordion.create_section("OpenAI API Keys")
        self.w_openai = KeyListV2(title='', kind='openai', 
                                  initial=self.state.get('openai_api_keys') or [])
        openai_section.add_content_widget(self.w_openai)
        
        api_layout.addWidget(self.accordion)
        
        # Toggle buttons
        toggle_row = create_button_row(
            ("📂 Expand All", "btn_expand"),
            ("📁 Collapse All", "btn_collapse")
        )
        toggle_row.buttons[0].clicked.connect(self.accordion.expand_all)
        toggle_row.buttons[1].clicked.connect(self.accordion.collapse_all)
        api_layout.addWidget(toggle_row)
        
        root.addWidget(api_group)
        
        # === STORAGE - FIXED ===
        storage_group = QGroupBox("💾 Storage Settings")
        storage_group.setFont(FONT_H2)
        st_layout = QVBoxLayout(storage_group)
        st_layout.setSpacing(12)
        
        # Radio buttons
        radio_row = QHBoxLayout()
        radio_row.setSpacing(16)
        self.rb_local = QRadioButton("📁 Local Storage")
        self.rb_drive = QRadioButton("☁️ Google Drive")
        self.rb_local.setFont(FONT_BODY)
        self.rb_drive.setFont(FONT_BODY)
        storage = (self.state.get('download_storage') or 'local').lower()
        (self.rb_drive if storage == 'gdrive' else self.rb_local).setChecked(True)
        radio_row.addWidget(self.rb_local)
        radio_row.addWidget(self.rb_drive)
        radio_row.addStretch()
        st_layout.addLayout(radio_row)
        
        # Local path - FIXED
        local_row = QHBoxLayout()
        local_row.setSpacing(8)
        self.ed_local = _line('Select download folder...')
        self.ed_local.setText(self.state.get('download_root', ''))
        self.btn_browse = CompactButton("📂 Browse")
        self.btn_browse.setObjectName("btn_browse")
        self.btn_browse.setMinimumWidth(100)
        self.btn_browse.setMinimumHeight(36)  # FIXED
        self.btn_browse.clicked.connect(self._pick_dir)
        local_row.addWidget(_label("Local Path:"))
        local_row.addWidget(self.ed_local, 1)
        local_row.addWidget(self.btn_browse)
        st_layout.addLayout(local_row)
        
        # Drive settings
        drive_row = QHBoxLayout()
        drive_row.setSpacing(8)
        self.ed_gdrive = _line('Google Drive Folder ID')
        self.ed_gdrive.setText(self.state.get('gdrive_folder_id', ''))
        self.ed_oauth = _line('OAuth Token')
        self.ed_oauth.setText(self.state.get('google_workspace_oauth_token', ''))
        drive_row.addWidget(_label("Folder ID:"))
        drive_row.addWidget(self.ed_gdrive, 1)
        drive_row.addWidget(_label("OAuth:"))
        drive_row.addWidget(self.ed_oauth, 1)
        st_layout.addLayout(drive_row)
        
        self.rb_local.toggled.connect(self._toggle_storage)
        self.rb_drive.toggled.connect(self._toggle_storage)
        self._toggle_storage()
        
        root.addWidget(storage_group)
        
        # === SYSTEM PROMPTS - FIXED ===
        prompts_group = QGroupBox("🔄 System Prompts Updater")
        prompts_group.setFont(FONT_H2)
        prompts_layout = QVBoxLayout(prompts_group)
        prompts_layout.setSpacing(8)
        
        desc = _label("Update system prompts from Google Sheets without restarting")
        desc.setFont(FONT_SMALL)
        desc.setStyleSheet("color: #757575;")
        desc.setMinimumHeight(24)
        prompts_layout.addWidget(desc)
        
        prompts_row = QHBoxLayout()
        prompts_row.setSpacing(8)
        self.ed_sheets_url = _line('Google Sheets URL', read_only=True)
        self.ed_sheets_url.setText('https://docs.google.com/spreadsheets/d/1ohiL6xOBbjC7La2iUdkjrVjG4IEUnVWhI0fRoarD6P0')
        self.btn_update_prompts = CompactButton("⬇️ Update Now")
        self.btn_update_prompts.setObjectName("btn_primary")
        self.btn_update_prompts.setMinimumWidth(120)
        self.btn_update_prompts.setMinimumHeight(36)  # FIXED
        self.btn_update_prompts.clicked.connect(self._update_system_prompts)
        prompts_row.addWidget(_label("URL:"))
        prompts_row.addWidget(self.ed_sheets_url, 1)
        prompts_row.addWidget(self.btn_update_prompts)
        prompts_layout.addLayout(prompts_row)
        
        self.lb_prompts_status = _label("")
        self.lb_prompts_status.setFont(FONT_SMALL)
        self.lb_prompts_status.setMinimumHeight(24)
        self.lb_prompts_status.setWordWrap(True)
        prompts_layout.addWidget(self.lb_prompts_status)
        
        root.addWidget(prompts_group)
        
        # === BOTTOM BAR ===
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(16)
        
        self.btn_save = CompactButton("💾 Save Settings")
        self.btn_save.setObjectName("btn_save_luu")
        self.btn_save.setMinimumWidth(150)
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_save.clicked.connect(self._save)
        
        self.lb_saved = _label("")
        self.lb_saved.setFont(FONT_SMALL)
        self.lb_saved.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.lb_saved.setMinimumHeight(40)
        
        self.lb_version = _label(f"Video Super Ultra v{get_version()}")
        self.lb_version.setFont(QFont("Segoe UI", 12))
        self.lb_version.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        bottom_bar.addWidget(self.btn_save)
        bottom_bar.addWidget(self.lb_saved)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.lb_version)
        
        root.addLayout(bottom_bar)
        root.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _toggle_storage(self):
        is_local = self.rb_local.isChecked()
        self.ed_local.setEnabled(is_local)
        self.btn_browse.setEnabled(is_local)
        self.ed_gdrive.setEnabled(not is_local)
        self.ed_oauth.setEnabled(not is_local)
    
    def _pick_dir(self):
        d = QFileDialog.getExistingDirectory(self, 'Select download folder', '')
        if d:
            self.ed_local.setText(d)
    
    def _save(self):
        storage = 'gdrive' if self.rb_drive.isChecked() else 'local'
        st = {
            **cfg.load(),
            'account_email': self.ed_email.text().strip(),
            'download_storage': storage,
            'download_root': self.ed_local.text().strip(),
            'gdrive_folder_id': self.ed_gdrive.text().strip(),
            'google_workspace_oauth_token': self.ed_oauth.text().strip(),
            'labs_tokens': self.w_labs.get_keys(),
            'tokens': self.w_labs.get_keys(),
            'google_api_keys': self.w_google.get_keys(),
            'elevenlabs_api_keys': self.w_eleven.get_keys(),
            'openai_api_keys': self.w_openai.get_keys(),
            'default_voice_id': self.ed_voice.text().strip() or '3VnrjnYrskPMDsapTr8X',
            'flow_project_id': self.ed_project.text().strip() or '87b19267-13d6-49cd-a7ed-db19a90c9339',
        }
        cfg.save(st)
        self.lb_saved.setText(f'✓ Saved at {_ts()}')
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.lb_saved.setText(''))
    
    def _update_system_prompts(self):
        import os
        from PyQt5.QtWidgets import QMessageBox, QApplication
        
        self.lb_prompts_status.setText('⏳ Loading...')
        self.btn_update_prompts.setEnabled(False)
        QApplication.processEvents()
        
        try:
            from services.prompt_updater import update_prompts_file
            services_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services')
            prompts_file = os.path.join(services_dir, 'domain_prompts.py')
            
            success, message = update_prompts_file(prompts_file)
            
            if success:
                from services.domain_prompts import reload_prompts
                reload_success, reload_msg = reload_prompts()
                
                if reload_success:
                    self.lb_prompts_status.setText(f'✅ {message} - {reload_msg}')
                    QMessageBox.information(self, 'Success', f'{message}\n\n{reload_msg}')
                else:
                    self.lb_prompts_status.setText(f'⚠️ {message} - {reload_msg}')
                    QMessageBox.warning(self, 'Warning', f'{message}\n\nReload failed: {reload_msg}')
            else:
                self.lb_prompts_status.setText(f'❌ {message}')
                QMessageBox.critical(self, 'Error', message)
        
        except Exception as e:
            error_msg = f'❌ Error: {str(e)}'
            self.lb_prompts_status.setText(error_msg)
            QMessageBox.critical(self, 'Error', error_msg)
        
        finally:
            self.btn_update_prompts.setEnabled(True)
