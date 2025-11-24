//! 0RB_AETHER Compositor Demo
//! GPU-accelerated Aether field visualization with Cinematic Sequences
//!
//! Controls:
//! - 1: The Descent Into the Atlas (onboarding)
//! - 2: The Ignition (AGI birth)
//! - 3: The Folding World (3iAtlas navigation)
//! - 4: Celestial Nerve Network (agent swarm)
//! - 5: The Ascension Sequence (OS reveal)
//! - ESC: Stop sequence, return to ambient aether

mod aether;
mod particles;
mod sequences;

use std::sync::Arc;
use wgpu::util::DeviceExt;
use winit::{
    event::{Event, WindowEvent, KeyEvent},
    event_loop::{ControlFlow, EventLoop},
    keyboard::{KeyCode, PhysicalKey},
    window::{Window, WindowBuilder},
};
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

use aether::AetherRenderer;
use sequences::{SequencePlayer, SequenceStateMachine, SequenceType};

struct State {
    surface: wgpu::Surface<'static>,
    device: wgpu::Device,
    queue: wgpu::Queue,
    config: wgpu::SurfaceConfiguration,
    size: winit::dpi::PhysicalSize<u32>,
    aether: AetherRenderer,
    sequences: SequencePlayer,
    sequence_state: SequenceStateMachine,
    start_time: std::time::Instant,
    last_frame_time: std::time::Instant,
}

impl State {
    async fn new(window: Arc<Window>) -> anyhow::Result<Self> {
        let size = window.inner_size();

        let instance = wgpu::Instance::new(wgpu::InstanceDescriptor {
            backends: wgpu::Backends::all(),
            ..Default::default()
        });

        let surface = instance.create_surface(window.clone())?;

        let adapter = instance
            .request_adapter(&wgpu::RequestAdapterOptions {
                power_preference: wgpu::PowerPreference::HighPerformance,
                compatible_surface: Some(&surface),
                force_fallback_adapter: false,
            })
            .await
            .ok_or_else(|| anyhow::anyhow!("Failed to find adapter"))?;

        let (device, queue) = adapter
            .request_device(
                &wgpu::DeviceDescriptor {
                    required_features: wgpu::Features::empty(),
                    required_limits: wgpu::Limits::default(),
                    label: Some("0RB Device"),
                    memory_hints: Default::default(),
                },
                None,
            )
            .await?;

        let surface_caps = surface.get_capabilities(&adapter);
        let surface_format = surface_caps.formats.iter()
            .find(|f| f.is_srgb())
            .copied()
            .unwrap_or(surface_caps.formats[0]);

        let config = wgpu::SurfaceConfiguration {
            usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
            format: surface_format,
            width: size.width,
            height: size.height,
            present_mode: wgpu::PresentMode::Fifo,
            alpha_mode: surface_caps.alpha_modes[0],
            view_formats: vec![],
            desired_maximum_frame_latency: 2,
        };
        surface.configure(&device, &config);

        let aether = AetherRenderer::new(&device, &config)?;
        let sequences = SequencePlayer::new(&device, &config)?;
        let sequence_state = SequenceStateMachine::new();

        info!("Cinematic sequences initialized");
        info!("Controls: 1-5 to start sequences, ESC to stop");

        Ok(Self {
            surface,
            device,
            queue,
            config,
            size,
            aether,
            sequences,
            sequence_state,
            start_time: std::time::Instant::now(),
            last_frame_time: std::time::Instant::now(),
        })
    }

    fn handle_key(&mut self, key: KeyCode) {
        match key {
            KeyCode::Digit1 => {
                info!("Starting: The Descent Into the Atlas");
                self.sequence_state.play(SequenceType::Descent);
            }
            KeyCode::Digit2 => {
                info!("Starting: The Ignition");
                self.sequence_state.play(SequenceType::Ignition);
            }
            KeyCode::Digit3 => {
                info!("Starting: The Folding World");
                self.sequence_state.play(SequenceType::FoldingWorld);
            }
            KeyCode::Digit4 => {
                info!("Starting: Celestial Nerve Network");
                self.sequence_state.play(SequenceType::NerveNetwork);
            }
            KeyCode::Digit5 => {
                info!("Starting: The Ascension Sequence");
                self.sequence_state.play(SequenceType::Ascension);
            }
            KeyCode::Escape => {
                info!("Stopping sequence, returning to ambient aether");
                self.sequence_state.stop();
            }
            KeyCode::Space => {
                // Toggle pause for current sequence
                if self.sequence_state.is_playing() {
                    self.sequence_state.pause();
                    info!("Sequence paused");
                } else {
                    self.sequence_state.resume();
                    info!("Sequence resumed");
                }
            }
            _ => {}
        }
    }

    fn resize(&mut self, new_size: winit::dpi::PhysicalSize<u32>) {
        if new_size.width > 0 && new_size.height > 0 {
            self.size = new_size;
            self.config.width = new_size.width;
            self.config.height = new_size.height;
            self.surface.configure(&self.device, &self.config);
            self.aether.resize(&self.device, &self.config);
            self.sequences.resize(&self.config);
        }
    }

    fn render(&mut self) -> Result<(), wgpu::SurfaceError> {
        let output = self.surface.get_current_texture()?;
        let view = output.texture.create_view(&wgpu::TextureViewDescriptor::default());

        let time = self.start_time.elapsed().as_secs_f32();

        // Calculate delta time for sequence updates
        let now = std::time::Instant::now();
        let dt = (now - self.last_frame_time).as_secs_f32();
        self.last_frame_time = now;

        // Update sequence state
        let completed = self.sequence_state.update(dt);
        if completed {
            if let Some(seq) = self.sequence_state.current_sequence() {
                info!("Sequence completed: {:?}", seq);
            }
            self.sequence_state.stop();
        }

        let mut encoder = self.device.create_command_encoder(&wgpu::CommandEncoderDescriptor {
            label: Some("Render Encoder"),
        });

        // Render either sequence or ambient aether
        if self.sequence_state.is_playing() || matches!(self.sequence_state.state(), sequences::SequenceState::Paused { .. }) {
            self.sequences.render(&mut encoder, &view, &self.queue, &self.sequence_state, time);
        } else {
            self.aether.render(&mut encoder, &view, &self.queue, time);
        }

        self.queue.submit(std::iter::once(encoder.finish()));
        output.present();

        Ok(())
    }
}

fn main() -> anyhow::Result<()> {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    info!("Starting 0RB_AETHER Compositor Demo");

    let event_loop = EventLoop::new()?;
    let window = Arc::new(WindowBuilder::new()
        .with_title("0RB_AETHER")
        .with_inner_size(winit::dpi::LogicalSize::new(1280, 720))
        .build(&event_loop)?);

    let mut state = pollster::block_on(State::new(window.clone()))?;

    event_loop.run(move |event, elwt| {
        match event {
            Event::WindowEvent { event, window_id } if window_id == window.id() => {
                match event {
                    WindowEvent::CloseRequested => elwt.exit(),
                    WindowEvent::Resized(physical_size) => state.resize(physical_size),
                    WindowEvent::KeyboardInput {
                        event: KeyEvent {
                            physical_key: PhysicalKey::Code(key_code),
                            state: winit::event::ElementState::Pressed,
                            ..
                        },
                        ..
                    } => {
                        state.handle_key(key_code);
                    }
                    WindowEvent::RedrawRequested => {
                        match state.render() {
                            Ok(_) => {}
                            Err(wgpu::SurfaceError::Lost) => state.resize(state.size),
                            Err(wgpu::SurfaceError::OutOfMemory) => elwt.exit(),
                            Err(e) => eprintln!("Render error: {:?}", e),
                        }
                    }
                    _ => {}
                }
            }
            Event::AboutToWait => {
                window.request_redraw();
            }
            _ => {}
        }
    })?;

    Ok(())
}
