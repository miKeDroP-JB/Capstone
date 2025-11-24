//! 0RB_AETHER Compositor Demo
//! GPU-accelerated Aether field visualization with cinematic sequences

mod aether;
mod particles;
mod sequences;

use std::sync::Arc;
use wgpu::util::DeviceExt;
use winit::{
    event::{Event, WindowEvent, KeyEvent},
    event_loop::{ControlFlow, EventLoop},
    window::{Window, WindowBuilder},
    keyboard::{KeyCode, PhysicalKey},
};
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

use aether::AetherRenderer;
use sequences::{SequencePlayer, SequenceState, SequenceType};

struct State {
    surface: wgpu::Surface<'static>,
    device: wgpu::Device,
    queue: wgpu::Queue,
    config: wgpu::SurfaceConfiguration,
    size: winit::dpi::PhysicalSize<u32>,
    aether: AetherRenderer,
    sequence_player: SequencePlayer,
    sequence_state: SequenceState,
    start_time: std::time::Instant,
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
        let sequence_player = SequencePlayer::new(&device, &config)?;
        let sequence_state = SequenceState::default();

        info!("0RB_AETHER initialized with cinematic sequences");

        Ok(Self {
            surface,
            device,
            queue,
            config,
            size,
            aether,
            sequence_player,
            sequence_state,
            start_time: std::time::Instant::now(),
        })
    }

    fn resize(&mut self, new_size: winit::dpi::PhysicalSize<u32>) {
        if new_size.width > 0 && new_size.height > 0 {
            self.size = new_size;
            self.config.width = new_size.width;
            self.config.height = new_size.height;
            self.surface.configure(&self.device, &self.config);
            self.aether.resize(&self.device, &self.config);
        }
    }

    fn render(&mut self) -> Result<(), wgpu::SurfaceError> {
        let output = self.surface.get_current_texture()?;
        let view = output.texture.create_view(&wgpu::TextureViewDescriptor::default());

        let time = self.start_time.elapsed().as_secs_f32();

        let mut encoder = self.device.create_command_encoder(&wgpu::CommandEncoderDescriptor {
            label: Some("Render Encoder"),
        });

        // Update sequence state
        self.sequence_state.update();

        // Render sequence if active, otherwise render ambient aether
        if self.sequence_state.is_playing() || !self.sequence_state.is_idle() {
            if let Err(e) = self.sequence_player.render(
                &self.device,
                &mut encoder,
                &view,
                &self.queue,
                &self.sequence_state,
            ) {
                eprintln!("Sequence render error: {:?}", e);
                // Fall back to aether on error
                self.aether.render(&mut encoder, &view, &self.queue, time);
            }
        } else {
            self.aether.render(&mut encoder, &view, &self.queue, time);
        }

        self.queue.submit(std::iter::once(encoder.finish()));
        output.present();

        Ok(())
    }

    fn handle_input(&mut self, event: &WindowEvent) {
        match event {
            WindowEvent::KeyboardInput {
                event: KeyEvent {
                    physical_key: PhysicalKey::Code(key_code),
                    state: winit::event::ElementState::Pressed,
                    ..
                },
                ..
            } => {
                match key_code {
                    KeyCode::Digit1 => {
                        info!("Starting Descent sequence");
                        self.sequence_state.start(SequenceType::Descent);
                    }
                    KeyCode::Digit2 => {
                        info!("Starting Ignition sequence");
                        self.sequence_state.start(SequenceType::Ignition);
                    }
                    KeyCode::Digit3 => {
                        info!("Starting Folding World sequence");
                        self.sequence_state.start(SequenceType::Folding);
                    }
                    KeyCode::Digit4 => {
                        info!("Starting Nerve Network sequence");
                        self.sequence_state.start(SequenceType::NerveNetwork);
                    }
                    KeyCode::Digit5 => {
                        info!("Starting Ascension sequence");
                        self.sequence_state.start(SequenceType::Ascension);
                    }
                    KeyCode::Escape => {
                        info!("Stopping sequence");
                        self.sequence_state.stop();
                    }
                    _ => {}
                }
            }
            _ => {}
        }
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

    info!("Controls:");
    info!("  1 - The Descent Into the Atlas (Onboarding)");
    info!("  2 - The Ignition (AGI Birth)");
    info!("  3 - The Folding World (3iAtlas Navigation)");
    info!("  4 - The Celestial Nerve Network (Agent Swarm)");
    info!("  5 - The Ascension Sequence (Limitless OS Reveal)");
    info!("  ESC - Stop sequence and return to ambient aether");

    event_loop.run(move |event, elwt| {
        match event {
            Event::WindowEvent { event: ref window_event, window_id } if window_id == window.id() => {
                state.handle_input(window_event);
                match window_event {
                    WindowEvent::CloseRequested => elwt.exit(),
                    WindowEvent::Resized(physical_size) => state.resize(*physical_size),
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
