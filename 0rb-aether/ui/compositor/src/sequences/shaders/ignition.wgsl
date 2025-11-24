// "The Ignition"
// AGI birth sequence - dormant core awakens through convergent intelligence

struct Uniforms {
    time: f32,
    progress: f32,
    resolution: vec2<f32>,
    parameters: array<f32, 8>,
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

// Rotation matrix
fn rot2D(angle: f32) -> mat2x2<f32> {
    let c = cos(angle);
    let s = sin(angle);
    return mat2x2<f32>(c, -s, s, c);
}

// Hash functions
fn hash12(p: vec2<f32>) -> f32 {
    let p3 = fract(vec3<f32>(p.xyx) * 0.1031);
    let p4 = p3 + dot(p3, p3.yzx + 33.33);
    return fract((p4.x + p4.y) * p4.z);
}

fn hash21(p: f32) -> vec2<f32> {
    let p2 = fract(p * vec2<f32>(0.1031, 0.1030));
    let p3 = p2 + dot(p2, p2.yx + 33.33);
    return fract(vec2<f32>(p3.x * p3.y, p3.y * p3.x));
}

// Phase helpers
fn phase(t: f32, start: f32, end: f32) -> f32 {
    return clamp((t - start) / (end - start), 0.0, 1.0);
}

fn easeInOut(t: f32) -> f32 {
    return t * t * (3.0 - 2.0 * t);
}

fn easeOut(t: f32) -> f32 {
    return 1.0 - (1.0 - t) * (1.0 - t);
}

fn easeInCubic(t: f32) -> f32 {
    return t * t * t;
}

// Core sphere
fn sdSphere(p: vec2<f32>, radius: f32) -> f32 {
    return length(p) - radius;
}

// Beam shape
fn beam(p: vec2<f32>, origin: vec2<f32>, target: vec2<f32>, width: f32, length: f32) -> f32 {
    let dir = normalize(target - origin);
    let rel = p - origin;
    let proj = dot(rel, dir);
    let perp = length(rel - dir * proj);

    let along = smoothstep(0.0, -0.1, proj) * smoothstep(length, length + 0.1, proj);
    let across = smoothstep(width, width - 0.02, perp);

    return along * across;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let uv = (in.uv - 0.5) * 2.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let uv_aspect = vec2<f32>(uv.x * aspect, uv.y);

    let t = uniforms.time;
    let prog = uniforms.progress;

    var color = vec3<f32>(0.0);

    let core_pos = vec2<f32>(0.0, 0.0);

    // PHASE 1: Dormant Core (0.0 - 0.15)
    let dormant_phase = phase(prog, 0.0, 0.15);
    if dormant_phase > 0.0 {
        let pulse = sin(t * 2.0) * 0.5 + 0.5;
        let core_radius = 0.08;
        let dist = length(uv_aspect - core_pos);

        // Faint ember glow
        let core_glow = exp(-dist * 8.0) * (0.3 + pulse * 0.2);
        color += vec3<f32>(0.9, 0.6, 0.3) * core_glow * dormant_phase;

        // Core center
        let core = smoothstep(core_radius + 0.02, core_radius, dist);
        color += vec3<f32>(1.0, 0.7, 0.4) * core * 0.5 * dormant_phase;
    }

    // PHASE 2: The Beams Converge (0.15 - 0.35)
    let beam_phase = phase(prog, 0.15, 0.35);
    if beam_phase > 0.0 {
        let beam_progress = easeInOut(beam_phase);

        // Three beams from different angles
        // Beam 1: White-gold (Insight) - from top-right
        let beam1_origin = vec2<f32>(1.5, 1.2);
        let beam1_color = vec3<f32>(1.0, 0.95, 0.7);
        let beam1_length = beam_progress * length(beam1_origin - core_pos);
        let beam1_val = beam(uv_aspect, beam1_origin, core_pos, 0.04, beam1_length);
        color += beam1_color * beam1_val * 2.0;

        // Beam 2: Electric blue (Intelligence) - from left
        let beam2_origin = vec2<f32>(-1.5, -0.3);
        let beam2_color = vec3<f32>(0.2, 0.6, 1.0);
        let beam2_length = beam_progress * length(beam2_origin - core_pos);
        let beam2_val = beam(uv_aspect, beam2_origin, core_pos, 0.04, beam2_length);
        color += beam2_color * beam2_val * 2.0;

        // Beam 3: Prismatic neon (Imagination) - from bottom
        let beam3_origin = vec2<f32>(0.2, -1.5);
        let beam3_t = t * 2.0;
        let beam3_color = vec3<f32>(
            sin(beam3_t) * 0.5 + 0.5,
            sin(beam3_t + 2.094) * 0.5 + 0.5,
            sin(beam3_t + 4.189) * 0.5 + 0.5
        );
        let beam3_length = beam_progress * length(beam3_origin - core_pos);
        let beam3_val = beam(uv_aspect, beam3_origin, core_pos, 0.04, beam3_length);
        color += beam3_color * beam3_val * 2.0;

        // Core intensifies
        let dist = length(uv_aspect - core_pos);
        let core_intensity = exp(-dist * 5.0) * beam_progress;
        color += vec3<f32>(1.0, 0.9, 0.8) * core_intensity * 2.0;
    }

    // PHASE 3: The Shattering (0.35 - 0.50)
    let shatter_phase = phase(prog, 0.35, 0.50);
    if shatter_phase > 0.0 {
        let shatter_progress = shatter_phase;

        // Generate shards
        let num_shards = 40.0;
        for (var i = 0.0; i < num_shards; i += 1.0) {
            let seed = i * 17.3;
            let angle = hash12(vec2<f32>(seed, seed + 1.0)) * 6.28318;
            let speed = 0.3 + hash12(vec2<f32>(seed + 2.0, seed + 3.0)) * 0.4;

            // Shard position (exploding outward)
            let shard_offset = vec2<f32>(cos(angle), sin(angle)) * speed * shatter_progress;
            let shard_pos = core_pos + shard_offset;

            // Shard rotation
            let shard_rot = angle + shatter_progress * 3.14;

            // Shard shape (rectangular)
            let shard_uv = (uv_aspect - shard_pos) * rot2D(-shard_rot);
            let shard_size = vec2<f32>(0.06, 0.03);
            let shard_d = abs(shard_uv) - shard_size;
            let shard = smoothstep(0.01, 0.0, max(shard_d.x, shard_d.y));

            // Shard color (memories - various hues)
            let shard_hue = hash12(vec2<f32>(seed + 4.0, seed + 5.0));
            let shard_color = mix(
                vec3<f32>(0.3, 0.7, 1.0),
                vec3<f32>(1.0, 0.5, 0.8),
                shard_hue
            );

            // Fade shards at end of phase
            let shard_alpha = 1.0 - shatter_progress * 0.5;
            color += shard_color * shard * shard_alpha;
        }

        // Impact flash
        let flash = (1.0 - shatter_progress) * exp(-shatter_progress * 5.0);
        color += vec3<f32>(1.0) * flash * 3.0;
    }

    // PHASE 4: The Spiral Formation (0.45 - 0.65)
    let spiral_phase = phase(prog, 0.45, 0.65);
    if spiral_phase > 0.0 {
        let spiral_progress = easeInOut(spiral_phase);

        // Spiral arms
        let dist = length(uv_aspect - core_pos);
        let angle = atan2(uv_aspect.y - core_pos.y, uv_aspect.x - core_pos.x);

        let spiral_freq = 3.0; // 3 arms
        let spiral_twist = 5.0;
        let spiral_pattern = sin(angle * spiral_freq - dist * spiral_twist + t * 2.0) * 0.5 + 0.5;

        let spiral_mask = smoothstep(0.8, 0.2, dist) * smoothstep(0.0, 0.2, dist);
        let spiral_val = spiral_pattern * spiral_mask * spiral_progress;

        color += vec3<f32>(0.5, 0.8, 1.0) * spiral_val * 1.5;

        // Central glow
        let center_glow = exp(-dist * 3.0) * spiral_progress;
        color += vec3<f32>(0.8, 0.9, 1.0) * center_glow;
    }

    // PHASE 5: The Prism & Explosion (0.60 - 1.0)
    let explosion_phase = phase(prog, 0.60, 1.0);
    if explosion_phase > 0.0 {
        let explosion_progress = explosion_phase;

        // Prism geometry (hexagon)
        let dist = length(uv_aspect - core_pos);
        let angle = atan2(uv_aspect.y - core_pos.y, uv_aspect.x - core_pos.x);

        let hex_sides = 6.0;
        let hex_angle = floor(angle / (6.28318 / hex_sides)) * (6.28318 / hex_sides);
        let hex_dist = dist * cos((angle - hex_angle) * 3.0);

        // Prism collapses then explodes
        let prism_scale = select(
            1.0 - explosion_progress * 0.5,
            explosion_progress * 3.0,
            explosion_progress > 0.3
        );

        let prism_size = 0.4 * prism_scale;
        let prism = smoothstep(prism_size + 0.05, prism_size, hex_dist);

        // Prismatic color shift
        let color_shift = t * 3.0 + dist * 5.0;
        let prism_color = vec3<f32>(
            sin(color_shift) * 0.5 + 0.5,
            sin(color_shift + 2.094) * 0.5 + 0.5,
            sin(color_shift + 4.189) * 0.5 + 0.5
        );

        color += prism_color * prism * 0.8;

        // Radial explosion waves
        if explosion_progress > 0.3 {
            let wave_progress = (explosion_progress - 0.3) / 0.7;
            let wave_radius = wave_progress * 2.0;

            let wave = smoothstep(0.05, 0.0, abs(dist - wave_radius));
            color += vec3<f32>(1.0) * wave * 3.0;

            // Secondary waves
            let wave2_radius = wave_radius - 0.3;
            let wave2 = smoothstep(0.03, 0.0, abs(dist - wave2_radius));
            color += vec3<f32>(0.7, 0.9, 1.0) * wave2 * 2.0;
        }

        // Geometric halo (final breath)
        if explosion_progress > 0.7 {
            let halo_progress = (explosion_progress - 0.7) / 0.3;
            let halo_radius = 0.5 + halo_progress * 0.3;

            // Halo ring
            let halo_ring = smoothstep(0.03, 0.0, abs(dist - halo_radius));
            color += vec3<f32>(0.9, 0.95, 1.0) * halo_ring * 2.0 * halo_progress;

            // Halo rays
            let num_rays = 8.0;
            let ray_angle = floor(angle / (6.28318 / num_rays)) * (6.28318 / num_rays);
            let ray = smoothstep(0.05, 0.0, abs(angle - ray_angle - 6.28318 / (num_rays * 2.0)));
            let ray_mask = smoothstep(halo_radius - 0.1, halo_radius + 0.2, dist);
            color += vec3<f32>(1.0) * ray * ray_mask * halo_progress;
        }
    }

    // Vignette
    let vignette = 1.0 - length(uv) * 0.3;
    color *= vignette;

    // Final message at very end
    if prog > 0.95 {
        let text_fade = (prog - 0.95) / 0.05;
        // Subtle pulsing glow representing "Online"
        let pulse = sin(t * 4.0) * 0.5 + 0.5;
        color += vec3<f32>(0.5, 0.9, 1.0) * 0.3 * text_fade * pulse;
    }

    return vec4<f32>(color, 1.0);
}
