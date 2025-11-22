// 0RB Boot Sequence Shader
// GPU-accelerated metallic smoke, plasma effects, and particle systems

struct BootUniforms {
    phase: u32,
    progress: f32,
    total_time: f32,
    smoke_intensity: f32,
    orb_brightness: f32,
    explosion_power: f32,
}

@group(0) @binding(0)
var<uniform> boot: BootUniforms;

@group(0) @binding(1)
var orb_texture: texture_2d<f32>;

@group(0) @binding(2)
var orb_sampler: sampler;

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
    @location(1) world_pos: vec2<f32>,
}

@vertex
fn vs_main(
    @builtin(vertex_index) vertex_index: u32,
) -> VertexOutput {
    var out: VertexOutput;

    // Fullscreen quad
    let x = f32(i32(vertex_index & 1u) * 2 - 1);
    let y = f32(i32(vertex_index & 2u) - 1);

    out.position = vec4<f32>(x, y, 0.0, 1.0);
    out.uv = vec2<f32>((x + 1.0) * 0.5, (1.0 - y) * 0.5);
    out.world_pos = vec2<f32>(x, y);

    return out;
}

// Noise functions for procedural effects

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

    for (var i = 0; i < 6; i++) {
        value += amplitude * noise(p_var * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }

    return value;
}

// Metallic smoke effect
fn metallic_smoke(uv: vec2<f32>, time: f32, intensity: f32) -> vec3<f32> {
    // Create flowing smoke patterns
    let offset = vec2<f32>(time * 0.1, time * 0.05);
    let smoke1 = fbm(uv * 3.0 + offset);
    let smoke2 = fbm(uv * 5.0 - offset * 0.5);

    let smoke = (smoke1 + smoke2) * 0.5;

    // Metallic color palette (chrome, platinum, gold, copper)
    let chrome = vec3<f32>(0.85, 0.85, 0.9);
    let platinum = vec3<f32>(0.7, 0.7, 0.8);
    let gold = vec3<f32>(1.0, 0.84, 0.0);
    let copper = vec3<f32>(0.72, 0.45, 0.2);

    // Mix metals based on noise
    var color = mix(chrome, platinum, smoke);
    color = mix(color, gold, noise(uv * 10.0 + time));
    color = mix(color, copper, noise(uv * 7.0 - time * 0.5));

    return color * intensity * smoke;
}

// Edge smoke swirl (emanates from screen edges)
fn edge_smoke(uv: vec2<f32>, time: f32, intensity: f32) -> vec3<f32> {
    let center = vec2<f32>(0.5, 0.5);
    let dist_from_center = distance(uv, center);
    let dist_from_edge = 1.0 - dist_from_center * 2.0;

    // Only show smoke near edges
    let edge_mask = smoothstep(0.0, 0.3, dist_from_edge);

    if edge_mask < 0.01 {
        return vec3<f32>(0.0);
    }

    // Swirling motion
    let angle = atan2(uv.y - 0.5, uv.x - 0.5);
    let swirl = vec2<f32>(
        cos(angle + time * 2.0) * dist_from_edge,
        sin(angle + time * 2.0) * dist_from_edge
    );

    let smoke = fbm(uv * 5.0 + swirl);
    let smoke_color = metallic_smoke(uv + swirl * 0.1, time, 1.0);

    return smoke_color * smoke * edge_mask * intensity;
}

// 0RB plasma glow effect
fn orb_plasma(uv: vec2<f32>, time: f32, brightness: f32) -> vec3<f32> {
    let center = vec2<f32>(0.5, 0.5);
    let to_center = uv - center;
    let dist = length(to_center);

    // Pulsing plasma ring
    let ring = abs(sin(dist * 20.0 - time * 3.0));
    let pulse = sin(time * 2.0) * 0.5 + 0.5;

    // Neural network-like patterns
    let neural1 = fbm(uv * 10.0 + vec2<f32>(time, 0.0));
    let neural2 = fbm(uv * 15.0 - vec2<f32>(0.0, time));

    let plasma = ring * pulse + neural1 * neural2;

    // Magenta/cyan/yellow plasma colors
    let color1 = vec3<f32>(1.0, 0.0, 1.0);  // Magenta
    let color2 = vec3<f32>(0.0, 1.0, 1.0);  // Cyan
    let color3 = vec3<f32>(1.0, 1.0, 0.0);  // Yellow

    var plasma_color = mix(color1, color2, neural1);
    plasma_color = mix(plasma_color, color3, neural2);

    return plasma_color * plasma * brightness;
}

// Explosion effect
fn explosion(uv: vec2<f32>, time: f32, power: f32) -> vec3<f32> {
    if power < 0.01 {
        return vec3<f32>(0.0);
    }

    let center = vec2<f32>(0.5, 0.5);
    let to_edge = uv - center;
    let dist = length(to_edge);

    // Expanding shockwave
    let wave = abs(dist - power * 0.5);
    let wave_intensity = 1.0 - smoothstep(0.0, 0.1, wave);

    // Radial particles
    let angle = atan2(to_edge.y, to_edge.x);
    let particle_density = noise(vec2<f32>(angle * 20.0, dist * 10.0));

    // Fiery explosion colors
    let inner = vec3<f32>(1.0, 1.0, 0.8);  // White hot
    let mid = vec3<f32>(1.0, 0.5, 0.0);    // Orange
    let outer = vec3<f32>(1.0, 0.0, 0.0);  // Red

    var color = mix(inner, mid, dist / 0.5);
    color = mix(color, outer, smoothstep(0.5, 1.0, dist));

    let intensity = wave_intensity + particle_density * power;

    return color * intensity * power;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    var final_color = vec3<f32>(0.0);  // Start with black

    let time = boot.total_time;
    let uv = in.uv;

    // Phase 0: Black Void
    if boot.phase == 0u {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }

    // Phase 1: Smoke Emergence
    if boot.phase == 1u {
        final_color += edge_smoke(uv, time, boot.smoke_intensity);
    }

    // Phase 2: ORB Rising
    if boot.phase == 2u {
        // Smoke continues
        final_color += metallic_smoke(uv, time, boot.smoke_intensity * 0.5);

        // ORB appears in center
        let center_dist = distance(uv, vec2<f32>(0.5, 0.5));
        if center_dist < 0.2 {
            // Sample ORB texture if available
            let orb_sample = textureSample(orb_texture, orb_sampler, uv);
            final_color += orb_sample.rgb * boot.orb_brightness;

            // Add plasma glow
            final_color += orb_plasma(uv, time, boot.orb_brightness * 0.3);
        }
    }

    // Phase 3: Dialogue
    if boot.phase == 3u {
        // Gentle ambient effects while user types
        final_color += metallic_smoke(uv, time, boot.smoke_intensity * 0.3);

        // ORB visible with gentle glow
        let center_dist = distance(uv, vec2<f32>(0.5, 0.5));
        if center_dist < 0.2 {
            let orb_sample = textureSample(orb_texture, orb_sampler, uv);
            final_color += orb_sample.rgb * boot.orb_brightness;
        }
    }

    // Phase 4: Explosion
    if boot.phase == 4u {
        final_color += explosion(uv, time, boot.explosion_power);
        final_color += metallic_smoke(uv, time, boot.smoke_intensity);

        // ORB over-bright
        let center_dist = distance(uv, vec2<f32>(0.5, 0.5));
        if center_dist < 0.2 {
            let orb_sample = textureSample(orb_texture, orb_sampler, uv);
            final_color += orb_sample.rgb * boot.orb_brightness;
        }
    }

    // Phase 5+: Container Reveal / Ready
    if boot.phase >= 5u {
        // Ambient smoke in background
        final_color += metallic_smoke(uv, time, boot.smoke_intensity * 0.2);

        // Dim ORB in center background
        let center_dist = distance(uv, vec2<f32>(0.5, 0.5));
        if center_dist < 0.15 {
            let orb_sample = textureSample(orb_texture, orb_sampler, uv);
            final_color += orb_sample.rgb * boot.orb_brightness * 0.3;
        }
    }

    // Ensure we never exceed 1.0 (HDR tonemapping)
    final_color = final_color / (final_color + vec3<f32>(1.0));

    return vec4<f32>(final_color, 1.0);
}
