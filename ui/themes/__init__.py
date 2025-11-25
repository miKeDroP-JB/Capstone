#!/usr/bin/env python3
"""
UI THEMES - Visual Styling Engine
Theme system for 0RB_AETHER UI.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from .. import Color, Colors, Border, Shadow, Style, Padding


# =============================================================================
# THEME DEFINITIONS
# =============================================================================

@dataclass
class ThemeColors:
    """Theme color palette"""
    # Primary
    primary: Color = field(default_factory=lambda: Colors.PRIMARY)
    primary_light: Color = field(default_factory=lambda: Color.from_hex("#818cf8"))
    primary_dark: Color = field(default_factory=lambda: Color.from_hex("#4f46e5"))

    # Secondary
    secondary: Color = field(default_factory=lambda: Colors.SECONDARY)
    secondary_light: Color = field(default_factory=lambda: Color.from_hex("#a78bfa"))
    secondary_dark: Color = field(default_factory=lambda: Color.from_hex("#7c3aed"))

    # Status
    success: Color = field(default_factory=lambda: Colors.SUCCESS)
    warning: Color = field(default_factory=lambda: Colors.WARNING)
    error: Color = field(default_factory=lambda: Colors.ERROR)
    info: Color = field(default_factory=lambda: Colors.INFO)

    # Background
    background: Color = field(default_factory=lambda: Colors.GRAY_900)
    surface: Color = field(default_factory=lambda: Colors.GRAY_800)
    overlay: Color = field(default_factory=lambda: Color(0, 0, 0, 128))

    # Text
    text_primary: Color = field(default_factory=lambda: Colors.WHITE)
    text_secondary: Color = field(default_factory=lambda: Colors.GRAY_400)
    text_disabled: Color = field(default_factory=lambda: Colors.GRAY_600)

    # Border
    border: Color = field(default_factory=lambda: Colors.GRAY_700)
    border_focus: Color = field(default_factory=lambda: Colors.PRIMARY)


@dataclass
class ThemeTypography:
    """Theme typography settings"""
    font_family: str = "Inter, system-ui, sans-serif"
    font_family_mono: str = "JetBrains Mono, monospace"

    # Font sizes
    size_xs: int = 12
    size_sm: int = 14
    size_base: int = 16
    size_lg: int = 18
    size_xl: int = 20
    size_2xl: int = 24
    size_3xl: int = 30
    size_4xl: int = 36

    # Line heights
    line_height_tight: float = 1.25
    line_height_normal: float = 1.5
    line_height_loose: float = 1.75

    # Font weights
    weight_normal: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700


@dataclass
class ThemeSpacing:
    """Theme spacing scale"""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass
class ThemeBorders:
    """Theme border settings"""
    radius_sm: int = 4
    radius_md: int = 8
    radius_lg: int = 12
    radius_xl: int = 16
    radius_full: int = 9999

    width_thin: int = 1
    width_normal: int = 2
    width_thick: int = 4


@dataclass
class ThemeShadows:
    """Theme shadow presets"""
    sm: Shadow = field(default_factory=lambda: Shadow(0, 1, 2, 0, Color(0, 0, 0, 50)))
    md: Shadow = field(default_factory=lambda: Shadow(0, 4, 6, -1, Color(0, 0, 0, 60)))
    lg: Shadow = field(default_factory=lambda: Shadow(0, 10, 15, -3, Color(0, 0, 0, 70)))
    xl: Shadow = field(default_factory=lambda: Shadow(0, 20, 25, -5, Color(0, 0, 0, 80)))


@dataclass
class Theme:
    """Complete theme definition"""
    name: str = "default"
    variant: str = "dark"  # dark, light

    colors: ThemeColors = field(default_factory=ThemeColors)
    typography: ThemeTypography = field(default_factory=ThemeTypography)
    spacing: ThemeSpacing = field(default_factory=ThemeSpacing)
    borders: ThemeBorders = field(default_factory=ThemeBorders)
    shadows: ThemeShadows = field(default_factory=ThemeShadows)

    def get_style(self, component: str, variant: str = None) -> Style:
        """Get style for a component"""
        styles = self._get_component_styles()
        component_styles = styles.get(component, {})
        style = component_styles.get(variant or 'default', Style())
        return style

    def _get_component_styles(self) -> Dict[str, Dict[str, Style]]:
        """Define component styles"""
        return {
            'button': {
                'default': Style(
                    background=self.colors.primary,
                    foreground=self.colors.text_primary,
                    border=Border(width=0, radius=self.borders.radius_md),
                    padding=Padding.symmetric(horizontal=self.spacing.md, vertical=self.spacing.sm),
                ),
                'secondary': Style(
                    background=self.colors.secondary,
                    foreground=self.colors.text_primary,
                    border=Border(width=0, radius=self.borders.radius_md),
                ),
                'outline': Style(
                    background=Colors.TRANSPARENT,
                    foreground=self.colors.primary,
                    border=Border(width=2, color=self.colors.primary, radius=self.borders.radius_md),
                ),
                'ghost': Style(
                    background=Colors.TRANSPARENT,
                    foreground=self.colors.text_primary,
                ),
            },
            'input': {
                'default': Style(
                    background=self.colors.surface,
                    foreground=self.colors.text_primary,
                    border=Border(width=1, color=self.colors.border, radius=self.borders.radius_md),
                    padding=Padding.symmetric(horizontal=self.spacing.sm, vertical=self.spacing.sm),
                ),
            },
            'card': {
                'default': Style(
                    background=self.colors.surface,
                    border=Border(radius=self.borders.radius_lg),
                    shadow=self.shadows.md,
                    padding=Padding.all(self.spacing.md),
                ),
            },
            'text': {
                'default': Style(
                    foreground=self.colors.text_primary,
                    font_size=self.typography.size_base,
                ),
                'secondary': Style(
                    foreground=self.colors.text_secondary,
                    font_size=self.typography.size_sm,
                ),
                'heading': Style(
                    foreground=self.colors.text_primary,
                    font_size=self.typography.size_2xl,
                    font_weight='bold',
                ),
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize theme"""
        return {
            "name": self.name,
            "variant": self.variant,
            "colors": {
                "primary": self.colors.primary.to_hex(),
                "secondary": self.colors.secondary.to_hex(),
                "background": self.colors.background.to_hex(),
                "surface": self.colors.surface.to_hex(),
                "text_primary": self.colors.text_primary.to_hex(),
                "text_secondary": self.colors.text_secondary.to_hex(),
            },
            "typography": {
                "font_family": self.typography.font_family,
                "size_base": self.typography.size_base,
            },
            "spacing": {
                "sm": self.spacing.sm,
                "md": self.spacing.md,
                "lg": self.spacing.lg,
            },
            "borders": {
                "radius_md": self.borders.radius_md,
            },
        }

    def to_json(self, path: str = None) -> str:
        """Export theme as JSON"""
        data = json.dumps(self.to_dict(), indent=2)
        if path:
            Path(path).write_text(data)
        return data


# =============================================================================
# PRE-BUILT THEMES
# =============================================================================

class Themes:
    """Pre-built theme collection"""

    @staticmethod
    def dark() -> Theme:
        """Default dark theme"""
        return Theme(name="Dark", variant="dark")

    @staticmethod
    def light() -> Theme:
        """Light theme"""
        colors = ThemeColors(
            background=Colors.GRAY_50,
            surface=Colors.WHITE,
            text_primary=Colors.GRAY_900,
            text_secondary=Colors.GRAY_600,
            border=Colors.GRAY_200,
        )
        return Theme(name="Light", variant="light", colors=colors)

    @staticmethod
    def midnight() -> Theme:
        """Midnight blue theme"""
        colors = ThemeColors(
            primary=Color.from_hex("#3b82f6"),
            secondary=Color.from_hex("#6366f1"),
            background=Color.from_hex("#0f172a"),
            surface=Color.from_hex("#1e293b"),
            border=Color.from_hex("#334155"),
        )
        return Theme(name="Midnight", variant="dark", colors=colors)

    @staticmethod
    def forest() -> Theme:
        """Forest green theme"""
        colors = ThemeColors(
            primary=Color.from_hex("#22c55e"),
            secondary=Color.from_hex("#10b981"),
            background=Color.from_hex("#052e16"),
            surface=Color.from_hex("#14532d"),
            border=Color.from_hex("#166534"),
        )
        return Theme(name="Forest", variant="dark", colors=colors)

    @staticmethod
    def sunset() -> Theme:
        """Warm sunset theme"""
        colors = ThemeColors(
            primary=Color.from_hex("#f97316"),
            secondary=Color.from_hex("#ef4444"),
            background=Color.from_hex("#1c1917"),
            surface=Color.from_hex("#292524"),
            border=Color.from_hex("#44403c"),
        )
        return Theme(name="Sunset", variant="dark", colors=colors)

    @staticmethod
    def cyberpunk() -> Theme:
        """Cyberpunk neon theme"""
        colors = ThemeColors(
            primary=Color.from_hex("#f0f"),
            primary_light=Color.from_hex("#f5f"),
            primary_dark=Color.from_hex("#a0a"),
            secondary=Color.from_hex("#0ff"),
            background=Color.from_hex("#0a0a0a"),
            surface=Color.from_hex("#1a1a1a"),
            border=Color.from_hex("#333"),
        )
        return Theme(name="Cyberpunk", variant="dark", colors=colors)

    @staticmethod
    def orb_aether() -> Theme:
        """Official 0RB_AETHER theme"""
        colors = ThemeColors(
            primary=Color.from_hex("#6366f1"),
            primary_light=Color.from_hex("#818cf8"),
            primary_dark=Color.from_hex("#4f46e5"),
            secondary=Color.from_hex("#8b5cf6"),
            success=Color.from_hex("#22c55e"),
            warning=Color.from_hex("#f59e0b"),
            error=Color.from_hex("#ef4444"),
            info=Color.from_hex("#3b82f6"),
            background=Color.from_hex("#0f0f23"),
            surface=Color.from_hex("#1a1a2e"),
            text_primary=Color.from_hex("#e0e0ff"),
            text_secondary=Color.from_hex("#a0a0c0"),
            border=Color.from_hex("#2a2a4e"),
        )
        return Theme(name="0RB_AETHER", variant="dark", colors=colors)


# =============================================================================
# THEME MANAGER
# =============================================================================

class ThemeManager:
    """
    Theme management singleton.

    Handles theme switching, persistence, and customization.
    """

    _instance = None
    _current_theme: Theme = None
    _themes: Dict[str, Theme] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize theme manager"""
        # Register built-in themes
        self.register("dark", Themes.dark())
        self.register("light", Themes.light())
        self.register("midnight", Themes.midnight())
        self.register("forest", Themes.forest())
        self.register("sunset", Themes.sunset())
        self.register("cyberpunk", Themes.cyberpunk())
        self.register("orb_aether", Themes.orb_aether())

        # Set default theme
        self._current_theme = self._themes["orb_aether"]

    def register(self, name: str, theme: Theme):
        """Register a theme"""
        self._themes[name] = theme

    def get(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        return self._themes.get(name)

    def list_themes(self) -> list:
        """List available themes"""
        return list(self._themes.keys())

    @property
    def current(self) -> Theme:
        """Get current theme"""
        return self._current_theme

    def set_theme(self, name: str) -> bool:
        """Set current theme"""
        theme = self._themes.get(name)
        if theme:
            self._current_theme = theme
            return True
        return False

    def create_custom(self, name: str, base: str = "dark", **overrides) -> Theme:
        """Create custom theme based on existing"""
        base_theme = self._themes.get(base, Themes.dark())

        # Create new theme with overrides
        colors = ThemeColors(**{
            **vars(base_theme.colors),
            **overrides.get('colors', {}),
        })

        theme = Theme(
            name=name,
            variant=base_theme.variant,
            colors=colors,
        )

        self.register(name, theme)
        return theme


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme() -> Theme:
    """Get current theme"""
    return theme_manager.current


def set_theme(name: str) -> bool:
    """Set current theme"""
    return theme_manager.set_theme(name)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Theme classes
    "Theme",
    "ThemeColors",
    "ThemeTypography",
    "ThemeSpacing",
    "ThemeBorders",
    "ThemeShadows",

    # Pre-built themes
    "Themes",

    # Manager
    "ThemeManager",
    "theme_manager",
    "get_theme",
    "set_theme",
]
