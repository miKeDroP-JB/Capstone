// "The Ascension Sequence"
// Limitless OS reveal - ascending through layers of capability

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

// Hash functions
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

// Noise
fn noise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let u = f * f * (3.0 - 2.0 * f);

    return mix(
        mix(hash12(i), hash12(i + vec2<f32>(1.0, 0.0)), u.x),
        mix(hash12(i + vec2<f32>(0.0, 1.0)), hash12(i + vec2<f32>(1.0)), u.x),
        u.y
    );
}

fn fbm(p: vec2<f32>, octaves: i32) -> f32 {
    var value = 0.0;
    var amplitude = 0.5;
    var frequency = 1.0;
    var pos = p;

    for (var i = 0; i < octaves; i += 1) {
        value += amplitude * noise(pos * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }

    return value;
}

// Rotation matrix
fn rot2D(angle: f32) -> mat2x2<f32> {
    let c = cos(angle);
    let s = sin(angle);
    return mat2x2<f32>(c, -s, s, c);
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

// Sacred geometry rune
fn rune(uv: vec2<f32>, time: f32, progress: f32) -> f32 {
    var val = 0.0;

    // Outer circle
    let outer_radius = 0.3;
    let outer_circle = abs(length(uv) - outer_radius);
    val = max(val, smoothstep(0.015, 0.01, outer_circle) * progress);

    // Inner circles
    let num_inner = 6.0;
    for (var i = 0.0; i < num_inner; i += 1.0) {
        let angle = (i / num_inner) * 6.28318 + time * 0.3;
        let pos = vec2<f32>(cos(angle), sin(angle)) * 0.15;
        let inner_circle = abs(length(uv - pos) - 0.08);
        val = max(val, smoothstep(0.012, 0.008, inner_circle) * progress);
    }

    // Center star
    let star_points = 8.0;
    let angle = atan2(uv.y, uv.x);
    let star_angle = floor(angle / (6.28318 / star_points)) * (6.28318 / star_points);
    let star_dist = length(uv);
    let star_ray = smoothstep(0.03, 0.0, abs(angle - star_angle - 6.28318 / (star_points * 2.0)));
    let star_mask = smoothstep(0.1, 0.25, star_dist);
    val = max(val, star_ray * star_mask * progress);

    // Connecting lines
    let line_angle = angle + time * 0.5;
    let line_pattern = abs(fract(line_angle / 6.28318 * 12.0) - 0.5) * 2.0;
    let line = smoothstep(0.95, 1.0, line_pattern);
    let line_mask = smoothstep(0.15, 0.25, star_dist) * smoothstep(0.35, 0.25, star_dist);
    val = max(val, line * line_mask * progress);

    return val;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let uv = (in.uv - 0.5) * 2.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let uv_aspect = vec2<f32>(uv.x * aspect, uv.y);

    let t = uniforms.time;
    let prog = uniforms.progress;

    var color = vec3<f32>(0.0);

    // PHASE 1: White screen (0.0 - 0.08)
    let white_phase = phase(prog, 0.0, 0.08);
    if white_phase > 0.0 {
        let white_fade = 1.0 - easeOut(white_phase);
        color += vec3<f32>(1.0) * white_fade;
    }

    // PHASE 2: Rune draws itself (0.08 - 0.25)
    let rune_phase = phase(prog, 0.08, 0.25);
    if rune_phase > 0.0 {
        let rune_progress = easeInOut(rune_phase);
        let rune_val = rune(uv_aspect, t, rune_progress);

        let rune_color = vec3<f32>(0.6, 0.8, 1.0);
        color += rune_color * rune_val * 2.0;

        // Rune glow
        let dist = length(uv_aspect);
        let rune_glow = exp(-dist * 2.0) * rune_progress * 0.3;
        color += rune_color * rune_glow;
    }

    // PHASE 3: OS city rises from fog (0.20 - 0.60)
    let city_phase = phase(prog, 0.20, 0.60);
    if city_phase > 0.0 {
        let city_progress = easeOut(city_phase);

        // Camera zoom out effect
        let zoom = 1.0 + city_progress * 2.0;
        let city_uv = uv_aspect * zoom;

        // Fog base
        let fog = fbm(city_uv * 2.0 + vec2<f32>(t * 0.2, 0.0), 4);
        let fog_density = (1.0 - city_progress) * 0.8;
        color += vec3<f32>(0.7, 0.8, 0.9) * fog * fog_density;

        // Data towers (vertical structures)
        let num_towers = 12.0;
        for (var i = 0.0; i < num_towers; i += 1.0) {
            let tower_id = i;
            let tower_x = (hash12(vec2<f32>(tower_id, 7.0)) - 0.5) * 3.0;
            let tower_height = 0.4 + hash12(vec2<f32>(tower_id, 11.0)) * 0.6;
            let tower_width = 0.06 + hash12(vec2<f32>(tower_id, 13.0)) * 0.04;

            let tower_uv = city_uv - vec2<f32>(tower_x, -0.5);
            let tower_rise = city_progress * tower_height;

            // Tower body
            let d_x = abs(tower_uv.x) - tower_width;
            let d_y = tower_uv.y;
            let tower = smoothstep(0.02, 0.0, max(d_x, -d_y)) *
                       smoothstep(tower_rise + 0.1, tower_rise, tower_uv.y);

            let tower_color = vec3<f32>(0.4, 0.7, 1.0);
            color += tower_color * tower * 0.6;

            // Tower lights (windows)
            let window_pattern = fract(tower_uv.y * 20.0 + tower_id * 3.7);
            let window = smoothstep(0.6, 0.7, window_pattern) * tower;
            color += vec3<f32>(0.8, 0.9, 1.0) * window * 1.5;
        }

        // Floating plazas (agent collaboration spaces)
        let num_plazas = 8.0;
        for (var i = 0.0; i < num_plazas; i += 1.0) {
            let plaza_id = i + 20.0;
            let plaza_pos = (hash22(vec2<f32>(plaza_id, plaza_id + 3.0)) - 0.5) * 2.5;
            let plaza_size = 0.15 + hash12(vec2<f32>(plaza_id, plaza_id + 5.0)) * 0.1;

            let plaza_uv = city_uv - plaza_pos;
            let plaza = smoothstep(plaza_size + 0.05, plaza_size, length(plaza_uv));

            let plaza_color = vec3<f32>(0.6, 0.8, 0.9);
            color += plaza_color * plaza * city_progress * 0.4;

            // Plaza activity glow
            let pulse = sin(t * 2.0 + plaza_id) * 0.5 + 0.5;
            let plaza_glow = exp(-length(plaza_uv) * 3.0) * pulse;
            color += plaza_color * plaza_glow * city_progress * 0.3;
        }

        // Bridges (luminous connections)
        let num_bridges = 6.0;
        for (var i = 0.0; i < num_bridges; i += 1.0) {
            let bridge_id = i + 40.0;
            let start_x = (hash12(vec2<f32>(bridge_id, 1.0)) - 0.5) * 2.5;
            let end_x = (hash12(vec2<f32>(bridge_id, 2.0)) - 0.5) * 2.5;
            let bridge_y = hash12(vec2<f32>(bridge_id, 3.0)) * 0.6 - 0.2;

            let bridge_start = vec2<f32>(start_x, bridge_y);
            let bridge_end = vec2<f32>(end_x, bridge_y);

            let to_line = city_uv - bridge_start;
            let line_dir = normalize(bridge_end - bridge_start);
            let proj = dot(to_line, line_dir);
            let perp = length(to_line - line_dir * proj);

            let bridge_len = length(bridge_end - bridge_start);
            let along = smoothstep(0.0, 0.02, proj) * smoothstep(bridge_len, bridge_len - 0.02, proj);
            let bridge = smoothstep(0.015, 0.0, perp) * along;

            let bridge_color = vec3<f32>(0.7, 0.9, 1.0);
            color += bridge_color * bridge * city_progress * 0.8;
        }

        // Rivers of computation (flowing data streams)
        let river_flow = fbm(city_uv * 3.0 + vec2<f32>(t * 0.5, 0.0), 3);
        let river_mask = smoothstep(0.45, 0.55, river_flow) * city_progress;
        let river_color = vec3<f32>(0.3, 0.8, 1.0);
        color += river_color * river_mask * 0.4;

        // Thought vortices (swirling idea evolution)
        let num_vortices = 4.0;
        for (var i = 0.0; i < num_vortices; i += 1.0) {
            let vortex_id = i + 60.0;
            let vortex_pos = (hash22(vec2<f32>(vortex_id, vortex_id + 1.0)) - 0.5) * 2.0;
            let vortex_uv = city_uv - vortex_pos;

            let angle = atan2(vortex_uv.y, vortex_uv.x);
            let dist = length(vortex_uv);
            let spiral = sin(angle * 5.0 - dist * 10.0 + t * 2.0) * 0.5 + 0.5;
            let vortex_mask = exp(-dist * 3.0) * smoothstep(0.3, 0.1, dist);

            let vortex_color = vec3<f32>(0.8, 0.5, 1.0);
            color += vortex_color * spiral * vortex_mask * city_progress * 0.5;
        }

        // Sky of swirling intelligence
        let sky_mask = smoothstep(-0.5, 0.5, city_uv.y);
        let sky_flow = fbm(city_uv * 1.5 + vec2<f32>(t * 0.3, t * 0.2), 4);
        let sky_color = mix(
            vec3<f32>(0.3, 0.5, 0.8),
            vec3<f32>(0.6, 0.4, 0.9),
            sky_flow
        );
        color += sky_color * sky_mask * city_progress * 0.3;
    }

    // PHASE 4: Camera pulls back (0.55 - 0.80)
    let pullback_phase = phase(prog, 0.55, 0.80);
    if pullback_phase > 0.0 {
        let pullback_progress = easeInOut(pullback_phase);

        // System expands beyond edges
        let expand_zoom = 1.0 + pullback_progress * 4.0;
        let expand_uv = uv_aspect * expand_zoom;

        // Organism silhouette
        let organism_shape = fbm(expand_uv * 2.0 + vec2<f32>(t * 0.1, 0.0), 5);
        let organism = smoothstep(0.4, 0.6, organism_shape);

        // Organism glow (alive, intricate, aware)
        let glow_color = vec3<f32>(0.5, 0.8, 1.0);
        color += glow_color * organism * (1.0 - pullback_progress * 0.5);

        // Tendrils extending into void
        let num_tendrils = 12.0;
        for (var i = 0.0; i < num_tendrils; i += 1.0) {
            let tendril_angle = (i / num_tendrils) * 6.28318 + t * 0.2;
            let tendril_dir = vec2<f32>(cos(tendril_angle), sin(tendril_angle));
            let tendril_dist = length(uv_aspect);

            let tendril_mask = smoothstep(0.5, 1.5, tendril_dist) *
                              smoothstep(0.05, 0.0, abs(atan2(uv_aspect.y, uv_aspect.x) - tendril_angle));

            color += glow_color * tendril_mask * pullback_progress * 0.3;
        }
    }

    // PHASE 5: Final message (0.75 - 1.0)
    let message_phase = phase(prog, 0.75, 1.0);
    if message_phase > 0.0 {
        // "The Impossible is Now Operational" - represented as pulsing central glow
        let message_pulse = sin(t * 3.0) * 0.5 + 0.5;
        let message_glow = exp(-length(uv_aspect) * 1.5) * message_phase;

        let message_color = vec3<f32>(0.9, 0.95, 1.0);
        color += message_color * message_glow * (0.5 + message_pulse * 0.5);

        // Subtle text position indicator (where text would appear)
        let text_y_pos = -0.6;
        let text_glow_line = smoothstep(0.1, 0.0, abs(uv.y - text_y_pos));
        color += message_color * text_glow_line * message_phase * 0.5;
    }

    // Fade to black at very end
    if prog > 0.95 {
        let final_fade = (prog - 0.95) / 0.05;
        color *= (1.0 - final_fade * 0.5);
    }

    // Vignette
    let vignette = 1.0 - length(uv) * 0.4;
    color *= vignette;

    return vec4<f32>(color, 1.0);
}
