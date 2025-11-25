#!/usr/bin/env python3
"""
UI WIDGETS - Reusable UI Components
Standard widget library for 0RB_AETHER UI.
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from .. import (
    Widget, Renderer, Event, EventType,
    Point, Size, Rect, Padding,
    Color, Colors, Border, Shadow, Style,
    Alignment, Direction,
)


# =============================================================================
# LAYOUT WIDGETS
# =============================================================================

class Container(Widget):
    """Basic container widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = kwargs.get('padding', Padding.all(0))

    def render(self, renderer: Renderer):
        # Background
        if self.style.background:
            renderer.draw_rect(self.bounds, self.style.background, self.style.border)

        # Render children
        for child in self.children:
            if child.visible:
                child.render(renderer)

    def layout(self, available: Rect):
        self.bounds = available

        # Apply padding
        content = Rect(
            x=available.x + self.padding.left,
            y=available.y + self.padding.top,
            width=available.width - self.padding.left - self.padding.right,
            height=available.height - self.padding.top - self.padding.bottom,
        )

        for child in self.children:
            child.layout(content)


class Row(Widget):
    """Horizontal layout"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing = kwargs.get('spacing', 8)
        self.align = kwargs.get('align', Alignment.START)
        self.cross_align = kwargs.get('cross_align', Alignment.CENTER)

    def render(self, renderer: Renderer):
        if self.style.background:
            renderer.draw_rect(self.bounds, self.style.background, self.style.border)

        for child in self.children:
            if child.visible:
                child.render(renderer)

    def layout(self, available: Rect):
        self.bounds = available

        if not self.children:
            return

        # Calculate total width needed
        total_spacing = self.spacing * (len(self.children) - 1)
        child_width = (available.width - total_spacing) // len(self.children)

        x = available.x
        for child in self.children:
            child_rect = Rect(
                x=x,
                y=available.y,
                width=child_width,
                height=available.height,
            )
            child.layout(child_rect)
            x += child_width + self.spacing


class Column(Widget):
    """Vertical layout"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing = kwargs.get('spacing', 8)
        self.align = kwargs.get('align', Alignment.START)
        self.cross_align = kwargs.get('cross_align', Alignment.STRETCH)

    def render(self, renderer: Renderer):
        if self.style.background:
            renderer.draw_rect(self.bounds, self.style.background, self.style.border)

        for child in self.children:
            if child.visible:
                child.render(renderer)

    def layout(self, available: Rect):
        self.bounds = available

        if not self.children:
            return

        total_spacing = self.spacing * (len(self.children) - 1)
        child_height = (available.height - total_spacing) // len(self.children)

        y = available.y
        for child in self.children:
            child_rect = Rect(
                x=available.x,
                y=y,
                width=available.width,
                height=child_height,
            )
            child.layout(child_rect)
            y += child_height + self.spacing


class Stack(Widget):
    """Stacked layout (children overlap)"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render(self, renderer: Renderer):
        if self.style.background:
            renderer.draw_rect(self.bounds, self.style.background, self.style.border)

        for child in self.children:
            if child.visible:
                child.render(renderer)

    def layout(self, available: Rect):
        self.bounds = available

        for child in self.children:
            child.layout(available)


class Spacer(Widget):
    """Flexible spacer widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flex = kwargs.get('flex', 1)

    def render(self, renderer: Renderer):
        pass  # Invisible


class ScrollView(Widget):
    """Scrollable container"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll_x = 0
        self.scroll_y = 0
        self.content_size = Size(0, 0)

        self.on(EventType.SCROLL, self._handle_scroll)

    def _handle_scroll(self, event: Event):
        if event.delta:
            self.scroll_y -= event.delta.y * 20
            self.scroll_y = max(0, min(self.scroll_y, self.content_size.height - self.bounds.height))
            self.mark_dirty()

    def render(self, renderer: Renderer):
        if self.style.background:
            renderer.draw_rect(self.bounds, self.style.background, self.style.border)

        renderer.clip(self.bounds)

        for child in self.children:
            if child.visible:
                # Offset by scroll
                original_y = child.bounds.y
                child.bounds.y -= self.scroll_y
                child.render(renderer)
                child.bounds.y = original_y

        renderer.reset_clip()

    def layout(self, available: Rect):
        self.bounds = available

        # Calculate content size
        y = 0
        for child in self.children:
            child.layout(Rect(available.x, y, available.width, 100))  # Placeholder height
            y += child.bounds.height

        self.content_size = Size(available.width, y)


# =============================================================================
# TEXT WIDGETS
# =============================================================================

class Text(Widget):
    """Text display widget"""

    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = kwargs.get('font_size', 14)
        self.color = kwargs.get('color', Colors.WHITE)
        self.align = kwargs.get('align', Alignment.START)

    def render(self, renderer: Renderer):
        if self.style.background:
            renderer.draw_rect(self.bounds, self.style.background)

        # Calculate text position based on alignment
        x = self.bounds.x
        if self.align == Alignment.CENTER:
            x = self.bounds.x + self.bounds.width // 2
        elif self.align == Alignment.END:
            x = self.bounds.right

        renderer.draw_text(
            self.text,
            Point(x, self.bounds.y + self.bounds.height // 2),
            self.color,
            self.font_size,
        )


class Heading(Text):
    """Heading text"""

    SIZES = {
        1: 32,
        2: 28,
        3: 24,
        4: 20,
        5: 16,
        6: 14,
    }

    def __init__(self, text: str = "", level: int = 1, **kwargs):
        kwargs['font_size'] = kwargs.get('font_size', self.SIZES.get(level, 24))
        super().__init__(text, **kwargs)
        self.level = level


class Icon(Widget):
    """Icon widget"""

    # Icon mappings (would use actual icon font/images)
    ICONS = {
        "home": "🏠",
        "settings": "⚙️",
        "user": "👤",
        "search": "🔍",
        "menu": "☰",
        "close": "✕",
        "check": "✓",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
        "arrow_up": "↑",
        "arrow_down": "↓",
        "arrow_left": "←",
        "arrow_right": "→",
    }

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.size = kwargs.get('size', 24)
        self.color = kwargs.get('color', Colors.WHITE)

    def render(self, renderer: Renderer):
        icon_char = self.ICONS.get(self.name, "?")
        renderer.draw_text(
            icon_char,
            Point(self.bounds.x, self.bounds.y),
            self.color,
            self.size,
        )


# =============================================================================
# INPUT WIDGETS
# =============================================================================

class Button(Widget):
    """Button widget"""

    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.focusable = True
        self.variant = kwargs.get('variant', 'primary')  # primary, secondary, outline, ghost

        # State
        self.hovered = False
        self.pressed = False

        # Events
        self.on_click = kwargs.get('on_click')

        self.on(EventType.CLICK, self._handle_click)
        self.on(EventType.HOVER, self._handle_hover)

    def _handle_click(self, event: Event):
        if self.enabled and self.on_click:
            self.on_click()

    def _handle_hover(self, event: Event):
        self.hovered = True
        self.mark_dirty()

    def _get_colors(self) -> tuple:
        """Get background and text colors based on variant and state"""
        if not self.enabled:
            return Colors.GRAY_600, Colors.GRAY_400

        colors = {
            'primary': (Colors.PRIMARY, Colors.WHITE),
            'secondary': (Colors.SECONDARY, Colors.WHITE),
            'success': (Colors.SUCCESS, Colors.WHITE),
            'warning': (Colors.WARNING, Colors.BLACK),
            'error': (Colors.ERROR, Colors.WHITE),
            'outline': (Colors.TRANSPARENT, Colors.PRIMARY),
            'ghost': (Colors.TRANSPARENT, Colors.WHITE),
        }

        bg, fg = colors.get(self.variant, (Colors.PRIMARY, Colors.WHITE))

        if self.pressed:
            bg = Color(bg.r - 30, bg.g - 30, bg.b - 30, bg.a)
        elif self.hovered:
            bg = Color(bg.r + 20, bg.g + 20, bg.b + 20, bg.a)

        return bg, fg

    def render(self, renderer: Renderer):
        bg_color, text_color = self._get_colors()

        border = Border(
            width=1 if self.variant == 'outline' else 0,
            color=Colors.PRIMARY if self.variant == 'outline' else Colors.TRANSPARENT,
            radius=4,
        )

        renderer.draw_rect(self.bounds, bg_color, border)
        renderer.draw_text(
            self.text,
            Point(
                self.bounds.x + self.bounds.width // 2,
                self.bounds.y + self.bounds.height // 2,
            ),
            text_color,
            14,
        )


class TextInput(Widget):
    """Text input field"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = kwargs.get('value', '')
        self.placeholder = kwargs.get('placeholder', '')
        self.focusable = True
        self.cursor_pos = len(self.value)

        self.on_change = kwargs.get('on_change')

        self.on(EventType.KEY_DOWN, self._handle_key)
        self.on(EventType.CLICK, self._handle_click)

    def _handle_key(self, event: Event):
        if not self.focused:
            return

        if event.key == 'Backspace':
            if self.cursor_pos > 0:
                self.value = self.value[:self.cursor_pos-1] + self.value[self.cursor_pos:]
                self.cursor_pos -= 1
        elif event.key == 'Delete':
            if self.cursor_pos < len(self.value):
                self.value = self.value[:self.cursor_pos] + self.value[self.cursor_pos+1:]
        elif event.key == 'Left':
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif event.key == 'Right':
            self.cursor_pos = min(len(self.value), self.cursor_pos + 1)
        elif event.key == 'Home':
            self.cursor_pos = 0
        elif event.key == 'End':
            self.cursor_pos = len(self.value)
        elif len(event.key) == 1:  # Regular character
            self.value = self.value[:self.cursor_pos] + event.key + self.value[self.cursor_pos:]
            self.cursor_pos += 1

        if self.on_change:
            self.on_change(self.value)

        self.mark_dirty()

    def _handle_click(self, event: Event):
        # Focus and position cursor
        self.cursor_pos = len(self.value)

    def render(self, renderer: Renderer):
        # Background
        bg_color = Colors.GRAY_800 if self.focused else Colors.GRAY_700
        border = Border(
            width=2 if self.focused else 1,
            color=Colors.PRIMARY if self.focused else Colors.GRAY_600,
            radius=4,
        )
        renderer.draw_rect(self.bounds, bg_color, border)

        # Text or placeholder
        display_text = self.value if self.value else self.placeholder
        text_color = Colors.WHITE if self.value else Colors.GRAY_500

        renderer.draw_text(
            display_text,
            Point(self.bounds.x + 8, self.bounds.y + self.bounds.height // 2),
            text_color,
            14,
        )

        # Cursor
        if self.focused:
            cursor_x = self.bounds.x + 8 + self.cursor_pos * 8  # Approximate
            renderer.draw_line(
                Point(cursor_x, self.bounds.y + 4),
                Point(cursor_x, self.bounds.bottom - 4),
                Colors.WHITE,
                2,
            )


class Checkbox(Widget):
    """Checkbox widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.checked = kwargs.get('checked', False)
        self.label = kwargs.get('label', '')
        self.focusable = True

        self.on_change = kwargs.get('on_change')

        self.on(EventType.CLICK, self._handle_click)

    def _handle_click(self, event: Event):
        if self.enabled:
            self.checked = not self.checked
            if self.on_change:
                self.on_change(self.checked)
            self.mark_dirty()

    def render(self, renderer: Renderer):
        # Checkbox box
        box_size = 20
        box_rect = Rect(
            self.bounds.x,
            self.bounds.y + (self.bounds.height - box_size) // 2,
            box_size,
            box_size,
        )

        bg_color = Colors.PRIMARY if self.checked else Colors.GRAY_700
        border = Border(width=2, color=Colors.PRIMARY, radius=4)

        renderer.draw_rect(box_rect, bg_color, border)

        # Checkmark
        if self.checked:
            renderer.draw_text(
                "✓",
                Point(box_rect.x + 3, box_rect.y + 2),
                Colors.WHITE,
                16,
            )

        # Label
        if self.label:
            renderer.draw_text(
                self.label,
                Point(self.bounds.x + box_size + 8, self.bounds.y + self.bounds.height // 2),
                Colors.WHITE,
                14,
            )


class Slider(Widget):
    """Slider widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = kwargs.get('value', 0.5)
        self.min_value = kwargs.get('min', 0.0)
        self.max_value = kwargs.get('max', 1.0)
        self.focusable = True

        self.on_change = kwargs.get('on_change')
        self._dragging = False

        self.on(EventType.CLICK, self._handle_click)
        self.on(EventType.DRAG, self._handle_drag)

    def _handle_click(self, event: Event):
        self._update_value_from_position(event.position.x)

    def _handle_drag(self, event: Event):
        self._update_value_from_position(event.position.x)

    def _update_value_from_position(self, x: int):
        ratio = (x - self.bounds.x) / self.bounds.width
        ratio = max(0, min(1, ratio))
        self.value = self.min_value + ratio * (self.max_value - self.min_value)

        if self.on_change:
            self.on_change(self.value)

        self.mark_dirty()

    def render(self, renderer: Renderer):
        # Track
        track_height = 4
        track_rect = Rect(
            self.bounds.x,
            self.bounds.y + (self.bounds.height - track_height) // 2,
            self.bounds.width,
            track_height,
        )
        renderer.draw_rect(track_rect, Colors.GRAY_600, Border(radius=2))

        # Filled portion
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        filled_rect = Rect(
            track_rect.x,
            track_rect.y,
            int(track_rect.width * ratio),
            track_rect.height,
        )
        renderer.draw_rect(filled_rect, Colors.PRIMARY, Border(radius=2))

        # Thumb
        thumb_size = 16
        thumb_x = self.bounds.x + int(self.bounds.width * ratio) - thumb_size // 2
        thumb_rect = Rect(
            thumb_x,
            self.bounds.y + (self.bounds.height - thumb_size) // 2,
            thumb_size,
            thumb_size,
        )
        renderer.draw_rect(thumb_rect, Colors.WHITE, Border(radius=thumb_size // 2))


class Select(Widget):
    """Dropdown select widget"""

    def __init__(self, options: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.options = options or []
        self.selected_index = kwargs.get('selected', 0)
        self.focusable = True
        self.expanded = False

        self.on_change = kwargs.get('on_change')

        self.on(EventType.CLICK, self._handle_click)

    @property
    def selected_value(self) -> str:
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return ""

    def _handle_click(self, event: Event):
        if self.expanded:
            # Check if clicked on an option
            option_height = 32
            y_offset = event.position.y - self.bounds.y - 40  # Below header
            if y_offset > 0:
                clicked_index = y_offset // option_height
                if 0 <= clicked_index < len(self.options):
                    self.selected_index = clicked_index
                    if self.on_change:
                        self.on_change(self.selected_value)

        self.expanded = not self.expanded
        self.mark_dirty()

    def render(self, renderer: Renderer):
        # Main box
        bg_color = Colors.GRAY_700
        border = Border(
            width=2 if self.focused else 1,
            color=Colors.PRIMARY if self.focused else Colors.GRAY_600,
            radius=4,
        )
        renderer.draw_rect(self.bounds, bg_color, border)

        # Selected value
        renderer.draw_text(
            self.selected_value or "Select...",
            Point(self.bounds.x + 8, self.bounds.y + 12),
            Colors.WHITE if self.selected_value else Colors.GRAY_500,
            14,
        )

        # Arrow
        arrow = "▼" if not self.expanded else "▲"
        renderer.draw_text(
            arrow,
            Point(self.bounds.right - 20, self.bounds.y + 12),
            Colors.GRAY_400,
            12,
        )

        # Dropdown
        if self.expanded:
            dropdown_rect = Rect(
                self.bounds.x,
                self.bounds.bottom,
                self.bounds.width,
                len(self.options) * 32 + 8,
            )
            renderer.draw_rect(dropdown_rect, Colors.GRAY_800, Border(width=1, color=Colors.GRAY_600, radius=4))

            y = dropdown_rect.y + 4
            for i, option in enumerate(self.options):
                option_bg = Colors.PRIMARY if i == self.selected_index else Colors.TRANSPARENT
                option_rect = Rect(self.bounds.x + 4, y, self.bounds.width - 8, 28)
                renderer.draw_rect(option_rect, option_bg, Border(radius=4))
                renderer.draw_text(option, Point(self.bounds.x + 12, y + 6), Colors.WHITE, 14)
                y += 32


# =============================================================================
# DISPLAY WIDGETS
# =============================================================================

class Card(Container):
    """Card container with shadow"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style.background = kwargs.get('background', Colors.GRAY_800)
        self.style.border = Border(radius=8)
        self.style.shadow = Shadow(offset_y=4, blur=8)
        self.padding = kwargs.get('padding', Padding.all(16))


class Badge(Widget):
    """Badge/tag widget"""

    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.variant = kwargs.get('variant', 'default')

    def _get_colors(self) -> tuple:
        variants = {
            'default': (Colors.GRAY_600, Colors.WHITE),
            'primary': (Colors.PRIMARY, Colors.WHITE),
            'success': (Colors.SUCCESS, Colors.WHITE),
            'warning': (Colors.WARNING, Colors.BLACK),
            'error': (Colors.ERROR, Colors.WHITE),
        }
        return variants.get(self.variant, variants['default'])

    def render(self, renderer: Renderer):
        bg, fg = self._get_colors()
        renderer.draw_rect(self.bounds, bg, Border(radius=12))
        renderer.draw_text(
            self.text,
            Point(self.bounds.x + 8, self.bounds.y + 4),
            fg,
            12,
        )


class ProgressBar(Widget):
    """Progress bar widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = kwargs.get('value', 0.0)  # 0-1
        self.variant = kwargs.get('variant', 'primary')
        self.show_label = kwargs.get('show_label', True)

    def render(self, renderer: Renderer):
        # Track
        renderer.draw_rect(self.bounds, Colors.GRAY_700, Border(radius=4))

        # Fill
        fill_width = int(self.bounds.width * max(0, min(1, self.value)))
        if fill_width > 0:
            fill_rect = Rect(self.bounds.x, self.bounds.y, fill_width, self.bounds.height)
            fill_color = Colors.PRIMARY if self.variant == 'primary' else Colors.SUCCESS
            renderer.draw_rect(fill_rect, fill_color, Border(radius=4))

        # Label
        if self.show_label:
            label = f"{int(self.value * 100)}%"
            renderer.draw_text(
                label,
                Point(self.bounds.x + self.bounds.width // 2, self.bounds.y + 4),
                Colors.WHITE,
                12,
            )


class Avatar(Widget):
    """Avatar widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', '')
        self.image = kwargs.get('image')  # Image path
        self.size = kwargs.get('size', 40)

    def _get_initials(self) -> str:
        parts = self.name.split()
        if len(parts) >= 2:
            return parts[0][0].upper() + parts[1][0].upper()
        elif parts:
            return parts[0][0].upper()
        return "?"

    def render(self, renderer: Renderer):
        # Circle background
        renderer.draw_rect(
            self.bounds,
            Colors.PRIMARY,
            Border(radius=self.size // 2),
        )

        if self.image:
            renderer.draw_image(self.image, self.bounds)
        else:
            # Initials
            renderer.draw_text(
                self._get_initials(),
                Point(self.bounds.x + self.size // 4, self.bounds.y + self.size // 4),
                Colors.WHITE,
                self.size // 2,
            )


class Divider(Widget):
    """Horizontal or vertical divider"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.direction = kwargs.get('direction', Direction.HORIZONTAL)
        self.color = kwargs.get('color', Colors.GRAY_600)

    def render(self, renderer: Renderer):
        if self.direction == Direction.HORIZONTAL:
            y = self.bounds.y + self.bounds.height // 2
            renderer.draw_line(
                Point(self.bounds.x, y),
                Point(self.bounds.right, y),
                self.color,
                1,
            )
        else:
            x = self.bounds.x + self.bounds.width // 2
            renderer.draw_line(
                Point(x, self.bounds.y),
                Point(x, self.bounds.bottom),
                self.color,
                1,
            )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Layout
    "Container",
    "Row",
    "Column",
    "Stack",
    "Spacer",
    "ScrollView",

    # Text
    "Text",
    "Heading",
    "Icon",

    # Input
    "Button",
    "TextInput",
    "Checkbox",
    "Slider",
    "Select",

    # Display
    "Card",
    "Badge",
    "ProgressBar",
    "Avatar",
    "Divider",
]
