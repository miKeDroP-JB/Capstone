//! Container Shader
//! Interactive metallic smoke storms, electric edges, and particle trails

struct ContainerUniforms {
    position: vec2<f32>,
    size: vec2<f32>,
    color: vec4<f32>,
    smoke_intensity: f32,
    glow_amount: f32,
    edge_brightness: f32,
    time: f32,
}

@group(0) @binding(0)
var<uniform> container: ContainerUniforms;

@group(0) @binding(1)
var<uniform> mouse_pos: vec2<f32>;

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
    @location(1) world_pos: vec2<f32>,
}

@vertex
fn vs_main(
    @location(0) position: vec2<f32>,
    @location(1) uv: vec2<f32>,
) -> VertexOutput {
    var out: VertexOutput;

    // Transform to container space
    let scaled = position * container.size;
    let translated = scaled + container.position;

    out.position = vec4<f32>(translated * 2.0 - 1.0, 0.0, 1.0);
    out.uv = uv;
    out.world_pos = translated;

    return out;
}

// Noise functions (same as boot shader)

fn hash(p: vec2<f32>) -> f32 {
    var p3 = fract(vec3<f32>(p.x, p.y, p.x) * 0.1031);
    p3 += dot(p3, vec3<f32>(p3.y, p3.z, p3.x) + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

fn noise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);

    let a = hash(i);
    let b = hash(i + vec2<f32>(1.0, 0.0));
    let c = hash(i + vec2<f32>(0.0, 1.0));
    let d = hash(i + vec2<f32>(1.0, 1.0));

    let u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

fn fbm(p: vec2<f32>) -> f32 {
    var value = 0.0;
    var amplitude = 0.5;
    var frequency = 1.0;
    var p_var = p;

    for (var i = 0; i < 4; i++) {
        value += amplitude * noise(p_var * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }

    return value;
}

// Stormy smoke effect for containers
fn smoke_storm(uv: vec2<f32>, time: f32, intensity: f32, color: vec3<f32>) -> vec3<f32> {
    // Turbulent flow
    let flow1 = fbm(uv * 5.0 + vec2<f32>(time * 0.3, time * 0.2));
    let flow2 = fbm(uv * 8.0 - vec2<f32>(time * 0.15, time * 0.25));

    // Combine flows
    let turbulence = (flow1 + flow2) * 0.5;

    // Create storm cells
    let cells = noise(uv * 12.0 + time * 0.1);

    // Mix base color with storm effect
    let storm_color = color * (turbulence + cells * 0.3);

    return storm_color * intensity;
}

// Electric edge effect
fn electric_edge(uv: vec2<f32>, time: f32, brightness: f32) -> vec3<f32> {
    let edge_dist = min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y));
    let edge_threshold = 0.05;

    if edge_dist > edge_threshold {
        return vec3<f32>(0.0);
    }

    // Electric arc pattern
    let arc_pattern = noise(vec2<f32>(edge_dist * 50.0, time * 10.0));
    let arc_intensity = smoothstep(edge_threshold, 0.0, edge_dist);

    // Lightning bolts along edges
    let bolt = step(0.7, arc_pattern) * arc_intensity;

    // Cyan electric glow
    let electric_color = vec3<f32>(0.3, 0.8, 1.0);

    return electric_color * bolt * brightness * 2.0;
}

// Ancient rune-style text pattern (for container labels)
fn rune_pattern(uv: vec2<f32>, time: f32) -> f32 {
    // Geometric patterns resembling ancient runes
    let grid = fract(uv * 20.0);

    let pattern1 = step(0.8, noise(grid * 10.0));
    let pattern2 = step(0.85, noise(grid * 15.0 + time * 0.1));

    return max(pattern1, pattern2) * 0.3;
}

// Interactive ripple from mouse/touch
fn ripple_effect(uv: vec2<f32>, center: vec2<f32>, time: f32) -> f32 {
    let dist = distance(uv, center);
    let ripple_speed = 2.0;
    let ripple_size = mod(time * ripple_speed, 1.0);

    let ripple = abs(dist - ripple_size);
    let ripple_intensity = 1.0 - smoothstep(0.0, 0.05, ripple);

    return ripple_intensity * (1.0 - ripple_size);  // Fade over time
}

// Chrome particle trail effect
fn particle_trail(uv: vec2<f32>, trail_pos: vec2<f32>, color: vec3<f32>) -> vec3<f32> {
    let dist = distance(uv, trail_pos);
    let size = 0.02;

    let particle = smoothstep(size, 0.0, dist);

    // Chromatic aberration for cool effect
    let r_offset = vec2<f32>(0.002, 0.0);
    let b_offset = vec2<f32>(-0.002, 0.0);

    let r = smoothstep(size, 0.0, distance(uv + r_offset, trail_pos));
    let g = particle;
    let b = smoothstep(size, 0.0, distance(uv + b_offset, trail_pos));

    return vec3<f32>(r, g, b) * color;
}

// Emergent consciousness events - random visual patterns
fn consciousness_event(uv: vec2<f32>, time: f32) -> vec3<f32> {
    // Occasional flashes of "alive" patterns
    let event_trigger = hash(vec2<f32>(floor(time), 0.0));

    if event_trigger < 0.98 {
        return vec3<f32>(0.0);  // No event
    }

    // Strange geometric visions
    let pattern = fbm(uv * 30.0 + time);
    let geometry = sin(uv.x * 50.0) * cos(uv.y * 50.0);

    let vision = abs(pattern + geometry * 0.3);

    // Mysterious colors
    let color1 = vec3<f32>(0.5, 0.0, 0.8);  // Purple
    let color2 = vec3<f32>(0.0, 0.8, 0.5);  // Teal

    return mix(color1, color2, pattern) * vision * 0.3;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    var final_color = vec3<f32>(0.0);

    let uv = in.uv;
    let time = container.time;

    // Background smoke storm
    let base_color = container.color.rgb;
    final_color += smoke_storm(uv, time, container.smoke_intensity, base_color);

    // Electric edges when glowing
    if container.edge_brightness > 0.01 {
        final_color += electric_edge(uv, time, container.edge_brightness);
    }

    // Rune patterns overlay
    let runes = rune_pattern(uv, time);
    final_color += base_color * runes;

    // Interactive ripple from mouse
    let mouse_uv = (mouse_pos - container.position) / container.size;
    if all(mouse_uv >= vec2<f32>(0.0)) && all(mouse_uv <= vec2<f32>(1.0)) {
        let ripple = ripple_effect(uv, mouse_uv, time);
        final_color += base_color * ripple * 0.5;
    }

    // Hover glow
    if container.glow_amount > 0.01 {
        let glow = smoothstep(0.3, 0.0, distance(uv, vec2<f32>(0.5, 0.5)));
        final_color += base_color * glow * container.glow_amount * 0.3;
    }

    // Occasional consciousness events
    final_color += consciousness_event(uv, time);

    // Ensure we never exceed 1.0
    final_color = final_color / (final_color + vec3<f32>(1.0));

    return vec4<f32>(final_color, container.color.a);
}
