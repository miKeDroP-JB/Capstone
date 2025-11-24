//! Sequence Player
//! Renders cinematic sequences using GPU shaders

use wgpu::util::DeviceExt;
use bytemuck::{Pod, Zeroable};
use super::state::{SequenceState, SequenceType};

#[repr(C)]
#[derive(Copy, Clone, Debug, Pod, Zeroable)]
struct SequenceUniforms {
    time: f32,
    progress: f32,
    resolution: [f32; 2],
    parameters: [f32; 8],
}

pub struct SequencePlayer {
    /// Current sequence pipeline
    pipeline: Option<wgpu::RenderPipeline>,

    /// Uniform buffer
    uniform_buffer: wgpu::Buffer,

    /// Bind group
    bind_group: wgpu::BindGroup,

    /// Bind group layout (reusable)
    bind_group_layout: wgpu::BindGroupLayout,

    /// Current sequence type (for detecting changes)
    current_sequence: Option<SequenceType>,

    /// Surface format
    format: wgpu::TextureFormat,
}

impl SequencePlayer {
    pub fn new(device: &wgpu::Device, config: &wgpu::SurfaceConfiguration) -> anyhow::Result<Self> {
        // Create uniform buffer
        let uniform_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Sequence Uniform Buffer"),
            contents: bytemuck::cast_slice(&[SequenceUniforms {
                time: 0.0,
                progress: 0.0,
                resolution: [config.width as f32, config.height as f32],
                parameters: [0.0; 8],
            }]),
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
        });

        // Create bind group layout (shared across all sequences)
        let bind_group_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
            label: Some("Sequence Bind Group Layout"),
            entries: &[wgpu::BindGroupLayoutEntry {
                binding: 0,
                visibility: wgpu::ShaderStages::FRAGMENT,
                ty: wgpu::BindingType::Buffer {
                    ty: wgpu::BufferBindingType::Uniform,
                    has_dynamic_offset: false,
                    min_binding_size: None,
                },
                count: None,
            }],
        });

        // Create bind group
        let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("Sequence Bind Group"),
            layout: &bind_group_layout,
            entries: &[wgpu::BindGroupEntry {
                binding: 0,
                resource: uniform_buffer.as_entire_binding(),
            }],
        });

        Ok(Self {
            pipeline: None,
            uniform_buffer,
            bind_group,
            bind_group_layout,
            current_sequence: None,
            format: config.format,
        })
    }

    /// Load a sequence shader and create pipeline
    fn load_sequence(&mut self, device: &wgpu::Device, sequence: SequenceType) -> anyhow::Result<()> {
        let shader_source = match sequence {
            SequenceType::Descent => include_str!("shaders/descent.wgsl"),
            SequenceType::Ignition => include_str!("shaders/ignition.wgsl"),
            SequenceType::Folding => include_str!("shaders/folding.wgsl"),
            SequenceType::NerveNetwork => include_str!("shaders/nerve_network.wgsl"),
            SequenceType::Ascension => include_str!("shaders/ascension.wgsl"),
        };

        let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some(&format!("Sequence Shader: {:?}", sequence)),
            source: wgpu::ShaderSource::Wgsl(shader_source.into()),
        });

        let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("Sequence Pipeline Layout"),
            bind_group_layouts: &[&self.bind_group_layout],
            push_constant_ranges: &[],
        });

        let pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
            label: Some(&format!("Sequence Pipeline: {:?}", sequence)),
            layout: Some(&pipeline_layout),
            vertex: wgpu::VertexState {
                module: &shader,
                entry_point: Some("vs_main"),
                buffers: &[],
                compilation_options: Default::default(),
            },
            fragment: Some(wgpu::FragmentState {
                module: &shader,
                entry_point: Some("fs_main"),
                targets: &[Some(wgpu::ColorTargetState {
                    format: self.format,
                    blend: Some(wgpu::BlendState::ALPHA_BLENDING),
                    write_mask: wgpu::ColorWrites::ALL,
                })],
                compilation_options: Default::default(),
            }),
            primitive: wgpu::PrimitiveState {
                topology: wgpu::PrimitiveTopology::TriangleList,
                ..Default::default()
            },
            depth_stencil: None,
            multisample: wgpu::MultisampleState::default(),
            multiview: None,
            cache: None,
        });

        self.pipeline = Some(pipeline);
        self.current_sequence = Some(sequence);

        Ok(())
    }

    /// Render the current sequence
    pub fn render(
        &mut self,
        device: &wgpu::Device,
        encoder: &mut wgpu::CommandEncoder,
        view: &wgpu::TextureView,
        queue: &wgpu::Queue,
        state: &SequenceState,
    ) -> anyhow::Result<()> {
        // Check if we need to load a new sequence
        if let Some(sequence) = state.sequence {
            if self.current_sequence != Some(sequence) {
                self.load_sequence(device, sequence)?;
            }
        }

        // Only render if we have a pipeline
        if let Some(pipeline) = &self.pipeline {
            // Update uniforms
            queue.write_buffer(
                &self.uniform_buffer,
                0,
                bytemuck::cast_slice(&[SequenceUniforms {
                    time: state.elapsed,
                    progress: state.progress,
                    resolution: [1280.0, 720.0], // TODO: track actual size
                    parameters: state.parameters,
                }]),
            );

            // Render pass
            let mut render_pass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: Some("Sequence Render Pass"),
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view,
                    resolve_target: None,
                    ops: wgpu::Operations {
                        load: wgpu::LoadOp::Clear(wgpu::Color::BLACK),
                        store: wgpu::StoreOp::Store,
                    },
                })],
                depth_stencil_attachment: None,
                timestamp_writes: None,
                occlusion_query_set: None,
            });

            render_pass.set_pipeline(pipeline);
            render_pass.set_bind_group(0, &self.bind_group, &[]);
            render_pass.draw(0..6, 0..1); // Fullscreen quad
        }

        Ok(())
    }

    /// Clear current sequence
    pub fn clear(&mut self) {
        self.pipeline = None;
        self.current_sequence = None;
    }
}
