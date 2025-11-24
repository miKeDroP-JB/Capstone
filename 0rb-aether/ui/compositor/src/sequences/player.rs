//! Sequence Player - GPU Renderer for Cinematic Sequences
//! Manages shader pipelines and renders sequences to framebuffer

use wgpu::util::DeviceExt;
use bytemuck::{Pod, Zeroable};

use super::state::{SequenceParameters, SequenceStateMachine, SequenceType};

/// Uniforms passed to sequence shaders
#[repr(C)]
#[derive(Copy, Clone, Debug, Pod, Zeroable)]
pub struct SequenceUniforms {
    /// Current time in seconds
    pub time: f32,
    /// Sequence progress (0.0 - 1.0)
    pub progress: f32,
    /// Screen resolution
    pub resolution: [f32; 2],
    /// Interactive parameters (6 floats for various controls)
    pub parameters: [f32; 8],
}

/// GPU renderer for cinematic sequences
pub struct SequencePlayer {
    /// Pipeline for Descent sequence
    descent_pipeline: wgpu::RenderPipeline,
    /// Pipeline for Ignition sequence
    ignition_pipeline: wgpu::RenderPipeline,
    /// Pipeline for Folding World sequence
    folding_pipeline: wgpu::RenderPipeline,
    /// Pipeline for Nerve Network sequence
    nerve_pipeline: wgpu::RenderPipeline,
    /// Pipeline for Ascension sequence
    ascension_pipeline: wgpu::RenderPipeline,
    /// Shared uniform buffer
    uniform_buffer: wgpu::Buffer,
    /// Bind group for uniforms
    bind_group: wgpu::BindGroup,
    /// Current resolution
    resolution: [f32; 2],
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
                parameters: [1.0, 0.0, 0.0, 0.0, 1.0, 0.5, 40.0, 0.5],
            }]),
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
        });

        // Create bind group layout
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

        let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("Sequence Bind Group"),
            layout: &bind_group_layout,
            entries: &[wgpu::BindGroupEntry {
                binding: 0,
                resource: uniform_buffer.as_entire_binding(),
            }],
        });

        let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("Sequence Pipeline Layout"),
            bind_group_layouts: &[&bind_group_layout],
            push_constant_ranges: &[],
        });

        // Create shader modules for each sequence
        let descent_shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("Descent Shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shaders/descent.wgsl").into()),
        });

        let ignition_shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("Ignition Shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shaders/ignition.wgsl").into()),
        });

        let folding_shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("Folding World Shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shaders/folding.wgsl").into()),
        });

        let nerve_shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("Nerve Network Shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shaders/nerve_network.wgsl").into()),
        });

        let ascension_shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("Ascension Shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shaders/ascension.wgsl").into()),
        });

        // Helper to create pipeline
        let create_pipeline = |shader: &wgpu::ShaderModule, label: &str| {
            device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
                label: Some(label),
                layout: Some(&pipeline_layout),
                vertex: wgpu::VertexState {
                    module: shader,
                    entry_point: Some("vs_main"),
                    buffers: &[],
                    compilation_options: Default::default(),
                },
                fragment: Some(wgpu::FragmentState {
                    module: shader,
                    entry_point: Some("fs_main"),
                    targets: &[Some(wgpu::ColorTargetState {
                        format: config.format,
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
            })
        };

        Ok(Self {
            descent_pipeline: create_pipeline(&descent_shader, "Descent Pipeline"),
            ignition_pipeline: create_pipeline(&ignition_shader, "Ignition Pipeline"),
            folding_pipeline: create_pipeline(&folding_shader, "Folding Pipeline"),
            nerve_pipeline: create_pipeline(&nerve_shader, "Nerve Network Pipeline"),
            ascension_pipeline: create_pipeline(&ascension_shader, "Ascension Pipeline"),
            uniform_buffer,
            bind_group,
            resolution: [config.width as f32, config.height as f32],
        })
    }

    /// Update resolution on resize
    pub fn resize(&mut self, config: &wgpu::SurfaceConfiguration) {
        self.resolution = [config.width as f32, config.height as f32];
    }

    /// Render the current sequence
    pub fn render(
        &self,
        encoder: &mut wgpu::CommandEncoder,
        view: &wgpu::TextureView,
        queue: &wgpu::Queue,
        state_machine: &SequenceStateMachine,
        time: f32,
    ) {
        let sequence = match state_machine.current_sequence() {
            Some(seq) => seq,
            None => return, // No sequence to render
        };

        let params = state_machine.parameters();

        // Update uniforms
        queue.write_buffer(
            &self.uniform_buffer,
            0,
            bytemuck::cast_slice(&[SequenceUniforms {
                time,
                progress: state_machine.progress(),
                resolution: self.resolution,
                parameters: [
                    params.zoom,
                    params.fold_intensity,
                    params.focus_x,
                    params.focus_y,
                    params.flow_speed,
                    params.aurora_intensity,
                    params.agent_count as f32,
                    params.activity_level,
                ],
            }]),
        );

        // Select pipeline based on sequence type
        let pipeline = match sequence {
            SequenceType::Descent => &self.descent_pipeline,
            SequenceType::Ignition => &self.ignition_pipeline,
            SequenceType::FoldingWorld => &self.folding_pipeline,
            SequenceType::NerveNetwork => &self.nerve_pipeline,
            SequenceType::Ascension => &self.ascension_pipeline,
        };

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
}
