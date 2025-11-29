#!/usr/bin/env python3
"""
UI APPS - Built-in Applications
Dashboard, settings, and system applications for 0RB_AETHER.
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from .. import (
    Application, Window, WindowConfig, Widget,
    Point, Rect, Padding, Color, Colors, Border,
    Event, EventType,
)
from ..widgets import (
    Container, Row, Column, Card, Text, Heading, Button,
    TextInput, Checkbox, Slider, Select, Badge, ProgressBar,
    Icon, Divider, Spacer,
)
from ..themes import get_theme, set_theme, theme_manager, Themes


# =============================================================================
# DASHBOARD
# =============================================================================

class SystemStats(Widget):
    """System statistics display"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.disk_usage = 0.0
        self.network_rx = 0
        self.network_tx = 0

    def update(self, stats: Dict[str, Any]):
        """Update stats"""
        self.cpu_usage = stats.get('cpu', 0)
        self.memory_usage = stats.get('memory', 0)
        self.disk_usage = stats.get('disk', 0)
        self.network_rx = stats.get('network_rx', 0)
        self.network_tx = stats.get('network_tx', 0)
        self.mark_dirty()

    def render(self, renderer):
        theme = get_theme()

        # Container
        renderer.draw_rect(self.bounds, theme.colors.surface, Border(radius=8))

        # Title
        renderer.draw_text("System", Point(self.bounds.x + 16, self.bounds.y + 16), theme.colors.text_primary, 18)

        # Stats
        y = self.bounds.y + 50
        stats = [
            ("CPU", self.cpu_usage, Colors.PRIMARY),
            ("Memory", self.memory_usage, Colors.SECONDARY),
            ("Disk", self.disk_usage, Colors.SUCCESS),
        ]

        for label, value, color in stats:
            # Label
            renderer.draw_text(label, Point(self.bounds.x + 16, y), theme.colors.text_secondary, 14)

            # Progress bar background
            bar_rect = Rect(self.bounds.x + 80, y, self.bounds.width - 140, 16)
            renderer.draw_rect(bar_rect, theme.colors.border, Border(radius=4))

            # Progress fill
            fill_width = int(bar_rect.width * value)
            if fill_width > 0:
                fill_rect = Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
                renderer.draw_rect(fill_rect, color, Border(radius=4))

            # Percentage
            renderer.draw_text(
                f"{int(value * 100)}%",
                Point(self.bounds.right - 50, y),
                theme.colors.text_primary,
                14,
            )

            y += 32


class AIStatus(Widget):
    """AI system status display"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agents_active = 0
        self.tasks_pending = 0
        self.tasks_completed = 0
        self.models_loaded = []

    def update(self, status: Dict[str, Any]):
        """Update AI status"""
        self.agents_active = status.get('agents', 0)
        self.tasks_pending = status.get('pending', 0)
        self.tasks_completed = status.get('completed', 0)
        self.models_loaded = status.get('models', [])
        self.mark_dirty()

    def render(self, renderer):
        theme = get_theme()

        renderer.draw_rect(self.bounds, theme.colors.surface, Border(radius=8))

        # Title
        renderer.draw_text("AI Engine", Point(self.bounds.x + 16, self.bounds.y + 16), theme.colors.text_primary, 18)

        # Metrics
        y = self.bounds.y + 50
        metrics = [
            ("Active Agents", str(self.agents_active), Colors.SUCCESS),
            ("Pending Tasks", str(self.tasks_pending), Colors.WARNING),
            ("Completed", str(self.tasks_completed), Colors.PRIMARY),
        ]

        for label, value, color in metrics:
            renderer.draw_text(label, Point(self.bounds.x + 16, y), theme.colors.text_secondary, 14)
            renderer.draw_text(value, Point(self.bounds.right - 60, y), color, 16)
            y += 28

        # Models
        if self.models_loaded:
            y += 8
            renderer.draw_text("Models", Point(self.bounds.x + 16, y), theme.colors.text_secondary, 12)
            y += 20
            for model in self.models_loaded[:3]:
                renderer.draw_text(f"• {model}", Point(self.bounds.x + 24, y), theme.colors.text_primary, 12)
                y += 18


class QuickActions(Widget):
    """Quick action buttons"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.actions = kwargs.get('actions', [])

    def render(self, renderer):
        theme = get_theme()

        renderer.draw_rect(self.bounds, theme.colors.surface, Border(radius=8))

        # Title
        renderer.draw_text("Quick Actions", Point(self.bounds.x + 16, self.bounds.y + 16), theme.colors.text_primary, 18)

        # Action buttons
        y = self.bounds.y + 50
        button_height = 36
        button_width = self.bounds.width - 32

        actions = [
            ("🔍 Search", "search"),
            ("📁 Files", "files"),
            ("⚙️ Settings", "settings"),
            ("📊 Analytics", "analytics"),
            ("🤖 AI Assistant", "assistant"),
        ]

        for label, action_id in actions:
            button_rect = Rect(self.bounds.x + 16, y, button_width, button_height)
            renderer.draw_rect(button_rect, theme.colors.background, Border(width=1, color=theme.colors.border, radius=6))
            renderer.draw_text(label, Point(button_rect.x + 12, y + 10), theme.colors.text_primary, 14)
            y += button_height + 8


class NotificationPanel(Widget):
    """Notification display panel"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notifications = []

    def add_notification(self, title: str, message: str, level: str = "info"):
        """Add notification"""
        self.notifications.insert(0, {
            "title": title,
            "message": message,
            "level": level,
            "time": datetime.now(),
        })
        self.notifications = self.notifications[:5]  # Keep last 5
        self.mark_dirty()

    def render(self, renderer):
        theme = get_theme()

        renderer.draw_rect(self.bounds, theme.colors.surface, Border(radius=8))

        # Title
        renderer.draw_text("Notifications", Point(self.bounds.x + 16, self.bounds.y + 16), theme.colors.text_primary, 18)

        if not self.notifications:
            renderer.draw_text(
                "No notifications",
                Point(self.bounds.x + 16, self.bounds.y + 60),
                theme.colors.text_secondary,
                14,
            )
            return

        # Notifications
        y = self.bounds.y + 50
        level_colors = {
            "info": Colors.INFO,
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "error": Colors.ERROR,
        }

        for notif in self.notifications[:4]:
            color = level_colors.get(notif["level"], Colors.INFO)

            # Indicator
            renderer.draw_rect(
                Rect(self.bounds.x + 16, y + 4, 4, 30),
                color,
                Border(radius=2),
            )

            # Content
            renderer.draw_text(
                notif["title"],
                Point(self.bounds.x + 28, y + 4),
                theme.colors.text_primary,
                14,
            )
            renderer.draw_text(
                notif["message"][:40] + "..." if len(notif["message"]) > 40 else notif["message"],
                Point(self.bounds.x + 28, y + 22),
                theme.colors.text_secondary,
                12,
            )

            y += 48


class Dashboard(Container):
    """Main dashboard application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.system_stats = SystemStats()
        self.ai_status = AIStatus()
        self.quick_actions = QuickActions()
        self.notifications = NotificationPanel()

        # Demo data
        self.system_stats.update({'cpu': 0.45, 'memory': 0.62, 'disk': 0.38})
        self.ai_status.update({
            'agents': 3,
            'pending': 12,
            'completed': 847,
            'models': ['Claude', 'GPT-4', 'Gemini'],
        })
        self.notifications.add_notification("System", "All systems operational", "success")
        self.notifications.add_notification("AI", "New agent deployed", "info")

    def render(self, renderer):
        theme = get_theme()

        # Background
        renderer.draw_rect(self.bounds, theme.colors.background)

        # Header
        header_rect = Rect(self.bounds.x, self.bounds.y, self.bounds.width, 60)
        renderer.draw_rect(header_rect, theme.colors.surface)
        renderer.draw_text(
            "0RB_AETHER Dashboard",
            Point(self.bounds.x + 20, self.bounds.y + 18),
            theme.colors.text_primary,
            24,
        )

        # Time
        time_str = datetime.now().strftime("%H:%M:%S")
        renderer.draw_text(
            time_str,
            Point(self.bounds.right - 100, self.bounds.y + 22),
            theme.colors.text_secondary,
            16,
        )

        # Layout grid
        content_y = self.bounds.y + 80
        col_width = (self.bounds.width - 60) // 3
        row_height = (self.bounds.height - 100) // 2

        # Row 1
        self.system_stats.bounds = Rect(20, content_y, col_width, row_height - 20)
        self.ai_status.bounds = Rect(40 + col_width, content_y, col_width, row_height - 20)
        self.quick_actions.bounds = Rect(60 + col_width * 2, content_y, col_width, row_height - 20)

        # Row 2
        self.notifications.bounds = Rect(20, content_y + row_height, self.bounds.width - 40, row_height - 20)

        # Render widgets
        self.system_stats.render(renderer)
        self.ai_status.render(renderer)
        self.quick_actions.render(renderer)
        self.notifications.render(renderer)


# =============================================================================
# SETTINGS
# =============================================================================

class SettingsPanel(Container):
    """Settings application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_section = "general"
        self.sections = ["general", "appearance", "ai", "security", "about"]

    def render(self, renderer):
        theme = get_theme()

        # Background
        renderer.draw_rect(self.bounds, theme.colors.background)

        # Sidebar
        sidebar_width = 200
        sidebar_rect = Rect(self.bounds.x, self.bounds.y, sidebar_width, self.bounds.height)
        renderer.draw_rect(sidebar_rect, theme.colors.surface)

        # Sidebar title
        renderer.draw_text(
            "Settings",
            Point(self.bounds.x + 20, self.bounds.y + 20),
            theme.colors.text_primary,
            20,
        )

        # Sidebar items
        y = self.bounds.y + 60
        icons = {
            "general": "⚙️",
            "appearance": "🎨",
            "ai": "🤖",
            "security": "🔒",
            "about": "ℹ️",
        }

        for section in self.sections:
            is_active = section == self.current_section
            item_rect = Rect(self.bounds.x + 8, y, sidebar_width - 16, 40)

            if is_active:
                renderer.draw_rect(item_rect, theme.colors.primary.with_alpha(50), Border(radius=6))

            icon = icons.get(section, "•")
            renderer.draw_text(
                f"{icon} {section.title()}",
                Point(item_rect.x + 12, y + 12),
                theme.colors.text_primary if is_active else theme.colors.text_secondary,
                14,
            )
            y += 44

        # Content area
        content_rect = Rect(
            self.bounds.x + sidebar_width,
            self.bounds.y,
            self.bounds.width - sidebar_width,
            self.bounds.height,
        )

        # Render current section
        if self.current_section == "general":
            self._render_general(renderer, content_rect)
        elif self.current_section == "appearance":
            self._render_appearance(renderer, content_rect)
        elif self.current_section == "ai":
            self._render_ai(renderer, content_rect)
        elif self.current_section == "security":
            self._render_security(renderer, content_rect)
        elif self.current_section == "about":
            self._render_about(renderer, content_rect)

    def _render_section_header(self, renderer, rect: Rect, title: str):
        """Render section header"""
        theme = get_theme()
        renderer.draw_text(title, Point(rect.x + 24, rect.y + 24), theme.colors.text_primary, 24)
        return rect.y + 70

    def _render_setting_row(self, renderer, x: int, y: int, width: int, label: str, description: str = None):
        """Render a setting row"""
        theme = get_theme()
        renderer.draw_text(label, Point(x, y), theme.colors.text_primary, 16)
        if description:
            renderer.draw_text(description, Point(x, y + 22), theme.colors.text_secondary, 12)
        return y + (50 if description else 36)

    def _render_general(self, renderer, rect: Rect):
        """Render general settings"""
        theme = get_theme()
        y = self._render_section_header(renderer, rect, "General")

        settings = [
            ("Language", "English (US)", "Interface language"),
            ("Timezone", "Auto-detect", "System timezone"),
            ("Date Format", "YYYY-MM-DD", "Date display format"),
            ("Startup", "Open dashboard", "Action on startup"),
        ]

        for label, value, desc in settings:
            y = self._render_setting_row(renderer, rect.x + 24, y, rect.width - 48, label, desc)

            # Value display
            renderer.draw_text(
                value,
                Point(rect.right - 150, y - 40),
                theme.colors.text_secondary,
                14,
            )

    def _render_appearance(self, renderer, rect: Rect):
        """Render appearance settings"""
        theme = get_theme()
        y = self._render_section_header(renderer, rect, "Appearance")

        # Theme selection
        renderer.draw_text("Theme", Point(rect.x + 24, y), theme.colors.text_primary, 16)
        y += 30

        themes = ["Dark", "Light", "Midnight", "Cyberpunk", "0RB_AETHER"]
        x = rect.x + 24
        for theme_name in themes:
            is_current = theme_name.lower().replace(" ", "_") == theme.name.lower().replace(" ", "_")
            badge_rect = Rect(x, y, 80, 28)
            bg = theme.colors.primary if is_current else theme.colors.surface
            renderer.draw_rect(badge_rect, bg, Border(width=1, color=theme.colors.border, radius=14))
            renderer.draw_text(theme_name, Point(x + 10, y + 6), theme.colors.text_primary, 12)
            x += 90

        y += 50

        # Font size
        y = self._render_setting_row(renderer, rect.x + 24, y, rect.width - 48, "Font Size", "UI text size")

        # Animations
        y = self._render_setting_row(renderer, rect.x + 24, y, rect.width - 48, "Animations", "Enable UI animations")

    def _render_ai(self, renderer, rect: Rect):
        """Render AI settings"""
        theme = get_theme()
        y = self._render_section_header(renderer, rect, "AI Configuration")

        settings = [
            ("Default Model", "Claude Opus", "Primary AI model"),
            ("Context Length", "200K tokens", "Maximum context"),
            ("Temperature", "0.7", "Response creativity"),
            ("Safety Level", "Standard", "Content filtering"),
        ]

        for label, value, desc in settings:
            y = self._render_setting_row(renderer, rect.x + 24, y, rect.width - 48, label, desc)
            renderer.draw_text(value, Point(rect.right - 150, y - 40), theme.colors.text_secondary, 14)

    def _render_security(self, renderer, rect: Rect):
        """Render security settings"""
        theme = get_theme()
        y = self._render_section_header(renderer, rect, "Security")

        settings = [
            ("Encryption", "AES-256-GCM", "Data encryption"),
            ("2FA", "Enabled", "Two-factor auth"),
            ("Session Timeout", "30 minutes", "Auto-lock time"),
            ("Audit Logging", "Enabled", "Activity logging"),
        ]

        for label, value, desc in settings:
            y = self._render_setting_row(renderer, rect.x + 24, y, rect.width - 48, label, desc)

            # Status badge
            is_enabled = "Enabled" in value or "AES" in value
            badge_color = Colors.SUCCESS if is_enabled else Colors.GRAY_600
            badge_rect = Rect(rect.right - 100, y - 38, 70, 24)
            renderer.draw_rect(badge_rect, badge_color, Border(radius=12))
            renderer.draw_text(value, Point(rect.right - 95, y - 34), Colors.WHITE, 11)

    def _render_about(self, renderer, rect: Rect):
        """Render about section"""
        theme = get_theme()
        y = self._render_section_header(renderer, rect, "About")

        # Logo/banner area
        renderer.draw_text("0RB_AETHER", Point(rect.x + 24, y), theme.colors.primary, 32)
        y += 50

        info = [
            ("Version", "0.1.0"),
            ("Build", "2025.01.001"),
            ("Platform", "Linux x86_64"),
            ("License", "MIT"),
        ]

        for label, value in info:
            renderer.draw_text(f"{label}:", Point(rect.x + 24, y), theme.colors.text_secondary, 14)
            renderer.draw_text(value, Point(rect.x + 120, y), theme.colors.text_primary, 14)
            y += 28

        y += 20
        renderer.draw_text(
            "Love - Loyalty - Honor - Everybody Eats",
            Point(rect.x + 24, y),
            theme.colors.primary,
            14,
        )


# =============================================================================
# AI ASSISTANT
# =============================================================================

@dataclass
class ChatMessage:
    """Chat message"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class AIAssistant(Container):
    """AI chat assistant interface"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages: List[ChatMessage] = []
        self.input_value = ""

        # Welcome message
        self.messages.append(ChatMessage(
            role="assistant",
            content="Hello! I'm your 0RB_AETHER AI assistant. How can I help you today?",
        ))

    def add_message(self, role: str, content: str):
        """Add message to chat"""
        self.messages.append(ChatMessage(role=role, content=content))
        self.mark_dirty()

    def render(self, renderer):
        theme = get_theme()

        # Background
        renderer.draw_rect(self.bounds, theme.colors.background)

        # Header
        header_rect = Rect(self.bounds.x, self.bounds.y, self.bounds.width, 60)
        renderer.draw_rect(header_rect, theme.colors.surface)
        renderer.draw_text("🤖 AI Assistant", Point(self.bounds.x + 20, self.bounds.y + 18), theme.colors.text_primary, 20)

        # Messages area
        messages_rect = Rect(
            self.bounds.x,
            self.bounds.y + 60,
            self.bounds.width,
            self.bounds.height - 130,
        )

        y = messages_rect.y + 16
        for msg in self.messages[-10:]:  # Show last 10 messages
            is_user = msg.role == "user"

            # Message bubble
            bubble_width = min(self.bounds.width - 100, 400)
            bubble_x = self.bounds.right - bubble_width - 20 if is_user else self.bounds.x + 20
            bubble_color = theme.colors.primary if is_user else theme.colors.surface

            # Estimate height (rough)
            lines = len(msg.content) // 50 + 1
            bubble_height = 20 + lines * 20

            bubble_rect = Rect(bubble_x, y, bubble_width, bubble_height)
            renderer.draw_rect(bubble_rect, bubble_color, Border(radius=12))

            # Message text
            renderer.draw_text(
                msg.content[:100] + ("..." if len(msg.content) > 100 else ""),
                Point(bubble_x + 12, y + 8),
                Colors.WHITE if is_user else theme.colors.text_primary,
                14,
            )

            y += bubble_height + 12

        # Input area
        input_rect = Rect(self.bounds.x, self.bounds.bottom - 70, self.bounds.width, 70)
        renderer.draw_rect(input_rect, theme.colors.surface)

        # Input field
        field_rect = Rect(self.bounds.x + 16, input_rect.y + 15, self.bounds.width - 100, 40)
        renderer.draw_rect(field_rect, theme.colors.background, Border(width=1, color=theme.colors.border, radius=20))
        renderer.draw_text(
            self.input_value or "Type a message...",
            Point(field_rect.x + 16, field_rect.y + 12),
            theme.colors.text_primary if self.input_value else theme.colors.text_secondary,
            14,
        )

        # Send button
        send_rect = Rect(self.bounds.right - 70, input_rect.y + 15, 50, 40)
        renderer.draw_rect(send_rect, theme.colors.primary, Border(radius=20))
        renderer.draw_text("→", Point(send_rect.x + 18, send_rect.y + 10), Colors.WHITE, 18)


# =============================================================================
# APP LAUNCHER
# =============================================================================

def create_dashboard() -> Window:
    """Create dashboard window"""
    window = Window(WindowConfig(
        title="Dashboard - 0RB_AETHER",
        width=1200,
        height=800,
    ))
    window.set_content(Dashboard())
    return window


def create_settings() -> Window:
    """Create settings window"""
    window = Window(WindowConfig(
        title="Settings - 0RB_AETHER",
        width=900,
        height=600,
    ))
    window.set_content(SettingsPanel())
    return window


def create_assistant() -> Window:
    """Create AI assistant window"""
    window = Window(WindowConfig(
        title="AI Assistant - 0RB_AETHER",
        width=500,
        height=700,
    ))
    window.set_content(AIAssistant())
    return window


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Widgets
    "SystemStats",
    "AIStatus",
    "QuickActions",
    "NotificationPanel",
    "Dashboard",
    "SettingsPanel",
    "AIAssistant",
    "ChatMessage",

    # Launchers
    "create_dashboard",
    "create_settings",
    "create_assistant",
]
