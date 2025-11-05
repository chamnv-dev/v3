import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PromptViewer(QDialog):
    def __init__(self, prompt_json: str, dialogues=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prompts - Cảnh")
        self.resize(900, 650)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 11))

        # Parse JSON
        try:
            data = json.loads(prompt_json)
        except Exception:
            data = {}

        # Tab 1: Prompts
        tab1 = self._build_prompts_tab(data)
        tabs.addTab(tab1, "📝 Prompts")

        # Tab 2: Details
        tab2 = self._build_details_tab(data)
        tabs.addTab(tab2, "🎬 Chi tiết")

        # Tab 3: Raw JSON
        tab3 = QWidget()
        layout3 = QVBoxLayout(tab3)
        layout3.setContentsMargins(8, 8, 8, 8)
        ed = QTextEdit()
        ed.setReadOnly(True)
        ed.setPlainText(prompt_json)
        ed.setFont(QFont("Courier New", 10))
        layout3.addWidget(ed)
        tabs.addTab(tab3, "📄 JSON")

        layout.addWidget(tabs)

        # Close button
        btn_close = QPushButton("Đóng")
        btn_close.setMinimumHeight(36)
        btn_close.setStyleSheet("""
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
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _build_prompts_tab(self, data):
        """Build prompts tab with Vietnamese and target language prompts"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(16)

        # Extract localization prompts
        loc = data.get('localization', {})
        vi_prompt = loc.get('vi', {}).get('prompt', '')

        # Get target language prompt (usually 'en')
        tgt_prompt = ''
        for lang_key in ['en', 'ja', 'ko', 'zh', 'fr', 'de', 'es']:
            if lang_key in loc and lang_key != 'vi':
                tgt_prompt = loc.get(lang_key, {}).get('prompt', '')
                if tgt_prompt:
                    break

        # Vietnamese prompt section
        if vi_prompt:
            vi_frame = self._create_prompt_section(
                "📝 Prompt Ảnh (Vietnamese)",
                vi_prompt,
                "#E1F5FE",
                "#00ACC1"
            )
            content_layout.addWidget(vi_frame)

        # Target language prompt section
        if tgt_prompt:
            tgt_frame = self._create_prompt_section(
                "🎬 Prompt Video (Target)",
                tgt_prompt,
                "#F3E5F5",
                "#9C27B0"
            )
            content_layout.addWidget(tgt_frame)

        # If no prompts found, show placeholder
        if not vi_prompt and not tgt_prompt:
            placeholder = QLabel("Không tìm thấy prompts trong JSON")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #999; font-size: 13px; padding: 40px;")
            content_layout.addWidget(placeholder)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        return widget

    def _create_prompt_section(self, title, text, bg_color, border_color):
        """Create a styled prompt section with copy button"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Title
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_title.setStyleSheet(f"color: {border_color};")
        layout.addWidget(lbl_title)

        # Text edit
        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        text_edit.setMinimumHeight(120)
        text_edit.setMaximumHeight(200)
        text_edit.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        layout.addWidget(text_edit)

        # Copy button
        btn_copy = QPushButton("📋 Copy")
        btn_copy.setMaximumWidth(120)
        # Create darker shade for hover effect
        hover_color = self._darken_color(border_color)
        btn_copy.setStyleSheet(f"""
            QPushButton {{
                background: {border_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
        """)
        btn_copy.clicked.connect(lambda: self._copy_to_clipboard(text))
        layout.addWidget(btn_copy)

        return frame

    def _build_details_tab(self, data):
        """Build details tab with other fields"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(12)

        # Build detail sections
        details = []

        # Audio settings
        audio = data.get('audio', {})
        if audio:
            voiceover = audio.get('voiceover', {})
            bg_music = audio.get('background_music', {})

            audio_text = []
            if voiceover:
                audio_text.append("🎙️ VOICEOVER:")
                audio_text.append(f"  • Language: {voiceover.get('language', 'N/A')}")
                audio_text.append(f"  • Provider: {voiceover.get('tts_provider', 'N/A')}")
                voice_name = voiceover.get('voice_name', voiceover.get('voice_id', 'N/A'))
                audio_text.append(f"  • Voice: {voice_name}")
                audio_text.append(f"  • Style: {voiceover.get('speaking_style', 'N/A')}")

                prosody = voiceover.get('prosody', {})
                if prosody:
                    rate = prosody.get('rate', 1.0)
                    rate_desc = prosody.get('rate_description', 'normal')
                    audio_text.append(f"  • Rate: {rate:.2f}x ({rate_desc})")

                    pitch = int(prosody.get('pitch', 0))
                    pitch_desc = prosody.get('pitch_description', 'neutral')
                    audio_text.append(f"  • Pitch: {pitch:+d}st ({pitch_desc})")

                    expr = prosody.get('expressiveness', 0.5)
                    expr_desc = prosody.get('expressiveness_description', 'moderate')
                    audio_text.append(f"  • Expressiveness: {expr:.2f} ({expr_desc})")

            if bg_music:
                audio_text.append("")
                audio_text.append("🎵 BACKGROUND MUSIC:")
                audio_text.append(f"  • Type: {bg_music.get('type', 'N/A')}")
                audio_text.append(f"  • Mood: {bg_music.get('mood', 'N/A')}")
                audio_text.append(f"  • Volume: {bg_music.get('volume', 0.3):.1f}")

            if audio_text:
                details.append(("🎙️ Audio Settings", "\n".join(audio_text), "#E8F5E9", "#4CAF50"))

        # Camera direction
        camera_dir = data.get('camera_direction', [])
        if camera_dir:
            cam_text = []
            cam_text.append("🎥 CAMERA DIRECTION:")
            for i, segment in enumerate(camera_dir, 1):
                cam_text.append(f"\n  {i}. {segment.get('t', 'N/A')}:")
                cam_text.append(f"     {segment.get('shot', 'N/A')}")
            details.append(("🎥 Camera Direction", "\n".join(cam_text), "#FFF3E0", "#FF9800"))

        # Character details
        char_details = data.get('character_details', '')
        if char_details:
            details.append(("👥 Character Details", char_details, "#F3E5F5", "#9C27B0"))

        # Setting details
        setting = data.get('setting_details', '')
        if setting:
            details.append(("🎨 Visual Style", setting, "#E3F2FD", "#2196F3"))

        # Constraints
        constraints = data.get('constraints', {})
        if constraints:
            const_text = []
            const_text.append(f"⏱️ Duration: {constraints.get('duration_seconds', 'N/A')} seconds")
            const_text.append(f"📐 Aspect Ratio: {constraints.get('aspect_ratio', 'N/A')}")
            const_text.append(f"🖥️ Resolution: {constraints.get('resolution', 'N/A')}")

            style_tags = constraints.get('visual_style_tags', [])
            if style_tags:
                const_text.append(f"🎨 Style Tags: {', '.join(style_tags)}")

            camera = constraints.get('camera', {})
            if camera:
                fps = camera.get('fps', 'N/A')
                lens = camera.get('lens_hint', 'N/A')
                const_text.append(f"📹 Camera: {fps} fps, {lens}")

            details.append(("⚙️ Constraints", "\n".join(const_text), "#FFF8E1", "#FFC107"))

        # Domain context
        domain_ctx = data.get('domain_context', {})
        if domain_ctx:
            dom_text = []
            dom_text.append(f"📚 Domain: {domain_ctx.get('domain', 'N/A')}")
            dom_text.append(f"📖 Topic: {domain_ctx.get('topic', 'N/A')}")
            if domain_ctx.get('expertise_intro'):
                dom_text.append(f"\n{domain_ctx.get('expertise_intro')}")
            details.append(("📚 Domain Context", "\n".join(dom_text), "#E0F2F1", "#009688"))

        # Add all detail sections
        for title, text, bg_color, border_color in details:
            frame = self._create_detail_section(title, text, bg_color, border_color)
            content_layout.addWidget(frame)

        # If no details, show placeholder
        if not details:
            placeholder = QLabel("Không có chi tiết bổ sung")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #999; font-size: 13px; padding: 40px;")
            content_layout.addWidget(placeholder)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        return widget

    def _create_detail_section(self, title, text, bg_color, border_color):
        """Create a styled detail section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Title
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_title.setStyleSheet(f"color: {border_color};")
        layout.addWidget(lbl_title)

        # Text
        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl_text.setStyleSheet("""
            QLabel {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        layout.addWidget(lbl_text)

        return frame

    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Darken a hex color by a factor (0.0 to 1.0)"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Darken
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        try:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(text)
        except Exception:
            pass
