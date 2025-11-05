# -*- coding: utf-8 -*-
"""
Settings Panel V3 Compact - Super compact, 2-column API
Fits in one screen
"""

import datetime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QGroupBox, QFileDialog, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt

from ui.widgets.accordion import Accordion, AccordionSection
from ui.widgets.compact_button import CompactButton
from ui.widgets.key_list_v2 import KeyListV2
from utils import config as cfg
from utils.version import get_version

# Typography
FONT_H2 = QFont("Segoe UI", 14, QFont.Bold)
FONT_BODY = QFont("Segoe UI", 13)
FONT_SMALL = QFont("Segoe UI", 12)
FONT_MONO = QFont("Courier New", 11)

def _ts():
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

def _line(placeholder='', read_only=False):
    """Create compact line edit"""
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setFont(FONT_BODY)
    e.setMinimumHeight(36)
    e.setMaximumHeight(36)
    e.setReadOnly(read_only)
    
    if not read_only:
        e.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid #1E88E5;
                background: #F8FCFF;
            }
        """)
    else:
        e.setStyleSheet("""
            QLineEdit {
                background: #F5F5F5;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px 12px;
            }
        """)
    
    return e

def _label(text):
    l = QLabel(text)
    l.setFont(FONT_BODY)
    l.setMinimumHeight(36)
    l.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
    return l

class SettingsPanelV3Compact(QWidget):
    """Settings Panel V3 - Super Compact"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = cfg.load()
        self._build_ui()
    
    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)  # Compact spacing
        
        # === ACCOUNT INFO ===
        acc_group = QGroupBox("👤 Account Information")
        acc_group.setFont(FONT_H2)
        acc_layout = QGridLayout(acc_group)
        acc_layout.setVerticalSpacing(8)
        acc_layout.setHorizontalSpacing(12)
        acc_layout.setColumnStretch(1, 1)
        acc_layout.setColumnStretch(3, 1)
        
        self.ed_email = _line('Email', read_only=True)
        self.ed_email.setText(self.state.get('account_email', ''))
        
        hwid_text = self.state.get('hardware_id', '')
        self.lb_hwid = _label(hwid_text)
        self.lb_hwid.setFont(FONT_MONO)
        self.lb_hwid.setStyleSheet("background: #F5F5F5; padding: 8px; border-radius: 4px;")
        
        status_text = self.state.get('license_status', 'Kích Hoạt')
        self.lb_status = _label(status_text)
        if 'kích' in status_text.lower() or 'active' in status_text.lower():
            self.lb_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        expiry_text = self.state.get('license_expiry', 'Không có hạn sử dụng')
        self.lb_expiry = _label(expiry_text)
        
        acc_layout.addWidget(_label("Email:"), 0, 0)
        acc_layout.addWidget(self.ed_email, 0, 1)
        acc_layout.addWidget(_label("Hardware ID:"), 0, 2)
        acc_layout.addWidget(self.lb_hwid, 0, 3)
        
        acc_layout.addWidget(_label("Status:"), 1, 0)
        acc_layout.addWidget(self.lb_status, 1, 1)
        acc_layout.addWidget(_label("Expires:"), 1, 2)
        acc_layout.addWidget(self.lb_expiry, 1, 3)
        
        root.addWidget(acc_group)
        
        # === API CREDENTIALS - 2 COLUMNS ===
        api_group = QGroupBox("🔑 API Credentials")
        api_group.setFont(FONT_H2)
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(6)
        
        hint = QLabel("💡 Click sections to expand. Keys are displayed compactly.")
        hint.setFont(FONT_SMALL)
        hint.setStyleSheet("color: #757575; font-style: italic;")
        api_layout.addWidget(hint)
        
        # 2-column grid for accordion sections
        accordion_grid = QGridLayout()
        accordion_grid.setSpacing(8)
        
        # Column 1
        labs_section = AccordionSection("Google Labs Token (OAuth)")
        labs_init = self.state.get('labs_tokens') or self.state.get('tokens') or []
        self.w_labs = KeyListV2(kind='google-labs', initial=labs_init)
        labs_section.add_content_widget(self.w_labs)
        
        self.ed_project = _line('Project ID')
        self.ed_project.setText(self.state.get('flow_project_id', '87b19267-13d6-49cd-a7ed-db19a90c9339'))
        proj_row = QHBoxLayout()
        proj_row.addWidget(QLabel("Project ID:"))
        proj_row.addWidget(self.ed_project)
        labs_section.add_content_layout(proj_row)
        
        accordion_grid.addWidget(labs_section, 0, 0)
        
        google_section = AccordionSection("Google API Keys")
        g_list = self.state.get('google_api_keys') or []
        self.w_google = KeyListV2(kind='google', initial=g_list)
        google_section.add_content_widget(self.w_google)
        accordion_grid.addWidget(google_section, 1, 0)
        
        # Column 2
        eleven_section = AccordionSection("Elevenlabs API Keys")
        self.w_eleven = KeyListV2(kind='elevenlabs', 
                                  initial=self.state.get('elevenlabs_api_keys') or [])
        eleven_section.add_content_widget(self.w_eleven)
        
        self.ed_voice = _line('Voice ID')
        self.ed_voice.setText(self.state.get('default_voice_id', '3VnrjnYrskPMDsapTr8X'))
        voice_row = QHBoxLayout()
        voice_row.addWidget(QLabel("Voice ID:"))
        voice_row.addWidget(self.ed_voice)
        eleven_section.add_content_layout(voice_row)
        
        accordion_grid.addWidget(eleven_section, 0, 1)
        
        openai_section = AccordionSection("OpenAI API Keys")
        self.w_openai = KeyListV2(kind='openai', 
                                  initial=self.state.get('openai_api_keys') or [])
        openai_section.add_content_widget(self.w_openai)
        accordion_grid.addWidget(openai_section, 1, 1)
        
        api_layout.addLayout(accordion_grid)
        
        # Expand/Collapse buttons
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(8)
        
        btn_expand = CompactButton("📂 Expand All")
        btn_expand.setObjectName("btn_expand")
        btn_expand.clicked.connect(lambda: [
            labs_section.set_expanded(True),
            google_section.set_expanded(True),
            eleven_section.set_expanded(True),
            openai_section.set_expanded(True)
        ])
        toggle_row.addWidget(btn_expand)
        
        btn_collapse = CompactButton("📁 Collapse All")
        btn_collapse.setObjectName("btn_collapse")
        btn_collapse.clicked.connect(lambda: [
            labs_section.set_expanded(False),
            google_section.set_expanded(False),
            eleven_section.set_expanded(False),
            openai_section.set_expanded(False)
        ])
        toggle_row.addWidget(btn_collapse)
        toggle_row.addStretch()
        
        api_layout.addLayout(toggle_row)
        root.addWidget(api_group)
        
        # === STORAGE - ONE LINE ===
        storage_group = QGroupBox("💾 Storage Settings")
        storage_group.setFont(FONT_H2)
        st_layout = QVBoxLayout(storage_group)
        st_layout.setSpacing(6)
        
        # Radio + path in one row
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        self.rb_local = QRadioButton("📁 Local")
        self.rb_drive = QRadioButton("☁️ Drive")
        storage = (self.state.get('download_storage') or 'local').lower()
        (self.rb_drive if storage == 'gdrive' else self.rb_local).setChecked(True)
        
        row1.addWidget(self.rb_local)
        row1.addWidget(self.rb_drive)
        row1.addWidget(QLabel("Path:"))
        
        self.ed_local = _line('Select folder...')
        self.ed_local.setText(self.state.get('download_root', ''))
        row1.addWidget(self.ed_local, 1)
        
        self.btn_browse = CompactButton("📂 Browse")
        self.btn_browse.setObjectName("btn_browse")
        self.btn_browse.setMinimumHeight(36)
        self.btn_browse.clicked.connect(self._pick_dir)
        row1.addWidget(self.btn_browse)
        
        st_layout.addLayout(row1)
        
        # Drive settings in one row
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        row2.addWidget(QLabel("Folder ID:"))
        self.ed_gdrive = _line('Folder ID')
        self.ed_gdrive.setText(self.state.get('gdrive_folder_id', ''))
        row2.addWidget(self.ed_gdrive, 1)
        row2.addWidget(QLabel("OAuth:"))
        self.ed_oauth = _line('Token')
        self.ed_oauth.setText(self.state.get('google_workspace_oauth_token', ''))
        row2.addWidget(self.ed_oauth, 1)
        st_layout.addLayout(row2)
        
        self.rb_local.toggled.connect(self._toggle_storage)
        self._toggle_storage()
        
        root.addWidget(storage_group)
        
        # === SYSTEM PROMPTS - ONE LINE ===
        prompts_row = QHBoxLayout()
        prompts_row.setSpacing(8)
        prompts_row.addWidget(QLabel("🔄 Prompts:"))
        self.ed_sheets_url = _line('', read_only=True)
        self.ed_sheets_url.setText('https://docs.google.com/spreadsheets/d/1ohiL6xOBbjC7La2iUdkjrVjG4IEUnVWhI0fRoarD6P0')
        prompts_row.addWidget(self.ed_sheets_url, 1)
        self.btn_update_prompts = CompactButton("⬇ Update")
        self.btn_update_prompts.setObjectName("btn_primary")
        self.btn_update_prompts.setMinimumHeight(36)
        self.btn_update_prompts.clicked.connect(self._update_system_prompts)
        prompts_row.addWidget(self.btn_update_prompts)
        root.addLayout(prompts_row)
        
        self.lb_prompts_status = QLabel("")
        self.lb_prompts_status.setFont(FONT_SMALL)
        root.addWidget(self.lb_prompts_status)
        
        # === BOTTOM BAR ===
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)
        
        self.btn_save = CompactButton("💾 Save Settings")
        self.btn_save.setObjectName("btn_save_luu")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_save.clicked.connect(self._save)
        bottom_row.addWidget(self.btn_save)
        
        self.lb_saved = QLabel("")
        self.lb_saved.setFont(FONT_SMALL)
        self.lb_saved.setStyleSheet("color: #4CAF50; font-weight: bold;")
        bottom_row.addWidget(self.lb_saved)
        bottom_row.addStretch()
        
        self.lb_version = QLabel(f"Video Super Ultra v{get_version()}")
        self.lb_version.setFont(FONT_SMALL)
        bottom_row.addWidget(self.lb_version)
        
        root.addLayout(bottom_row)
        
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
        from PyQt5.QtWidgets import QMessageBox, QApplication
        
        self.lb_prompts_status.setText('⏳ Updating...')
        self.btn_update_prompts.setEnabled(False)
        QApplication.processEvents()
        
        try:
            from services.prompt_updater import update_prompts_file
            import os
            
            services_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services')
            prompts_file = os.path.join(services_dir, 'domain_prompts.py')
            
            success, message = update_prompts_file(prompts_file)
            
            if success:
                self.lb_prompts_status.setText(f'✅ {message}')
                QMessageBox.information(self, 'Success', message)
            else:
                self.lb_prompts_status.setText(f'❌ {message}')
                QMessageBox.critical(self, 'Error', message)
        
        except Exception as e:
            error_msg = f'❌ Error: {str(e)}'
            self.lb_prompts_status.setText(error_msg)
            QMessageBox.critical(self, 'Error', error_msg)
        
        finally:
            self.btn_update_prompts.setEnabled(True)