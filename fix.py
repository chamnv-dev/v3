#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to add Storyboard view to Text2Video panel
Just adds the missing features without complex regex
"""

import os
import shutil
from datetime import datetime


def backup_file(filepath):
    """Create timestamped backup"""
    backup = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup)
    print(f"✅ Backup created: {backup}")
    return backup


def create_storyboard_additions():
    """Create the code additions needed"""
    
    # 1. StoryboardView class to add after CollapsibleGroupBox
    storyboard_class = '''

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap

class StoryboardView(QWidget):
    """Grid view for scenes - 3 columns, light theme"""
    
    scene_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Scroll container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #FAFAFA; border: none;")
        
        # Grid container
        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(16)
        self.grid.setContentsMargins(16, 16, 16, 16)
        self.grid.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(container)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        self.cards = {}
    
    def add_scene(self, scene_num, thumb_path, prompt, state):
        """Add scene card to grid"""
        row = (scene_num - 1) // 3
        col = (scene_num - 1) % 3
        
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
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Thumbnail
        thumb = QLabel()
        thumb.setFixedSize(242, 136)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setStyleSheet("""
            background: #F5F5F5;
            border: 1px solid #E0E0E0;
            border-radius: 6px;
            color: #9E9E9E;
            font-size: 11px;
        """)
        
        if thumb_path and os.path.exists(thumb_path):
            pix = QPixmap(thumb_path).scaled(242, 136, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumb.setPixmap(pix)
        else:
            thumb.setText("🖼️\\nChưa tạo ảnh")
        
        layout.addWidget(thumb)
        
        # Title
        title = QLabel(f"<b style='color:#1E88E5; font-size:13px;'>🎬 Cảnh {scene_num}</b>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Prompt preview
        preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
        desc = QLabel(preview)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #757575;")
        desc.setMaximumHeight(40)
        layout.addWidget(desc)
        
        # Video status
        vids = state.get('videos', {})
        if vids:
            completed = sum(1 for v in vids.values() if v.get('status') == 'completed')
            total = len(vids)
            status = QLabel(f"🎥 {completed}/{total} videos")
            status.setAlignment(Qt.AlignCenter)
            status.setFont(QFont("Segoe UI", 9))
            status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            layout.addWidget(status)
        
        card.scene_num = scene_num
        card.mousePressEvent = lambda e: self.scene_clicked.emit(scene_num)
        
        self.grid.addWidget(card, row, col)
        self.cards[scene_num] = card
    
    def clear(self):
        """Clear all cards"""
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cards.clear()
'''
    
    # 2. New _render_card_text method
    render_method = '''    def _render_card_text(self, scene):
        """Render card text with HTML formatting - Issue #7"""
        st = self._cards_state.get(scene, {})
        vi = st.get('vi', '').strip()
        tgt = st.get('tgt', '').strip()
        
        # Bold blue title (14px)
        lines = ['<b style="font-size:14px; color:#1E88E5;">🎬 Cảnh ' + str(scene) + '</b>']
        lines.append('━━━━━━━━━━━━━━━━━━━━')
        
        # Prompt (11px, max 150 chars)
        if tgt or vi:
            lines.append('<span style="font-size:11px; font-weight:600;">📝 PROMPT:</span>')
            prompt = (tgt or vi)[:150]
            if len(tgt or vi) > 150:
                prompt += '...'
            lines.append('<span style="font-size:11px; color:#424242;">' + prompt + '</span>')
        
        # Videos
        vids = st.get('videos', {})
        if vids:
            lines.append('')
            lines.append('<span style="font-size:11px; font-weight:600;">🎥 VIDEO:</span>')
            for copy, info in sorted(vids.items()):
                status = info.get('status', '?')
                tag = '<span style="font-size:10px; color:#616161;">  #' + str(copy) + ': ' + status
                if info.get('completed_at'):
                    tag += ' — ' + info['completed_at']
                tag += '</span>'
                lines.append(tag)
                
                if info.get('path'):
                    lines.append('<span style="font-size:10px; color:#757575;">  📥 ' + os.path.basename(info['path']) + '</span>')
        
        return '<br>'.join(lines)
'''
    
    # 3. Methods to add at end of class
    new_methods = '''
    def _switch_view(self, view_type):
        """Switch between Card and Storyboard views"""
        if view_type == 'card':
            self.view_stack.setCurrentIndex(0)
            self.btn_view_card.setChecked(True)
            self.btn_view_storyboard.setChecked(False)
        else:
            self.view_stack.setCurrentIndex(1)
            self.btn_view_card.setChecked(False)
            self.btn_view_storyboard.setChecked(True)
            self._refresh_storyboard()
    
    def _refresh_storyboard(self):
        """Refresh storyboard with current scenes"""
        self.storyboard_view.clear()
        for scene_num in sorted(self._cards_state.keys()):
            st = self._cards_state[scene_num]
            prompt = st.get('tgt', st.get('vi', ''))
            thumb = st.get('thumb', '')
            self.storyboard_view.add_scene(scene_num, thumb, prompt, st)
    
    def _open_card_prompt_detail(self, item):
        """Open detail dialog on double-click"""
        try:
            role = item.data(Qt.UserRole)
            if isinstance(role, tuple) and role[0] == 'scene':
                self._show_prompt_detail(int(role[1]))
        except:
            pass
    
    def _show_prompt_detail(self, scene_num):
        """Show prompt detail dialog"""
        st = self._cards_state.get(scene_num, {})
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Prompts - Cảnh {scene_num}")
        dialog.setMinimumSize(750, 550)
        dialog.setStyleSheet("""
            QDialog { background: #FAFAFA; }
            QTextEdit {
                background: white;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton {
                background: white;
                border: 2px solid #BDBDBD;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
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
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(f"<b style='font-size:16px; color:#1E88E5;'>📝 Prompts cho Cảnh {scene_num}</b>")
        layout.addWidget(title)
        
        # Image prompt
        layout.addWidget(QLabel("<b>📷 Prompt Ảnh (Vietnamese):</b>"))
        ed_img = QTextEdit()
        ed_img.setReadOnly(True)
        ed_img.setPlainText(st.get('vi', '(Không có)'))
        ed_img.setMaximumHeight(160)
        layout.addWidget(ed_img)
        
        btn_img = QPushButton("📋 Copy Prompt Ảnh")
        btn_img.setFixedHeight(36)
        btn_img.clicked.connect(lambda: self._copy_to_clipboard(st.get('vi', '')))
        layout.addWidget(btn_img)
        
        # Video prompt
        layout.addWidget(QLabel("<b>🎬 Prompt Video (Target):</b>"))
        ed_vid = QTextEdit()
        ed_vid.setReadOnly(True)
        ed_vid.setPlainText(st.get('tgt', '(Không có)'))
        ed_vid.setMaximumHeight(160)
        layout.addWidget(ed_vid)
        
        btn_vid = QPushButton("📋 Copy Prompt Video")
        btn_vid.setFixedHeight(36)
        btn_vid.clicked.connect(lambda: self._copy_to_clipboard(st.get('tgt', '')))
        layout.addWidget(btn_vid)
        
        layout.addStretch()
        
        btn_close = QPushButton("✖ Đóng")
        btn_close.setObjectName("btn_close")
        btn_close.setFixedHeight(40)
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)
        
        dialog.exec_()
    
    def _copy_to_clipboard(self, text):
        """Copy to clipboard"""
        try:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Thành công", "✅ Đã copy vào clipboard!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể copy: {e}")
'''
    
    return storyboard_class, render_method, new_methods


def patch_file():
    """Patch the text2video_panel.py file"""
    
    filepath = "ui/text2video_panel.py"
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    # Backup
    backup_file(filepath)
    
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("📝 Patching file...")
    
    # Get additions
    storyboard_class, render_method, new_methods = create_storyboard_additions()
    
    # Find insertion points
    new_lines = []
    i = 0
    
    # Step 1: Add imports at top (after existing imports)
    added_imports = False
    while i < len(lines):
        new_lines.append(lines[i])
        
        # After PyQt5 imports, add missing ones
        if not added_imports and 'from PyQt5.QtWidgets import' in lines[i]:
            # Check if QStackedWidget, QDialog, QGridLayout are imported
            imports_block = []
            j = i
            while j < len(lines) and (lines[j].strip().endswith(',') or 'from PyQt5.QtWidgets import' in lines[j]):
                imports_block.append(lines[j])
                j += 1
            
            imports_text = ''.join(imports_block)
            
            # Add missing imports
            if 'QStackedWidget' not in imports_text:
                new_lines[-1] = new_lines[-1].rstrip().rstrip(')') + ',\n    QStackedWidget,\n    QDialog,\n    QGridLayout,\n)\n'
                # Skip the closing paren
                while i < len(lines) and ')' not in lines[i]:
                    i += 1
                i += 1
                added_imports = True
                continue
        
        i += 1
    
    # Now work with new_lines
    lines = new_lines
    new_lines = []
    i = 0
    
    # Step 2: Add StoryboardView class after CollapsibleGroupBox
    added_storyboard = False
    while i < len(lines):
        new_lines.append(lines[i])
        
        # After CollapsibleGroupBox class definition
        if not added_storyboard and 'class CollapsibleGroupBox' in lines[i]:
            # Find end of class (next class or end of file)
            j = i + 1
            indent_level = 0
            while j < len(lines):
                if lines[j].startswith('class ') and 'CollapsibleGroupBox' not in lines[j]:
                    # Found next class
                    new_lines.append(storyboard_class)
                    added_storyboard = True
                    break
                j += 1
            
            if not added_storyboard:
                # No next class found, add before Text2VideoPane
                pass
        
        if not added_storyboard and 'class Text2VideoPane' in lines[i]:
            new_lines.insert(-1, storyboard_class + '\n\n')
            added_storyboard = True
        
        i += 1
    
    if not added_storyboard:
        print("❌ Could not find insertion point for StoryboardView")
        return False
    
    # Step 3: Replace scenes tab section (lines ~499-507)
    lines = new_lines
    new_lines = []
    i = 0
    replaced_scenes_tab = False
    
    while i < len(lines):
        # Find "# Tab 3: Scene Results"
        if '# Tab 3: Scene Results' in lines[i] or 'Tab 3: Scene Results' in lines[i]:
            # Add comment
            new_lines.append(lines[i])
            i += 1
            
            # Skip old code until self.result_tabs.addTab
            while i < len(lines) and 'self.result_tabs.addTab(scenes_widget' not in lines[i]:
                i += 1
            
            # Add new code
            new_lines.append('        scenes_widget = QWidget()\n')
            new_lines.append('        scenes_layout = QVBoxLayout(scenes_widget)\n')
            new_lines.append('        scenes_layout.setContentsMargins(4, 4, 4, 4)\n')
            new_lines.append('\n')
            new_lines.append('        # Toggle buttons\n')
            new_lines.append('        toggle_widget = QWidget()\n')
            new_lines.append('        toggle_layout = QHBoxLayout(toggle_widget)\n')
            new_lines.append('        toggle_layout.setContentsMargins(8, 8, 8, 8)\n')
            new_lines.append('        toggle_layout.setSpacing(8)\n')
            new_lines.append('\n')
            new_lines.append('        self.btn_view_card = QPushButton("📇 Card")\n')
            new_lines.append('        self.btn_view_card.setCheckable(True)\n')
            new_lines.append('        self.btn_view_card.setChecked(True)\n')
            new_lines.append('        self.btn_view_card.setFixedHeight(34)\n')
            new_lines.append('        self.btn_view_card.setFixedWidth(100)\n')
            new_lines.append('        self.btn_view_card.setStyleSheet("""\n')
            new_lines.append('            QPushButton {\n')
            new_lines.append('                background: white;\n')
            new_lines.append('                border: 2px solid #BDBDBD;\n')
            new_lines.append('                border-radius: 6px;\n')
            new_lines.append('                font-size: 13px;\n')
            new_lines.append('                font-weight: 600;\n')
            new_lines.append('            }\n')
            new_lines.append('            QPushButton:checked {\n')
            new_lines.append('                background: #1E88E5;\n')
            new_lines.append('                border: 2px solid #1E88E5;\n')
            new_lines.append('                color: white;\n')
            new_lines.append('            }\n')
            new_lines.append('            QPushButton:hover { border: 2px solid #1E88E5; }\n')
            new_lines.append('        """)\n')
            new_lines.append('        self.btn_view_card.clicked.connect(lambda: self._switch_view("card"))\n')
            new_lines.append('\n')
            new_lines.append('        self.btn_view_storyboard = QPushButton("📊 Storyboard")\n')
            new_lines.append('        self.btn_view_storyboard.setCheckable(True)\n')
            new_lines.append('        self.btn_view_storyboard.setFixedHeight(34)\n')
            new_lines.append('        self.btn_view_storyboard.setFixedWidth(120)\n')
            new_lines.append('        self.btn_view_storyboard.setStyleSheet(self.btn_view_card.styleSheet())\n')
            new_lines.append('        self.btn_view_storyboard.clicked.connect(lambda: self._switch_view("storyboard"))\n')
            new_lines.append('\n')
            new_lines.append('        toggle_layout.addWidget(self.btn_view_card)\n')
            new_lines.append('        toggle_layout.addWidget(self.btn_view_storyboard)\n')
            new_lines.append('        toggle_layout.addStretch()\n')
            new_lines.append('        scenes_layout.addWidget(toggle_widget)\n')
            new_lines.append('\n')
            new_lines.append('        # Stacked widget\n')
            new_lines.append('        from PyQt5.QtWidgets import QStackedWidget\n')
            new_lines.append('        self.view_stack = QStackedWidget()\n')
            new_lines.append('\n')
            new_lines.append('        # Card view\n')
            new_lines.append('        self.cards = QListWidget()\n')
            new_lines.append('        self.cards.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)\n')
            new_lines.append('        self.cards.setIconSize(QSize(240, 135))\n')
            new_lines.append('        self.cards.itemDoubleClicked.connect(self._open_card_prompt_detail)\n')
            new_lines.append('        self.view_stack.addWidget(self.cards)\n')
            new_lines.append('\n')
            new_lines.append('        # Storyboard view\n')
            new_lines.append('        self.storyboard_view = StoryboardView(self)\n')
            new_lines.append('        self.storyboard_view.scene_clicked.connect(self._show_prompt_detail)\n')
            new_lines.append('        self.view_stack.addWidget(self.storyboard_view)\n')
            new_lines.append('\n')
            new_lines.append('        scenes_layout.addWidget(self.view_stack)\n')
            new_lines.append(lines[i])  # Add the addTab line
            replaced_scenes_tab = True
            i += 1
            continue
        
        new_lines.append(lines[i])
        i += 1
    
    if not replaced_scenes_tab:
        print("⚠️  Could not find scenes tab section, adding anyway")
    
    # Step 4: Replace _render_card_text method
    lines = new_lines
    new_lines = []
    i = 0
    replaced_render = False
    
    while i < len(lines):
        if 'def _render_card_text(self' in lines[i]:
            # Skip old method
            new_lines.append(render_method)
            while i < len(lines) and not (lines[i].strip().startswith('def ') and '_render_card_text' not in lines[i]):
                i += 1
            replaced_render = True
            continue
        
        new_lines.append(lines[i])
        i += 1
    
    if not replaced_render:
        print("⚠️  Could not replace _render_card_text")
    
    # Step 5: Add new methods at end of class
    lines = new_lines
    new_lines = []
    
    # Find last line of Text2VideoPane class
    last_method_line = 0
    for i, line in enumerate(lines):
        if line.strip() and not line[0].isspace():
            # Non-indented line (new class or module-level)
            if i > 100:  # Skip early module stuff
                # Add methods before this line
                new_lines = lines[:i] + [new_methods + '\n\n'] + lines[i:]
                break
    else:
        # No other class found, add at end
        new_lines = lines + [new_methods]
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ File patched successfully: {filepath}")
    print(f"   Added {len(storyboard_class.split(chr(10)))} lines for StoryboardView")
    print(f"   Updated _render_card_text method")
    print(f"   Added 4 new methods")
    
    return True


def main():
    print("=" * 60)
    print("🚀 Simple Storyboard Patcher - Issue #7")
    print("=" * 60)
    print()
    
    if not os.path.exists('ui'):
        print("❌ Run from project root (where 'ui' folder exists)")
        return 1
    
    if patch_file():
        print()
        print("=" * 60)
        print("✅ Patch completed!")
        print("=" * 60)
        print()
        print("📋 Next steps:")
        print("   1. Test: python -B main_image2video.py")
        print("   2. Look for toggle buttons in '🎬 Kết quả cảnh' tab")
        print("   3. Try Card/Storyboard views")
        print("   4. Double-click scenes for details")
        print()
        return 0
    else:
        print()
        print("❌ Patch failed - check errors above")
        return 1


if __name__ == "__main__":
    exit(main())