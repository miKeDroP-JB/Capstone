//! Container System
//!
//! Manages the interactive workspace containers (WORK, PLAY, CREATE, etc.)

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ContainerType {
    Work,
    Play,
    Home,
    Family,
    Create,
    Health,
    Spiritual,
    Undefined,
}

impl ContainerType {
    pub fn name(&self) -> &str {
        match self {
            Self::Work => "WORK",
            Self::Play => "PLAY",
            Self::Home => "HOME",
            Self::Family => "FAMILY",
            Self::Create => "CREATE",
            Self::Health => "HEALTH",
            Self::Spiritual => "SPIRITUAL",
            Self::Undefined => "UNDEFINED",
        }
    }

    pub fn color(&self) -> [f32; 4] {
        match self {
            Self::Work => [0.7, 0.7, 0.8, 1.0],      // Platinum
            Self::Play => [1.0, 0.84, 0.0, 1.0],     // Gold
            Self::Home => [0.72, 0.45, 0.2, 1.0],    // Copper
            Self::Family => [0.9, 0.6, 0.4, 1.0],    // Warm bronze
            Self::Create => [0.85, 0.85, 0.9, 1.0],  // Chrome
            Self::Health => [0.4, 0.8, 0.4, 1.0],    // Green metallic
            Self::Spiritual => [0.6, 0.4, 0.8, 1.0], // Purple metallic
            Self::Undefined => [0.5, 0.5, 0.5, 1.0], // Gray
        }
    }

    pub fn all() -> Vec<Self> {
        vec![
            Self::Work,
            Self::Play,
            Self::Home,
            Self::Family,
            Self::Create,
            Self::Health,
            Self::Spiritual,
            Self::Undefined,
        ]
    }
}

#[derive(Debug, Clone)]
pub struct Container {
    pub container_type: ContainerType,
    pub position: [f32; 2],      // Screen position (normalized 0-1)
    pub size: [f32; 2],          // Size (normalized)
    pub hover_amount: f32,       // 0-1, for hover effects
    pub active: bool,            // Currently active/focused
    pub smoke_intensity: f32,    // Ambient smoke effect
    pub particle_trails: Vec<ParticleTrail>,
}

#[derive(Debug, Clone)]
pub struct ParticleTrail {
    pub positions: Vec<[f32; 2]>,
    pub life_remaining: f32,
    pub color: [f32; 4],
}

impl Container {
    pub fn new(container_type: ContainerType, position: [f32; 2]) -> Self {
        Self {
            container_type,
            position,
            size: [0.25, 0.25],  // Default size
            hover_amount: 0.0,
            active: false,
            smoke_intensity: 0.3,
            particle_trails: Vec::new(),
        }
    }

    pub fn update(&mut self, delta_time: f32, mouse_pos: [f32; 2]) {
        // Update hover state based on mouse position
        let in_bounds = self.point_in_bounds(mouse_pos);

        if in_bounds {
            self.hover_amount = (self.hover_amount + delta_time * 3.0).min(1.0);
            self.smoke_intensity = 0.6;
        } else {
            self.hover_amount = (self.hover_amount - delta_time * 2.0).max(0.0);
            if !self.active {
                self.smoke_intensity = 0.3;
            }
        }

        // Update particle trails
        self.particle_trails.retain_mut(|trail| {
            trail.life_remaining -= delta_time;
            trail.life_remaining > 0.0
        });
    }

    pub fn point_in_bounds(&self, point: [f32; 2]) -> bool {
        let [x, y] = point;
        let [px, py] = self.position;
        let [w, h] = self.size;

        x >= px && x <= px + w && y >= py && y <= py + h
    }

    pub fn on_click(&mut self, mouse_pos: [f32; 2]) -> bool {
        if self.point_in_bounds(mouse_pos) {
            self.active = true;
            self.smoke_intensity = 1.0;

            // Create particle trail on click
            self.add_particle_trail(mouse_pos);

            true
        } else {
            false
        }
    }

    fn add_particle_trail(&mut self, start_pos: [f32; 2]) {
        let color = self.container_type.color();

        let trail = ParticleTrail {
            positions: vec![start_pos],
            life_remaining: 2.0,  // 2 second trail
            color,
        };

        self.particle_trails.push(trail);
    }

    /// Get visual properties for rendering
    pub fn get_visual_state(&self) -> ContainerVisuals {
        let base_color = self.container_type.color();

        // Enhance color based on hover/active state
        let intensity_multiplier = 1.0 + self.hover_amount * 0.3 + if self.active { 0.5 } else { 0.0 };

        let enhanced_color = [
            (base_color[0] * intensity_multiplier).min(1.0),
            (base_color[1] * intensity_multiplier).min(1.0),
            (base_color[2] * intensity_multiplier).min(1.0),
            base_color[3],
        ];

        ContainerVisuals {
            position: self.position,
            size: self.size,
            color: enhanced_color,
            smoke_intensity: self.smoke_intensity,
            glow_amount: self.hover_amount,
            edge_brightness: if self.active { 1.0 } else { self.hover_amount * 0.5 },
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct ContainerVisuals {
    pub position: [f32; 2],
    pub size: [f32; 2],
    pub color: [f32; 4],
    pub smoke_intensity: f32,
    pub glow_amount: f32,
    pub edge_brightness: f32,
}

pub struct ContainerGrid {
    pub containers: HashMap<ContainerType, Container>,
    pub active_container: Option<ContainerType>,
    pub mouse_position: [f32; 2],
}

impl ContainerGrid {
    pub fn new() -> Self {
        let mut containers = HashMap::new();

        // Arrange containers in a grid (3x3 with center empty for 0RB)
        let positions = [
            [0.1, 0.1],   // WORK (top-left)
            [0.4, 0.1],   // PLAY (top-center)
            [0.7, 0.1],   // HOME (top-right)
            [0.1, 0.4],   // FAMILY (mid-left)
            [0.7, 0.4],   // CREATE (mid-right)
            [0.1, 0.7],   // HEALTH (bottom-left)
            [0.4, 0.7],   // SPIRITUAL (bottom-center)
            [0.7, 0.7],   // UNDEFINED (bottom-right)
        ];

        for (i, container_type) in ContainerType::all().iter().enumerate() {
            if i < positions.len() {
                containers.insert(
                    container_type.clone(),
                    Container::new(container_type.clone(), positions[i])
                );
            }
        }

        Self {
            containers,
            active_container: None,
            mouse_position: [0.0, 0.0],
        }
    }

    pub fn update(&mut self, delta_time: f32, mouse_pos: [f32; 2]) {
        self.mouse_position = mouse_pos;

        for container in self.containers.values_mut() {
            container.update(delta_time, mouse_pos);
        }
    }

    pub fn handle_click(&mut self, mouse_pos: [f32; 2]) -> Option<ContainerType> {
        // Deactivate all first
        for container in self.containers.values_mut() {
            container.active = false;
        }

        // Check which container was clicked
        for (container_type, container) in &mut self.containers {
            if container.on_click(mouse_pos) {
                self.active_container = Some(container_type.clone());
                return Some(container_type.clone());
            }
        }

        self.active_container = None;
        None
    }

    pub fn get_container(&self, container_type: &ContainerType) -> Option<&Container> {
        self.containers.get(container_type)
    }

    pub fn get_container_mut(&mut self, container_type: &ContainerType) -> Option<&mut Container> {
        self.containers.get_mut(container_type)
    }

    /// Get all containers sorted by render order (back to front)
    pub fn get_render_order(&self) -> Vec<&Container> {
        let mut containers: Vec<&Container> = self.containers.values().collect();

        // Sort by z-order (active on top, then by hover amount)
        containers.sort_by(|a, b| {
            if a.active != b.active {
                a.active.cmp(&b.active)
            } else {
                a.hover_amount.partial_cmp(&b.hover_amount).unwrap()
            }
        });

        containers
    }
}

impl Default for ContainerGrid {
    fn default() -> Self {
        Self::new()
    }
}

/// CREATE Container - Special case with enhanced capabilities
pub struct CreateContainer {
    pub base: Container,
    pub layers: Vec<CanvasLayer>,
    pub active_tool: Tool,
    pub ide_open: bool,
    pub terminal_open: bool,
}

#[derive(Debug, Clone)]
pub struct CanvasLayer {
    pub name: String,
    pub visible: bool,
    pub opacity: f32,
    pub blend_mode: BlendMode,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BlendMode {
    Normal,
    Multiply,
    Screen,
    Overlay,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Tool {
    Select,
    Brush,
    Eraser,
    Text,
    Shape,
    Code,
    Terminal,
}

impl CreateContainer {
    pub fn new(position: [f32; 2]) -> Self {
        Self {
            base: Container::new(ContainerType::Create, position),
            layers: vec![
                CanvasLayer {
                    name: "Background".to_string(),
                    visible: true,
                    opacity: 1.0,
                    blend_mode: BlendMode::Normal,
                }
            ],
            active_tool: Tool::Select,
            ide_open: false,
            terminal_open: false,
        }
    }

    pub fn add_layer(&mut self, name: String) {
        self.layers.push(CanvasLayer {
            name,
            visible: true,
            opacity: 1.0,
            blend_mode: BlendMode::Normal,
        });
    }

    pub fn toggle_ide(&mut self) {
        self.ide_open = !self.ide_open;
    }

    pub fn toggle_terminal(&mut self) {
        self.terminal_open = !self.terminal_open;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_container_creation() {
        let container = Container::new(ContainerType::Work, [0.1, 0.1]);
        assert_eq!(container.container_type, ContainerType::Work);
        assert_eq!(container.position, [0.1, 0.1]);
    }

    #[test]
    fn test_point_in_bounds() {
        let container = Container::new(ContainerType::Work, [0.0, 0.0]);
        assert!(container.point_in_bounds([0.1, 0.1]));
        assert!(!container.point_in_bounds([0.5, 0.5]));
    }

    #[test]
    fn test_container_grid() {
        let grid = ContainerGrid::new();
        assert_eq!(grid.containers.len(), 8);
        assert!(grid.get_container(&ContainerType::Work).is_some());
    }

    #[test]
    fn test_create_container_layers() {
        let mut create = CreateContainer::new([0.5, 0.5]);
        assert_eq!(create.layers.len(), 1);

        create.add_layer("Layer 1".to_string());
        assert_eq!(create.layers.len(), 2);
    }
}
