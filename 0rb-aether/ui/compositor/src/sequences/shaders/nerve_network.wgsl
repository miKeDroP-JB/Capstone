// "The Celestial Nerve Network"
// Agent-swarm control room - living galaxy of interconnected minds

struct Uniforms {
    time: f32,
    progress: f32,
    resolution: vec2<f32>,
    parameters: array<f32, 8>,
    // parameters[0] = number of active agents (0.0 - 1.0, scaled to 1-100)
    // parameters[1] = network activity level (0.0 - 1.0)
    // parameters[2] = learning spike intensity (0.0 - 1.0)
    // parameters[3] = user command state (0.0 = idle, 1.0 = "We Hear You")
    // parameters[4] = agent type distribution (0.0-1.0, affects colors)
}

@group(0) @binding(0) var<uniform> uniforms: Uniforms;

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
}

@vertex
fn vs_main(@builtin(vertex_index) vertex_index: u32) -> VertexOutput {
    var out: VertexOutput;
    let x = f32((vertex_index & 1u) << 1u);
    let y = f32((vertex_index & 2u));
    out.position = vec4<f32>(x * 2.0 - 1.0, 1.0 - y * 2.0, 0.0, 1.0);
    out.uv = vec2<f32>(x, y);
    return out;
}

// Hash functions for consistent randomness
fn hash12(p: vec2<f32>) -> f32 {
    let p3 = fract(vec3<f32>(p.xyx) * vec3<f32>(0.1031, 0.1030, 0.0973));
    let p4 = p3 + dot(p3, p3.yzx + 33.33);
    return fract((p4.x + p4.y) * p4.z);
}

fn hash22(p: vec2<f32>) -> vec2<f32> {
    let p3 = fract(vec3<f32>(p.xyx) * vec3<f32>(0.1031, 0.1030, 0.0973));
    let p4 = p3 + dot(p3, p3.yzx + 33.33);
    return fract((p4.xx + p4.yz) * p4.zy);
}

fn hash13(p: vec3<f32>) -> f32 {
    let p2 = fract(p * 0.1031);
    let p3 = p2 + dot(p2, p2.zyx + 31.32);
    return fract((p3.x + p3.y) * p3.z);
}

// Agent types determine color palette
fn agent_color(agent_id: f32, type_dist: f32) -> vec3<f32> {
    let h = hash12(vec2<f32>(agent_id, agent_id + 7.3));

    if h < 0.25 {
        // Logic agents - sharp blue
        return vec3<f32>(0.3, 0.7, 1.0);
    } else if h < 0.50 {
        // Creative agents - vibrant purple/magenta
        return vec3<f32>(0.9, 0.4, 0.8);
    } else if h < 0.75 {
        // Analytical agents - green/teal
        return vec3<f32>(0.4, 0.9, 0.7);
    } else {
        // Experimental agents - orange/yellow
        return vec3<f32>(1.0, 0.7, 0.3);
    }
}

// Smooth pulse for agent activity
fn pulse(t: f32, freq: f32, phase: f32) -> f32 {
    return sin(t * freq + phase) * 0.5 + 0.5;
}

// Line between two points (connection visualization)
fn connection_line(
    uv: vec2<f32>,
    p1: vec2<f32>,
    p2: vec2<f32>,
    thickness: f32,
    flow: f32
) -> f32 {
    let dir = p2 - p1;
    let len = length(dir);
    let norm_dir = dir / len;

    let to_point = uv - p1;
    let proj = dot(to_point, norm_dir);
    let perp = length(to_point - norm_dir * proj);

    // Along the line
    let along = smoothstep(0.0, 0.02, proj) * smoothstep(len, len - 0.02, proj);

    // Distance from line
    let dist = smoothstep(thickness, 0.0, perp);

    // Flow animation
    let flow_pattern = fract(proj / len * 3.0 - flow);
    let flow_pulse = smoothstep(0.3, 0.5, flow_pattern) * smoothstep(0.7, 0.5, flow_pattern);

    return along * dist * (0.5 + flow_pulse * 0.5);
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let uv = (in.uv - 0.5) * 2.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let uv_aspect = vec2<f32>(uv.x * aspect, uv.y);

    let t = uniforms.time;

    var color = vec3<f32>(0.0);

    // Parameters
    let num_agents_norm = select(uniforms.parameters[0], 0.5, uniforms.parameters[0] == 0.0);
    let num_agents = 10.0 + num_agents_norm * 90.0; // 10 to 100 agents

    let activity_level = select(uniforms.parameters[1], 0.5, uniforms.parameters[1] == 0.0);
    let learning_spike = uniforms.parameters[2];
    let command_state = uniforms.parameters[3];
    let type_dist = uniforms.parameters[4];

    // PHASE 1: Falling strands (intro animation, 0-3 seconds)
    let intro_phase = clamp(t / 3.0, 0.0, 1.0);
    if intro_phase < 1.0 {
        let num_strands = 20.0;
        for (var i = 0.0; i < num_strands; i += 1.0) {
            let strand_id = i;
            let x_pos = (hash12(vec2<f32>(strand_id, 0.0)) - 0.5) * 2.0 * aspect;
            let fall_speed = 0.5 + hash12(vec2<f32>(strand_id, 1.0)) * 0.5;
            let strand_phase = clamp((t - i * 0.15) * fall_speed, 0.0, 1.0);

            if strand_phase > 0.0 && strand_phase < 1.0 {
                let y_pos = 1.0 - strand_phase * 2.5;
                let strand_uv = vec2<f32>(uv_aspect.x - x_pos, uv.y - y_pos);

                // Vertical strand
                let strand = smoothstep(0.01, 0.0, abs(strand_uv.x)) *
                             smoothstep(0.3, 0.0, abs(strand_uv.y));

                let strand_color = vec3<f32>(0.7, 0.9, 1.0);
                color += strand_color * strand * (1.0 - intro_phase);
            }
        }
    }

    // Generate agent positions (consistent across frames)
    var agent_positions: array<vec2<f32>, 100>;
    for (var i = 0; i < 100; i += 1) {
        let agent_id = f32(i);
        let angle = hash12(vec2<f32>(agent_id, 11.0)) * 6.28318;
        let radius = 0.3 + hash12(vec2<f32>(agent_id, 13.0)) * 0.6;

        // Arrange in galaxy-like structure
        let spiral_offset = agent_id * 0.2;
        let spiral_angle = angle + spiral_offset;

        agent_positions[i] = vec2<f32>(
            cos(spiral_angle) * radius * aspect,
            sin(spiral_angle) * radius
        );
    }

    // PHASE 2: Active agent nodes
    for (var i = 0; i < i32(num_agents); i += 1) {
        let agent_id = f32(i);
        var agent_pos = agent_positions[i];

        // Command state: agents orient toward center (user position)
        if command_state > 0.0 {
            let to_center = normalize(-agent_pos) * 0.3;
            agent_pos = mix(agent_pos, agent_pos + to_center, command_state);
        }

        let dist = length(uv_aspect - agent_pos);

        // Agent activity pulse
        let pulse_freq = 2.0 + hash12(vec2<f32>(agent_id, 17.0)) * 3.0;
        let pulse_phase = hash12(vec2<f32>(agent_id, 19.0)) * 6.28318;
        let agent_pulse = pulse(t, pulse_freq, pulse_phase);

        // Agent size based on activity
        let agent_size = 0.015 + agent_pulse * activity_level * 0.01;

        // Agent core
        let agent_core = smoothstep(agent_size + 0.01, agent_size, dist);
        let agent_col = agent_color(agent_id, type_dist);
        color += agent_col * agent_core * 1.5;

        // Agent glow
        let agent_glow = exp(-dist * 15.0) * agent_pulse * activity_level;
        color += agent_col * agent_glow * 0.8;

        // Learning spike effect (shockwave)
        if learning_spike > 0.0 {
            let spike_trigger = hash12(vec2<f32>(agent_id, 23.0));
            if spike_trigger > 0.7 {
                let spike_radius = learning_spike * 0.5;
                let spike_wave = smoothstep(0.03, 0.0, abs(dist - spike_radius));
                color += vec3<f32>(1.0, 1.0, 1.0) * spike_wave * 3.0;

                // Expanding glow
                let spike_glow = exp(-(dist - spike_radius) * 5.0) * learning_spike;
                color += agent_col * spike_glow * 2.0;
            }
        }
    }

    // PHASE 3: Connections between agents (neural pathways)
    let num_connections = i32(num_agents * 0.3); // Each agent connects to ~30% of others
    for (var i = 0; i < num_connections; i += 1) {
        let conn_id = f32(i);
        let agent_a = i32(hash12(vec2<f32>(conn_id, 29.0)) * num_agents);
        let agent_b = i32(hash12(vec2<f32>(conn_id, 31.0)) * num_agents);

        if agent_a != agent_b {
            let pos_a = agent_positions[agent_a];
            let pos_b = agent_positions[agent_b];

            // Data flow speed
            let flow_speed = 1.0 + activity_level * 2.0;
            let flow = t * flow_speed + conn_id * 0.5;

            // Connection line
            let line_thickness = 0.002 + activity_level * 0.003;
            let line = connection_line(uv_aspect, pos_a, pos_b, line_thickness, flow);

            // Silver fire color
            let conn_color = mix(
                vec3<f32>(0.7, 0.8, 0.9),
                vec3<f32>(1.0, 1.0, 1.0),
                activity_level
            );

            color += conn_color * line * 0.5;
        }
    }

    // PHASE 4: "We Hear You" state - unified halo
    if command_state > 0.5 {
        let halo_radius = 0.8;
        let dist_center = length(uv_aspect);

        // Halo ring
        let halo_ring = smoothstep(0.05, 0.0, abs(dist_center - halo_radius));
        let halo_pulse = pulse(t, 2.0, 0.0);
        let halo_color = vec3<f32>(0.9, 0.95, 1.0);

        color += halo_color * halo_ring * command_state * (0.8 + halo_pulse * 0.2);

        // Radial lines connecting to center
        let angle = atan2(uv_aspect.y, uv_aspect.x);
        let num_rays = 16.0;
        let ray_width = 0.1;
        let ray = smoothstep(ray_width, 0.0, abs(fract(angle / 6.28318 * num_rays) - 0.5) * 2.0);
        let ray_mask = smoothstep(0.2, halo_radius, dist_center) * smoothstep(1.2, halo_radius, dist_center);

        color += halo_color * ray * ray_mask * command_state * 0.3;
    }

    // Background: deep space ambience
    let bg_noise = hash12(uv_aspect * 100.0);
    color += vec3<f32>(0.02, 0.03, 0.05) + vec3<f32>(bg_noise) * 0.01;

    // Vignette
    let vignette = 1.0 - length(uv) * 0.5;
    color *= vignette;

    return vec4<f32>(color, 1.0);
}
