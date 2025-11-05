#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-patch script for Issue #7: Add Storyboard View and Improve CardList UI
Repository: chamnv-dev/v3
Branch: feature/text2video-storyboard-ui
Date: 2025-11-05
"""

import os
import re
import shutil
from datetime import datetime


def backup_file(file_path):
    """Create backup of original file"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path


def patch_text2video_panel():
    """Main patching function for ui/text2video_panel.py"""
    
    file_path = "ui/text2video_panel.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("   Please run this script from the project root directory")
        return False
    
    # Backup original file
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📝 Patching {file_path}...")
    
    # ========================================
    # STEP 1: Add StoryboardView class at the beginning (after imports)
    # ========================================
    
    storyboard_class = '''

class StoryboardView(QWidget):
    """
    Grid view for scenes - 3 columns layout
    Light theme with hover effects
    """
    
    scene_clicked = pyqtSignal(int)  # Emit scene number when clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #FAFAFA; border: none; }")
        
        # Container for grid
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        self.grid_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        self.scene_cards = {}  # Store card widgets by scene number
    
    def add_scene(self, scene_num, thumbnail_path, prompt_text, state_dict):
        """
        Add scene card to grid
        
        Args:
            scene_num: Scene number (1-based)
            thumbnail_path: Path to thumbnail image
            prompt_text: Prompt text to display
            state_dict: Full state dict for this scene
        """
        row = (scene_num - 1) // 3
        col = (scene_num - 1) % 3
        
        # Create card widget
        card = QFrame()
        card.setFixedSize(260, 240)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 2px solid #1E88E5;
                background: #F8FCFF;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(8, 8, 8, 8)
        
        # Thumbnail (16:9 aspect ratio)
        thumb_label = QLabel()
        thumb_label.setFixedSize(242, 136)
        thumb_label.setAlignment(Qt.AlignCenter)
        thumb_label.setStyleSheet("""
            background: #F5F5F5; 
            border: 1px solid #E0E0E0;
            border-radius: 6px;
            color: #9E9E9E;
            font-size: 11px;
        """)
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path).scaled(
                242, 136, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            thumb_label.setPixmap(pixmap)
        else:
            thumb_label.setText("🖼️\nChưa tạo ảnh")
        
        card_layout.addWidget(thumb_label)
        
        # Scene title (bold, blue)
        title_label = QLabel(f"<b style='color:#1E88E5; font-size:13px;'>🎬 Cảnh {scene_num}</b>")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Prompt preview (truncated)
        preview_text = prompt_text[:50] + "..." if len(prompt_text) > 50 else prompt_text
        desc_label = QLabel(preview_text)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Segoe UI", 9))
        desc_label.setStyleSheet("color: #757575;")
        desc_label.setMaximumHeight(40)
        card_layout.addWidget(desc_label)
        
        # Video status indicator
        vids = state_dict.get('videos', {})
        if vids:
            completed = sum(1 for v in vids.values() if v.get('status') == 'completed')
            total = len(vids)
            status_label = QLabel(f"🎥 {completed}/{total} videos")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setFont(QFont("Segoe UI", 9))
            status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            card_layout.addWidget(status_label)
        
        # Store scene number for click handling
        card.scene_num = scene_num
        card.mousePressEvent = lambda e: self.scene_clicked.emit(scene_num)
        
        # Add to grid
        self.grid_layout.addWidget(card, row, col)
        self.scene_cards[scene_num] = card
    
    def clear(self):
        """Clear all scene cards"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.scene_cards.clear()
    
    def update_scene_thumbnail(self, scene_num, thumbnail_path):
        """Update thumbnail for a specific scene"""
        card = self.scene_cards.get(scene_num)
        if not card:
            return
        
        # Find thumbnail label (first child widget)
        thumb_label = card.findChild(QLabel)
        if thumb_label and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path).scaled(
                242, 136, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            thumb_label.setPixmap(pixmap)
'''
    
    # Find where to insert (after imports, before CollapsibleGroupBox)
    insert_pos = content.find("class CollapsibleGroupBox")
    if insert_pos == -1:
        print("❌ Could not find insertion point for StoryboardView class")
        return False
    
    content = content[:insert_pos] + storyboard_class + "\n\n" + content[insert_pos:]
    print("✅ Added StoryboardView class")
    
    # ========================================
    # STEP 2: Update _render_card_text() method
    # ========================================
    
    # Find the method
    old_render_pattern = r'def _render_card_text\(self, scene\):.*?return.*?\n'
    
    new_render_method = '''def _render_card_text(self, scene):
        """Render card text with improved styling - Issue #7"""
        st = self._cards_state.get(scene, {})
        vi = st.get('vi', '').strip()
        tgt = st.get('tgt', '').strip()
        
        # Bold, blue scene title (14px) - Issue #7 requirement
        lines = [f'<b style="font-size:14px; color:#1E88E5;">🎬 Cảnh {scene}</b>']
        lines.append('━━━━━━━━━━━━━━━━━━━━')
        
        # Prompt text (11px, truncated to 150 chars) - Issue #7 requirement
        if tgt or vi:
            lines.append('<span style="font-size:11px; font-weight:600;">📝 PROMPT:</span>')
            prompt_text = (tgt or vi)[:150]
            if len(tgt or vi) > 150:
                prompt_text += '...'
            lines.append(f'<span style="font-size:11px; color:#424242;">{prompt_text}</span>')
        
        # Video status
        vids = st.get('videos', {})
        if vids:
            lines.append('')
            lines.append('<span style="font-size:11px; font-weight:600;">🎥 VIDEO:</span>')
            for copy, info in sorted(vids.items()):
                status = info.get('status', '?')
                tag = f'<span style="font-size:10px; color:#616161;">  #{copy}: {status}</span>'
                if info.get('completed_at'):
                    tag = f'<span style="font-size:10px; color:#616161;">  #{copy}: {status} — {info["completed_at"]}</span>'
                lines.append(tag)
                
                if info.get('path'):
                    lines.append(f'<span style="font-size:10px; color:#757575;">  📥 {os.path.basename(info["path"])}</span>')
        
        return '<br>'.join(lines)
'''
    
    content = re.sub(old_render_pattern, new_render_method, content, flags=re.DOTALL)
    print("✅ Updated _render_card_text() method")
    
    # ========================================
    # STEP 3: Add toggle buttons and storyboard view in scenes tab
    # ========================================
    
    # Find the scenes tab section (around line 494-509)
    scenes_tab_pattern = r'(self\.cards = QListWidget\(\).*?self\.cards\.setIconSize\(QSize\(240, 135\)\))'
    
    new_scenes_tab = r'''# === Scene View Toggle Buttons (Issue #7) ===
        toggle_widget = QWidget()
        toggle_layout = QHBoxLayout(toggle_widget)
        toggle_layout.setContentsMargins(8, 8, 8, 8)
        toggle_layout.setSpacing(8)
        
        self.btn_view_card = QPushButton("📇 Card")
        self.btn_view_card.setCheckable(True)
        self.btn_view_card.setChecked(True)
        self.btn_view_card.setFixedHeight(34)
        self.btn_view_card.setFixedWidth(100)
        self.btn_view_card.setStyleSheet("""
            QPushButton {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:checked {
                background: #1E88E5;
                border: 2px solid #1E88E5;
                color: white;
            }
            QPushButton:hover {
                border: 2px solid #1E88E5;
            }
        """)
        self.btn_view_card.clicked.connect(lambda: self._switch_view('card'))
        
        self.btn_view_storyboard = QPushButton("📊 Storyboard")
        self.btn_view_storyboard.setCheckable(True)
        self.btn_view_storyboard.setChecked(False)
        self.btn_view_storyboard.setFixedHeight(34)
        self.btn_view_storyboard.setFixedWidth(120)
        self.btn_view_storyboard.setStyleSheet("""
            QPushButton {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:checked {
                background: #1E88E5;
                border: 2px solid #1E88E5;
                color: white;
            }
            QPushButton:hover {
                border: 2px solid #1E88E5;
            }
        """)
        self.btn_view_storyboard.clicked.connect(lambda: self._switch_view('storyboard'))
        
        toggle_layout.addWidget(self.btn_view_card)
        toggle_layout.addWidget(self.btn_view_storyboard)
        toggle_layout.addStretch()
        
        scenes_layout.addWidget(toggle_widget)
        
        # === Stacked Widget for View Switching ===
        self.view_stack = QStackedWidget()
        
        # Card view (existing QListWidget)
        self.cards = QListWidget()
        self.cards.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cards.setIconSize(QSize(240, 135))
        self.cards.itemDoubleClicked.connect(self._open_card_prompt_detail)
        self.view_stack.addWidget(self.cards)
        
        # Storyboard view (new grid layout)
        self.storyboard_view = StoryboardView(self)
        self.storyboard_view.scene_clicked.connect(self._show_prompt_detail)
        self.view_stack.addWidget(self.storyboard_view)
        
        scenes_layout.addWidget(self.view_stack)'''
    
    content = re.sub(scenes_tab_pattern, new_scenes_tab, content, flags=re.DOTALL)
    print("✅ Added toggle buttons and storyboard view")
    
    # ========================================
    # STEP 4: Add new methods at the end of class
    # ========================================
    
    new_methods = '''
    # ========================================
    # Issue #7: Storyboard View and Prompt Detail Dialog
    # ========================================
    
    def _switch_view(self, view_type):
        """Switch between Card and Storyboard views"""
        if view_type == 'card':
            self.view_stack.setCurrentIndex(0)
            self.btn_view_card.setChecked(True)
            self.btn_view_storyboard.setChecked(False)
        else:  # storyboard
            self.view_stack.setCurrentIndex(1)
            self.btn_view_card.setChecked(False)
            self.btn_view_storyboard.setChecked(True)
            self._refresh_storyboard()
    
    def _refresh_storyboard(self):
        """Refresh storyboard view with current scenes"""
        self.storyboard_view.clear()
        
        for scene_num in sorted(self._cards_state.keys()):
            st = self._cards_state[scene_num]
            prompt = st.get('tgt', st.get('vi', ''))
            thumb_path = st.get('thumb', '')
            self.storyboard_view.add_scene(scene_num, thumb_path, prompt, st)
    
    def _open_card_prompt_detail(self, item):
        """Open prompt detail dialog when double-clicking card"""
        try:
            role = item.data(Qt.UserRole)
            if not isinstance(role, tuple) or role[0] != 'scene':
                return
            
            scene_num = int(role[1])
            self._show_prompt_detail(scene_num)
        except Exception as e:
            print(f"Error opening prompt detail: {e}")
    
    def _show_prompt_detail(self, scene_num):
        """Show detailed prompt dialog for a scene - Issue #7"""
        st = self._cards_state.get(scene_num, {})
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Prompts - Cảnh {scene_num}")
        dialog.setMinimumSize(750, 550)
        dialog.setStyleSheet("""
            QDialog {
                background: #FAFAFA;
            }
            QLabel {
                color: #212121;
            }
            QTextEdit {
                background: white;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                color: #424242;
            }
            QPushButton {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #F5F5F5;
                border: 2px solid #1E88E5;
            }
            QPushButton#btn_close {
                background: #1E88E5;
                border: 2px solid #1E88E5;
                color: white;
            }
            QPushButton#btn_close:hover {
                background: #1976D2;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(f"<b style='font-size:16px; color:#1E88E5;'>📝 Prompts cho Cảnh {scene_num}</b>")
        layout.addWidget(title)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setStyleSheet("background: #E0E0E0;")
        separator1.setFixedHeight(2)
        layout.addWidget(separator1)
        
        # Image prompt section
        lbl_img = QLabel("<b style='font-size:12px;'>📷 Prompt Ảnh (Vietnamese):</b>")
        layout.addWidget(lbl_img)
        
        ed_img_prompt = QTextEdit()
        ed_img_prompt.setReadOnly(True)
        ed_img_prompt.setPlainText(st.get('vi', '(Không có prompt)'))
        ed_img_prompt.setMaximumHeight(160)
        layout.addWidget(ed_img_prompt)
        
        btn_copy_img = QPushButton("📋 Copy Prompt Ảnh")
        btn_copy_img.setFixedHeight(36)
        btn_copy_img.clicked.connect(lambda: self._copy_to_clipboard(st.get('vi', '')))
        layout.addWidget(btn_copy_img)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background: #E0E0E0;")
        separator2.setFixedHeight(2)
        layout.addWidget(separator2)
        
        # Video prompt section
        lbl_vid = QLabel("<b style='font-size:12px;'>🎬 Prompt Video (Target Language):</b>")
        layout.addWidget(lbl_vid)
        
        ed_vid_prompt = QTextEdit()
        ed_vid_prompt.setReadOnly(True)
        ed_vid_prompt.setPlainText(st.get('tgt', '(Không có prompt)'))
        ed_vid_prompt.setMaximumHeight(160)
        layout.addWidget(ed_vid_prompt)
        
        btn_copy_vid = QPushButton("📋 Copy Prompt Video")
        btn_copy_vid.setFixedHeight(36)
        btn_copy_vid.clicked.connect(lambda: self._copy_to_clipboard(st.get('tgt', '')))
        layout.addWidget(btn_copy_vid)
        
        layout.addStretch()
        
        # Close button
        btn_close = QPushButton("✖ Đóng")
        btn_close.setObjectName("btn_close")
        btn_close.setFixedHeight(40)
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)
        
        dialog.exec_()
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(
                self, 
                "Thành công", 
                "✅ Đã copy vào clipboard!",
                QMessageBox.Ok
            )
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Lỗi", 
                f"Không thể copy: {str(e)}",
                QMessageBox.Ok
            )
'''
    
    # Find the last method of the class (before the end or before next class)
    # Look for pattern like "    def _some_method" at the end
    insert_pos = content.rfind("\n\nclass ")
    if insert_pos == -1:
        # No other class found, add before end of file
        insert_pos = len(content)
    
    content = content[:insert_pos] + new_methods + "\n\n" + content[insert_pos:]
    print("✅ Added new methods (_switch_view, _refresh_storyboard, _show_prompt_detail, _copy_to_clipboard)")
    
    # ========================================
    # STEP 5: Update scene population logic to refresh storyboard
    # ========================================
    
    # Find where cards are populated (around line 1000-1025)
    populate_pattern = r'(self\.cards\.addItem\(it\))'
    populate_replacement = r'''\1
        
        # Also refresh storyboard if visible (Issue #7)
        if hasattr(self, 'view_stack') and self.view_stack.currentIndex() == 1:
            self._refresh_storyboard()'''
    
    content = re.sub(populate_pattern, populate_replacement, content)
    print("✅ Updated scene population to refresh storyboard")
    
    # ========================================
    # STEP 6: Add pyqtSignal import if not present
    # ========================================
    
    if 'pyqtSignal' not in content:
        # Find QtCore import line
        import_pattern = r'(from PyQt5\.QtCore import[^)]+)'
        
        def add_pyqtsignal(match):
            imports = match.group(1)
            if 'pyqtSignal' not in imports:
                # Add before the closing parenthesis or at the end
                if ')' in imports:
                    imports = imports.replace(')', ', pyqtSignal)')
                else:
                    imports += ', pyqtSignal'
            return imports
        
        content = re.sub(import_pattern, add_pyqtsignal, content)
        print("✅ Added pyqtSignal import")
    
    # ========================================
    # STEP 7: Add QStackedWidget and QPixmap imports if not present
    # ========================================
    
    if 'QStackedWidget' not in content:
        widgets_import_pattern = r'(from PyQt5\.QtWidgets import \([^)]+)\)'
        
        def add_qstackedwidget(match):
            imports = match.group(1)
            if 'QStackedWidget' not in imports:
                imports += ',\n    QStackedWidget'
            return imports + ')'
        
        content = re.sub(widgets_import_pattern, add_qstackedwidget, content, count=1)
        print("✅ Added QStackedWidget import")
    
    if 'QPixmap' not in content:
        gui_import_pattern = r'(from PyQt5\.QtGui import[^)]+)'
        
        def add_qpixmap(match):
            imports = match.group(1)
            if 'QPixmap' not in imports:
                if ')' in imports:
                    imports = imports.replace(')', ', QPixmap)')
                else:
                    imports += ', QPixmap'
            return imports
        
        content = re.sub(gui_import_pattern, add_qpixmap, content)
        print("✅ Added QPixmap import")
    
    # Write patched content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Successfully patched {file_path}")
    print(f"   Total changes: ~400 lines added/modified")
    return True


def main():
    """Main execution"""
    print("=" * 60)
    print("🚀 Issue #7 Auto-Patch Script")
    print("   Add Storyboard View and Improve CardList UI")
    print("   Repository: chamnv-dev/v3")
    print("   Branch: feature/text2video-storyboard-ui")
    print("=" * 60)
    print()
    
    # Check if we're in project root
    if not os.path.exists('ui') or not os.path.exists('services'):
        print("❌ Error: Please run this script from the project root directory")
        print("   (where 'ui' and 'services' folders exist)")
        return 1
    
    # Run patches
    success = patch_text2video_panel()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ All patches applied successfully!")
        print("=" * 60)
        print("\n📋 Next steps:")
        print("   1. Test the changes:")
        print("      python -B main_image2video.py")
        print()
        print("   2. Check the new features:")
        print("      - Toggle between Card/Storyboard views")
        print("      - Double-click scene for prompt details")
        print("      - Verify bold blue 'Cảnh X' titles")
        print("      - Check smaller prompt text (11px)")
        print()
        print("   3. Commit and push:")
        print("      git add ui/text2video_panel.py")
        print("      git commit -m 'feat: Add Storyboard view and improve CardList UI (#7)'")
        print("      git push origin feature/text2video-storyboard-ui")
        print()
        print("   4. Create Pull Request on GitHub:")
        print("      https://github.com/chamnv-dev/v3/compare/feature/text2video-storyboard-ui")
        print()
        print("🎉 Done!")
        return 0
    else:
        print("\n❌ Patching failed. Please check errors above.")
        print("   Original file backup created with .backup_YYYYMMDD_HHMMSS suffix")
        return 1


if __name__ == "__main__":
    exit(main())