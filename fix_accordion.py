#!/usr/bin/env python3
"""
Fix UI Issues:
1. Add RippleButton with animation
2. Reduce button size (too much space)
3. Fix missing text in tabs
"""

from pathlib import Path

def create_ripple_button(repo_root):
    """Create RippleButton widget with Material Design ripple effect"""
    widget_path = repo_root / "ui" / "widgets" / "ripple_button.py"
    widget_path.parent.mkdir(parents=True, exist_ok=True)
    
    ripple_code = '''# -*- coding: utf-8 -*-
"""
Material Design Ripple Button
Implements ripple effect animation on click
"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect, QTimer, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPoint

class RippleButton(QPushButton):
    """QPushButton with Material Design ripple effect"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ripple_radius = 0
        self._ripple_pos = QPoint()
        self._ripple_animation = None
        self._ripple_color = QColor(255, 255, 255, 80)
        
    def mousePressEvent(self, event):
        """Start ripple animation on mouse press"""
        self._ripple_pos = event.pos()
        self._start_ripple()
        super().mousePressEvent(event)
    
    def _start_ripple(self):
        """Start the ripple animation"""
        # Calculate max radius (corner to corner)
        max_radius = max(self.width(), self.height()) * 1.5
        
        # Create animation
        self._ripple_animation = QPropertyAnimation(self, b"ripple_radius")
        self._ripple_animation.setDuration(600)  # 600ms duration
        self._ripple_animation.setStartValue(0)
        self._ripple_animation.setEndValue(max_radius)
        self._ripple_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._ripple_animation.finished.connect(self._reset_ripple)
        self._ripple_animation.start()
    
    def _reset_ripple(self):
        """Reset ripple after animation completes"""
        self._ripple_radius = 0
        self.update()
    
    @pyqtProperty(float)
    def ripple_radius(self):
        return self._ripple_radius
    
    @ripple_radius.setter
    def ripple_radius(self, value):
        self._ripple_radius = value
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Custom paint to draw ripple effect"""
        super().paintEvent(event)
        
        if self._ripple_radius > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Clip to button shape
            path = QPainterPath()
            path.addRoundedRect(self.rect(), 20, 20)  # Match button border-radius
            painter.setClipPath(path)
            
            # Draw ripple
            painter.setBrush(self._ripple_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self._ripple_pos, self._ripple_radius, self._ripple_radius)
'''
    
    with open(widget_path, 'w', encoding='utf-8') as f:
        f.write(ripple_code)
    
    print(f"✅ Created: {widget_path}")

def fix_button_sizes(repo_root):
    """Fix button sizes - make them more compact"""
    theme_file = repo_root / "ui" / "styles" / "light_theme.py"
    
    with open(theme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reduce button padding and height
    old_button_style = '''QPushButton {
    background: #1E88E5;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    min-height: 32px;
    font-weight: 600;
    font-size: 14px;
    font-family: "Segoe UI", Arial, sans-serif;
}'''
    
    new_button_style = '''QPushButton {
    background: #1E88E5;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    min-height: 28px;
    max-height: 32px;
    font-weight: 500;
    font-size: 13px;
    font-family: "Segoe UI", Arial, sans-serif;
}'''
    
    content = content.replace(old_button_style, new_button_style)
    
    with open(theme_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed button sizes in: {theme_file}")

def fix_tab_text(repo_root):
    """Fix missing text in tabs - reduce padding, fix font size"""
    theme_file = repo_root / "ui" / "styles" / "light_theme.py"
    
    with open(theme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix main tabs (top level)
    old_tab_style = '''QTabBar::tab {
    font-family: "Segoe UI", Arial, sans-serif;
    font-weight: 700;
    font-size: 15px;
    min-width: 150px;
    padding: 12px 24px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    color: #FFFFFF;
    background: #BDBDBD;
}'''
    
    new_tab_style = '''QTabBar::tab {
    font-family: "Segoe UI", Arial, sans-serif;
    font-weight: 600;
    font-size: 13px;
    min-width: 120px;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #FFFFFF;
    background: #BDBDBD;
}'''
    
    content = content.replace(old_tab_style, new_tab_style)
    
    # Fix tab selected state
    old_selected = '''QTabBar::tab:selected {
    border-bottom: 4px solid #212121;
    font-size: 15px;
    padding-bottom: 8px;
}'''
    
    new_selected = '''QTabBar::tab:selected {
    border-bottom: 3px solid #212121;
    font-size: 13px;
    padding-bottom: 5px;
    font-weight: 700;
}'''
    
    content = content.replace(old_selected, new_selected)
    
    with open(theme_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed tab text visibility in: {theme_file}")

def add_ripple_to_buttons(repo_root):
    """Create helper function to convert QPushButton to RippleButton"""
    utils_file = repo_root / "ui" / "widgets" / "button_utils.py"
    
    utils_code = '''# -*- coding: utf-8 -*-
"""
Button utilities for easy RippleButton usage
"""

from ui.widgets.ripple_button import RippleButton

def create_ripple_button(text, object_name=None, parent=None):
    """
    Create a RippleButton with common settings
    
    Args:
        text: Button text
        object_name: Optional objectName for styling
        parent: Parent widget
    
    Returns:
        RippleButton instance
    """
    btn = RippleButton(text, parent)
    if object_name:
        btn.setObjectName(object_name)
    btn.setMinimumHeight(28)
    btn.setMaximumHeight(32)
    return btn

# Example usage:
# from ui.widgets.button_utils import create_ripple_button
# 
# btn_save = create_ripple_button("💾 Lưu", "btn_save")
# btn_delete = create_ripple_button("🗑️ Xóa", "btn_danger")
'''
    
    with open(utils_file, 'w', encoding='utf-8') as f:
        f.write(utils_code)
    
    print(f"✅ Created: {utils_file}")

def create_demo_file(repo_root):
    """Create demo file to test RippleButton"""
    demo_file = repo_root / "test_ripple_button.py"
    
    demo_code = '''#!/usr/bin/env python3
"""
Demo: Test RippleButton with Material Design ripple effect
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from ui.widgets.ripple_button import RippleButton

class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RippleButton Demo")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Create ripple buttons
        btn1 = RippleButton("Click me for ripple!")
        btn1.setObjectName("btn_primary")
        
        btn2 = RippleButton("💾 Save Button")
        btn2.setObjectName("btn_save")
        
        btn3 = RippleButton("🗑️ Delete Button")
        btn3.setObjectName("btn_danger")
        
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply theme
    try:
        from ui.styles.light_theme import apply_light_theme
        apply_light_theme(app)
    except:
        pass
    
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
'''
    
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(demo_code)
    
    print(f"✅ Created demo: {demo_file}")

def main():
    print("=" * 70)
    print("🎨 FIX UI ISSUES")
    print("=" * 70)
    print()
    
    repo_root = Path(__file__).parent.resolve()
    
    # Fix 1: Create RippleButton
    print("1️⃣ Creating RippleButton widget...")
    create_ripple_button(repo_root)
    add_ripple_to_buttons(repo_root)
    print()
    
    # Fix 2: Reduce button sizes
    print("2️⃣ Fixing button sizes (more compact)...")
    fix_button_sizes(repo_root)
    print()
    
    # Fix 3: Fix tab text visibility
    print("3️⃣ Fixing tab text (reduce padding, adjust font)...")
    fix_tab_text(repo_root)
    print()
    
    # Create demo
    print("📝 Creating demo file...")
    create_demo_file(repo_root)
    print()
    
    print("=" * 70)
    print("✅ ALL FIXES COMPLETE!")
    print()
    print("📌 CHANGES:")
    print("  • RippleButton widget with Material ripple animation")
    print("  • Buttons: 28-32px height (was 32px+), less padding")
    print("  • Tabs: 13px font (was 15px), less padding")
    print("  • Fixed tab text visibility")
    print()
    print("🧪 TEST:")
    print("  python test_ripple_button.py  # Test ripple effect")
    print()
    print("🚀 RUN:")
    print("  python main_image2video.py")
    print("=" * 70)

if __name__ == "__main__":
    main()