#!/usr/bin/env python3
"""
UI WORLDS - 0RB_AETHER Interface Layer
The visual layer connecting humans to the AI-powered Meta-OS.

Components:
- Core: Window management, rendering pipeline, event system
- Widgets: Reusable UI components
- Themes: Visual styling engine
- Apps: Built-in applications (dashboard, terminal, settings)

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib

__version__ = "0.1.0"


# =============================================================================
# ENUMS & TYPES
# =============================================================================

class WindowState(Enum):
    """Window states"""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"
    HIDDEN = "hidden"


class EventType(Enum):
    """UI event types"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    HOVER = "hover"
    FOCUS = "focus"
    BLUR = "blur"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    SCROLL = "scroll"
    DRAG_START = "drag_start"
    DRAG = "drag"
    DRAG_END = "drag_end"
    RESIZE = "resize"
    CLOSE = "close"


class Alignment(Enum):
    """Content alignment"""
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"


class Direction(Enum):
    """Layout direction"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


# =============================================================================
# GEOMETRY
# =============================================================================

@dataclass
class Point:
    """2D point"""
    x: int = 0
    y: int = 0

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)


@dataclass
class Size:
    """2D size"""
    width: int = 0
    height: int = 0


@dataclass
class Rect:
    """Rectangle"""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @property
    def position(self) -> Point:
        return Point(self.x, self.y)

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    def contains(self, point: Point) -> bool:
        return (self.x <= point.x < self.right and
                self.y <= point.y < self.bottom)

    def intersects(self, other: "Rect") -> bool:
        return not (self.right <= other.x or other.right <= self.x or
                   self.bottom <= other.y or other.bottom <= self.y)


@dataclass
class Padding:
    """Padding/margin"""
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    @classmethod
    def all(cls, value: int) -> "Padding":
        return cls(value, value, value, value)

    @classmethod
    def symmetric(cls, horizontal: int = 0, vertical: int = 0) -> "Padding":
        return cls(vertical, horizontal, vertical, horizontal)


# =============================================================================
# COLORS & STYLING
# =============================================================================

@dataclass
class Color:
    """RGBA Color"""
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Create color from hex string"""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
            return cls(r, g, b, 255)
        elif len(hex_str) == 8:
            r, g, b, a = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), int(hex_str[6:8], 16)
            return cls(r, g, b, a)
        return cls()

    def to_hex(self) -> str:
        """Convert to hex string"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}{self.a:02x}"

    def with_alpha(self, alpha: int) -> "Color":
        """Return color with modified alpha"""
        return Color(self.r, self.g, self.b, alpha)


# Pre-defined colors
class Colors:
    """Standard colors"""
    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    YELLOW = Color(255, 255, 0)
    CYAN = Color(0, 255, 255)
    MAGENTA = Color(255, 0, 255)
    TRANSPARENT = Color(0, 0, 0, 0)

    # Theme colors
    PRIMARY = Color.from_hex("#6366f1")
    SECONDARY = Color.from_hex("#8b5cf6")
    SUCCESS = Color.from_hex("#22c55e")
    WARNING = Color.from_hex("#f59e0b")
    ERROR = Color.from_hex("#ef4444")
    INFO = Color.from_hex("#3b82f6")

    # Neutrals
    GRAY_50 = Color.from_hex("#f9fafb")
    GRAY_100 = Color.from_hex("#f3f4f6")
    GRAY_200 = Color.from_hex("#e5e7eb")
    GRAY_300 = Color.from_hex("#d1d5db")
    GRAY_400 = Color.from_hex("#9ca3af")
    GRAY_500 = Color.from_hex("#6b7280")
    GRAY_600 = Color.from_hex("#4b5563")
    GRAY_700 = Color.from_hex("#374151")
    GRAY_800 = Color.from_hex("#1f2937")
    GRAY_900 = Color.from_hex("#111827")


@dataclass
class Border:
    """Border styling"""
    width: int = 0
    color: Color = field(default_factory=lambda: Colors.GRAY_300)
    radius: int = 0


@dataclass
class Shadow:
    """Box shadow"""
    offset_x: int = 0
    offset_y: int = 2
    blur: int = 4
    spread: int = 0
    color: Color = field(default_factory=lambda: Color(0, 0, 0, 50))


@dataclass
class Style:
    """Complete widget style"""
    background: Color = None
    foreground: Color = None
    border: Border = None
    padding: Padding = None
    margin: Padding = None
    shadow: Shadow = None
    font_size: int = 14
    font_weight: str = "normal"  # normal, bold
    font_family: str = "system"
    opacity: float = 1.0
    cursor: str = "default"


# =============================================================================
# EVENT SYSTEM
# =============================================================================

@dataclass
class Event:
    """UI Event"""
    type: EventType
    target: "Widget" = None
    position: Point = None
    key: str = None
    modifiers: List[str] = field(default_factory=list)
    delta: Point = None
    timestamp: datetime = field(default_factory=datetime.now)
    propagate: bool = True

    def stop_propagation(self):
        """Stop event from bubbling"""
        self.propagate = False


EventHandler = Callable[[Event], None]


class EventEmitter:
    """Event emitter mixin"""

    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}

    def on(self, event_type: EventType, handler: EventHandler):
        """Register event handler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        return self

    def off(self, event_type: EventType, handler: EventHandler = None):
        """Remove event handler"""
        if event_type in self._handlers:
            if handler:
                self._handlers[event_type].remove(handler)
            else:
                self._handlers[event_type] = []

    def emit(self, event: Event):
        """Emit event to handlers"""
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                handler(event)
                if not event.propagate:
                    break


# =============================================================================
# BASE WIDGET
# =============================================================================

class Widget(EventEmitter, ABC):
    """Base widget class"""

    _id_counter = 0

    def __init__(self, **kwargs):
        super().__init__()
        Widget._id_counter += 1
        self.id = kwargs.get('id', f"widget_{Widget._id_counter}")
        self.bounds = Rect()
        self.style = kwargs.get('style', Style())
        self.visible = kwargs.get('visible', True)
        self.enabled = kwargs.get('enabled', True)
        self.focusable = kwargs.get('focusable', False)
        self.focused = False
        self.parent: Optional["Widget"] = None
        self.children: List["Widget"] = []
        self._dirty = True

    def add_child(self, child: "Widget"):
        """Add child widget"""
        child.parent = self
        self.children.append(child)
        self.mark_dirty()
        return self

    def remove_child(self, child: "Widget"):
        """Remove child widget"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            self.mark_dirty()

    def find_by_id(self, widget_id: str) -> Optional["Widget"]:
        """Find widget by ID"""
        if self.id == widget_id:
            return self
        for child in self.children:
            found = child.find_by_id(widget_id)
            if found:
                return found
        return None

    def mark_dirty(self):
        """Mark widget as needing redraw"""
        self._dirty = True
        if self.parent:
            self.parent.mark_dirty()

    def hit_test(self, point: Point) -> Optional["Widget"]:
        """Find widget at point"""
        if not self.visible or not self.bounds.contains(point):
            return None

        # Check children in reverse order (top to bottom)
        for child in reversed(self.children):
            hit = child.hit_test(point)
            if hit:
                return hit

        return self

    @abstractmethod
    def render(self, renderer: "Renderer"):
        """Render the widget"""
        pass

    def layout(self, available: Rect):
        """Layout the widget"""
        self.bounds = available

    def to_dict(self) -> Dict[str, Any]:
        """Serialize widget"""
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            "bounds": {
                "x": self.bounds.x,
                "y": self.bounds.y,
                "width": self.bounds.width,
                "height": self.bounds.height,
            },
            "visible": self.visible,
            "children": [c.to_dict() for c in self.children],
        }


# =============================================================================
# RENDERER
# =============================================================================

class Renderer(ABC):
    """Abstract renderer interface"""

    @abstractmethod
    def clear(self, color: Color = None):
        """Clear the canvas"""
        pass

    @abstractmethod
    def draw_rect(self, rect: Rect, color: Color, border: Border = None):
        """Draw rectangle"""
        pass

    @abstractmethod
    def draw_text(self, text: str, position: Point, color: Color, font_size: int = 14):
        """Draw text"""
        pass

    @abstractmethod
    def draw_image(self, path: str, rect: Rect):
        """Draw image"""
        pass

    @abstractmethod
    def draw_line(self, start: Point, end: Point, color: Color, width: int = 1):
        """Draw line"""
        pass

    @abstractmethod
    def clip(self, rect: Rect):
        """Set clipping region"""
        pass

    @abstractmethod
    def reset_clip(self):
        """Reset clipping region"""
        pass


class CanvasRenderer(Renderer):
    """
    Canvas-based renderer.
    Generates drawing commands for the Wayland compositor.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.commands: List[Dict[str, Any]] = []
        self._clip_stack: List[Rect] = []

    def clear(self, color: Color = None):
        color = color or Colors.BLACK
        self.commands.append({
            "type": "clear",
            "color": color.to_hex(),
        })

    def draw_rect(self, rect: Rect, color: Color, border: Border = None):
        cmd = {
            "type": "rect",
            "x": rect.x,
            "y": rect.y,
            "width": rect.width,
            "height": rect.height,
            "color": color.to_hex(),
        }
        if border:
            cmd["border_width"] = border.width
            cmd["border_color"] = border.color.to_hex()
            cmd["border_radius"] = border.radius
        self.commands.append(cmd)

    def draw_text(self, text: str, position: Point, color: Color, font_size: int = 14):
        self.commands.append({
            "type": "text",
            "text": text,
            "x": position.x,
            "y": position.y,
            "color": color.to_hex(),
            "font_size": font_size,
        })

    def draw_image(self, path: str, rect: Rect):
        self.commands.append({
            "type": "image",
            "path": path,
            "x": rect.x,
            "y": rect.y,
            "width": rect.width,
            "height": rect.height,
        })

    def draw_line(self, start: Point, end: Point, color: Color, width: int = 1):
        self.commands.append({
            "type": "line",
            "x1": start.x,
            "y1": start.y,
            "x2": end.x,
            "y2": end.y,
            "color": color.to_hex(),
            "width": width,
        })

    def clip(self, rect: Rect):
        self._clip_stack.append(rect)
        self.commands.append({
            "type": "clip",
            "x": rect.x,
            "y": rect.y,
            "width": rect.width,
            "height": rect.height,
        })

    def reset_clip(self):
        if self._clip_stack:
            self._clip_stack.pop()
        self.commands.append({"type": "reset_clip"})

    def get_commands(self) -> List[Dict[str, Any]]:
        """Get and clear commands"""
        commands = self.commands
        self.commands = []
        return commands

    def to_json(self) -> str:
        """Export commands as JSON for compositor"""
        return json.dumps(self.commands)


# =============================================================================
# WINDOW
# =============================================================================

@dataclass
class WindowConfig:
    """Window configuration"""
    title: str = "0RB_AETHER"
    width: int = 800
    height: int = 600
    x: int = None  # None = center
    y: int = None
    resizable: bool = True
    decorations: bool = True
    transparent: bool = False
    always_on_top: bool = False
    min_width: int = 100
    min_height: int = 100
    max_width: int = None
    max_height: int = None


class Window(Widget):
    """Application window"""

    def __init__(self, config: WindowConfig = None):
        super().__init__()
        self.config = config or WindowConfig()
        self.state = WindowState.NORMAL
        self.bounds = Rect(
            x=self.config.x or 0,
            y=self.config.y or 0,
            width=self.config.width,
            height=self.config.height,
        )
        self.renderer = CanvasRenderer(self.config.width, self.config.height)
        self._content: Widget = None

    @property
    def title(self) -> str:
        return self.config.title

    @title.setter
    def title(self, value: str):
        self.config.title = value

    def set_content(self, widget: Widget):
        """Set window content"""
        self._content = widget
        self.add_child(widget)

    def minimize(self):
        self.state = WindowState.MINIMIZED

    def maximize(self):
        self.state = WindowState.MAXIMIZED

    def restore(self):
        self.state = WindowState.NORMAL

    def fullscreen(self, enable: bool = True):
        self.state = WindowState.FULLSCREEN if enable else WindowState.NORMAL

    def close(self):
        self.emit(Event(EventType.CLOSE, target=self))

    def render(self, renderer: Renderer):
        """Render window and contents"""
        # Background
        bg_color = self.style.background or Colors.GRAY_900
        renderer.draw_rect(self.bounds, bg_color)

        # Render children
        for child in self.children:
            if child.visible:
                child.render(renderer)

    def layout(self, available: Rect = None):
        """Layout window contents"""
        if available:
            self.bounds = available

        # Layout children to fill window
        content_rect = Rect(
            x=0,
            y=0,
            width=self.bounds.width,
            height=self.bounds.height,
        )

        for child in self.children:
            child.layout(content_rect)


# =============================================================================
# APPLICATION
# =============================================================================

class Application:
    """
    Main UI application.

    Manages windows, event loop, and compositor communication.
    """

    BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗   ██╗██╗    ██╗    ██╗ ██████╗ ██████╗ ██╗     ██████╗ ███████╗ ║
║   ██║   ██║██║    ██║    ██║██╔═══██╗██╔══██╗██║     ██╔══██╗██╔════╝ ║
║   ██║   ██║██║    ██║ █╗ ██║██║   ██║██████╔╝██║     ██║  ██║███████╗ ║
║   ██║   ██║██║    ██║███╗██║██║   ██║██╔══██╗██║     ██║  ██║╚════██║ ║
║   ╚██████╔╝██║    ╚███╔███╔╝╚██████╔╝██║  ██║███████╗██████╔╝███████║ ║
║    ╚═════╝ ╚═╝     ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝ ║
║                                                               ║
║              UI Worlds - 0RB_AETHER Interface                 ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
"""

    def __init__(self, name: str = "0RB_AETHER"):
        self.name = name
        self.windows: List[Window] = []
        self.active_window: Window = None
        self.running = False
        self._event_queue: asyncio.Queue = None
        self._focus_widget: Widget = None

    def create_window(self, config: WindowConfig = None) -> Window:
        """Create a new window"""
        window = Window(config)
        self.windows.append(window)

        if not self.active_window:
            self.active_window = window

        return window

    def close_window(self, window: Window):
        """Close a window"""
        if window in self.windows:
            self.windows.remove(window)

        if self.active_window == window:
            self.active_window = self.windows[0] if self.windows else None

        if not self.windows:
            self.quit()

    def focus_widget(self, widget: Widget):
        """Set focused widget"""
        if self._focus_widget:
            self._focus_widget.focused = False
            self._focus_widget.emit(Event(EventType.BLUR, target=self._focus_widget))

        self._focus_widget = widget

        if widget:
            widget.focused = True
            widget.emit(Event(EventType.FOCUS, target=widget))

    def handle_event(self, event_data: Dict[str, Any]):
        """Handle incoming event from compositor"""
        event_type = EventType(event_data.get("type", "click"))
        position = Point(
            event_data.get("x", 0),
            event_data.get("y", 0),
        )

        # Find target widget
        target = None
        if self.active_window:
            target = self.active_window.hit_test(position)

        event = Event(
            type=event_type,
            target=target,
            position=position,
            key=event_data.get("key"),
            modifiers=event_data.get("modifiers", []),
        )

        # Handle focus on click
        if event_type == EventType.CLICK and target and target.focusable:
            self.focus_widget(target)

        # Emit to target
        if target:
            target.emit(event)

    def render(self):
        """Render all windows"""
        for window in self.windows:
            if window.visible:
                window.layout()
                window.render(window.renderer)

    async def run(self):
        """Run the application event loop"""
        self.running = True
        self._event_queue = asyncio.Queue()

        print(self.BANNER)
        print(f"Application '{self.name}' starting...")

        while self.running:
            # Process events
            try:
                event_data = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=0.016  # ~60 FPS
                )
                self.handle_event(event_data)
            except asyncio.TimeoutError:
                pass

            # Render
            self.render()

            # Small sleep to prevent CPU spinning
            await asyncio.sleep(0.001)

    def quit(self):
        """Quit the application"""
        self.running = False

    def post_event(self, event_data: Dict[str, Any]):
        """Post event to queue"""
        if self._event_queue:
            self._event_queue.put_nowait(event_data)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core
    "Application",
    "Window",
    "WindowConfig",
    "WindowState",
    "Widget",
    "Renderer",
    "CanvasRenderer",

    # Geometry
    "Point",
    "Size",
    "Rect",
    "Padding",

    # Styling
    "Color",
    "Colors",
    "Border",
    "Shadow",
    "Style",

    # Events
    "Event",
    "EventType",
    "EventEmitter",
    "EventHandler",

    # Layout
    "Alignment",
    "Direction",
]
