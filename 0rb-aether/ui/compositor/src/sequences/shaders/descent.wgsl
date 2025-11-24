// "The Descent Into the Atlas"
// Onboarding journey - falling through knowledge space into 3iAtlas

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

// Noise functions
fn hash12(p: vec2<f32>) -> f32 {
    let p3 = fract(vec3<f32>(p.xyx) * 0.1031);
    let p4 = p3 + dot(p3, p3.yzx + 33.33);
    return fract((p4.x + p4.y) * p4.z);
}

fn hash22(p: vec2<f32>) -> vec2<f32> {
    let p3 = fract(vec3<f32>(p.xyx) * vec3<f32>(0.1031, 0.1030, 0.0973));
    let p4 = p3 + dot(p3, p3.yzx + 33.33);
    return fract((p4.xx + p4.yz) * p4.zy);
}

// Tunnel SDF
fn sdTunnel(p: vec3<f32>, radius: f32) -> f32 {
    let xz = vec2<f32>(p.x, p.z);
    return length(xz) - radius;
}

// Glyph-like floating symbols
fn glyph(p: vec2<f32>, seed: f32) -> f32 {
    let h = hash12(vec2<f32>(seed, seed * 1.7));
    let size = 0.05 + h * 0.1;

    // Create various glyph shapes based on hash
    if h < 0.25 {
        // Circle
        return length(p) - size;
    } else if h < 0.5 {
        // Square
        let d = abs(p) - vec2<f32>(size);
        return length(max(d, vec2<f32>(0.0))) + min(max(d.x, d.y), 0.0);
    } else if h < 0.75 {
        // Triangle
        let a = 2.094; // 120 degrees
        let n = vec2<f32>(sin(a), cos(a));
        let p2 = abs(p);
        return max(dot(p2, n), p2.y) - size;
    } else {
        // Plus sign
        let d1 = abs(p.x) - size * 0.3;
        let d2 = abs(p.y) - size;
        let d3 = abs(p.y) - size * 0.3;
        let d4 = abs(p.x) - size;
        return min(max(d1, d2), max(d3, d4));
    }
}

// Phase keyframes
fn phase(t: f32, start: f32, end: f32) -> f32 {
    return clamp((t - start) / (end - start), 0.0, 1.0);
}

fn easeInOut(t: f32) -> f32 {
    return t * t * (3.0 - 2.0 * t);
}

fn easeOut(t: f32) -> f32 {
    return 1.0 - (1.0 - t) * (1.0 - t);
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let uv = (in.uv - 0.5) * 2.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let uv_aspect = vec2<f32>(uv.x * aspect, uv.y);

    let t = uniforms.time;
    let prog = uniforms.progress;

    var color = vec3<f32>(0.0);

    // PHASE 1: The Tear (0.0 - 0.15)
    let tear_phase = phase(prog, 0.0, 0.15);
    if tear_phase > 0.0 {
        let tear_width = easeOut(tear_phase) * 0.3;
        let tear_glow = smoothstep(tear_width + 0.1, tear_width, abs(uv.x));
        color += vec3<f32>(0.9, 0.95, 1.0) * tear_glow * 2.0;
    }

    // PHASE 2: The Fall (0.15 - 0.60)
    let fall_phase = phase(prog, 0.15, 0.60);
    if fall_phase > 0.0 {
        let fade = easeInOut(fall_phase);

        // Create tunnel perspective
        let tunnel_speed = t * 2.0 + fall_phase * 10.0;
        let z = fract(tunnel_speed);
        let depth = 1.0 - z;

        // Tunnel walls
        let angle = atan2(uv_aspect.y, uv_aspect.x);
        let radius = length(uv_aspect);
        let tunnel_radius = 0.8 * (1.0 - fall_phase * 0.3);
        let tunnel = smoothstep(tunnel_radius + 0.05, tunnel_radius, radius);

        // Glyphs orbiting in the tunnel
        let num_glyphs = 12.0;
        for (var i = 0.0; i < num_glyphs; i += 1.0) {
            let seed = floor(tunnel_speed) * 17.0 + i;
            let glyph_angle = (i / num_glyphs) * 6.28318 + t * 0.5 + hash12(vec2<f32>(seed)) * 6.28;
            let glyph_dist = 0.5 + hash12(vec2<f32>(seed + 1.0)) * 0.2;

            let glyph_pos = vec2<f32>(
                cos(glyph_angle) * glyph_dist,
                sin(glyph_angle) * glyph_dist
            );

            let glyph_size = (0.8 + hash12(vec2<f32>(seed + 2.0)) * 0.4) * depth;
            let glyph_uv = (uv_aspect - glyph_pos * depth) / glyph_size;

            let g = glyph(glyph_uv, seed);
            let glyph_alpha = smoothstep(0.02, 0.0, g) * depth;

            // Glyph color - curious spirits (cyan to white)
            let glyph_color = mix(
                vec3<f32>(0.3, 0.9, 1.0),
                vec3<f32>(1.0, 1.0, 1.0),
                hash12(vec2<f32>(seed + 3.0))
            );

            color += glyph_color * glyph_alpha * fade * 0.8;
        }

        // Tunnel ambient light
        color += vec3<f32>(0.05, 0.1, 0.2) * tunnel * fade;
    }

    // PHASE 3: The Scan (0.50 - 0.70)
    let scan_phase = phase(prog, 0.50, 0.70);
    if scan_phase > 0.0 {
        let scan_pos = easeInOut(scan_phase);
        let scan_line = smoothstep(0.02, 0.0, abs(uv.y - (scan_pos * 2.0 - 1.0)));
        color += vec3<f32>(1.0, 0.95, 0.7) * scan_line * 3.0;

        // Scan glow expanding
        let glow = smoothstep(0.3, 0.0, abs(uv.y - (scan_pos * 2.0 - 1.0)));
        color += vec3<f32>(0.8, 0.9, 1.0) * glow * 0.5;
    }

    // PHASE 4: The Burst (0.65 - 0.85)
    let burst_phase = phase(prog, 0.65, 0.85);
    if burst_phase > 0.0 {
        let burst_radius = easeOut(burst_phase) * 2.0;
        let dist = length(uv_aspect);

        // Radial burst
        let burst = smoothstep(burst_radius + 0.1, burst_radius - 0.05, dist);
        let burst_glow = exp(-dist * 2.0) * burst_phase;

        color += vec3<f32>(0.9, 0.95, 1.0) * burst_glow * 2.0;

        // Expanding ring
        let ring = smoothstep(0.02, 0.0, abs(dist - burst_radius));
        color += vec3<f32>(1.0, 1.0, 1.0) * ring * 3.0;
    }

    // PHASE 5: The Atlas Sphere (0.80 - 1.0)
    let sphere_phase = phase(prog, 0.80, 1.0);
    if sphere_phase > 0.0 {
        let fade = easeInOut(sphere_phase);

        // Rotating sphere with orbiting knowledge islands
        let sphere_center = vec2<f32>(0.0, 0.0);
        let sphere_radius = 0.3;
        let dist_to_sphere = length(uv_aspect - sphere_center);

        // Main sphere
        let sphere = smoothstep(sphere_radius + 0.05, sphere_radius - 0.05, dist_to_sphere);

        // Sphere surface detail (rotating)
        let angle = atan2(uv_aspect.y, uv_aspect.x) + t * 0.3;
        let lat = dist_to_sphere / sphere_radius;
        let detail = sin(angle * 8.0 + lat * 10.0) * 0.5 + 0.5;

        color += vec3<f32>(0.2, 0.6, 1.0) * sphere * (0.5 + detail * 0.5) * fade;

        // Sphere rim lighting
        let rim = smoothstep(sphere_radius - 0.05, sphere_radius + 0.05, dist_to_sphere);
        let rim_power = rim * (1.0 - sphere);
        color += vec3<f32>(0.5, 0.9, 1.0) * rim_power * 2.0 * fade;

        // Crystalline obelisks in corners
        let num_obelisks = 4.0;
        for (var i = 0.0; i < num_obelisks; i += 1.0) {
            let obelisk_angle = (i / num_obelisks) * 6.28318 + t * 0.2;
            let obelisk_dist = 1.2;
            let obelisk_pos = vec2<f32>(
                cos(obelisk_angle) * obelisk_dist,
                sin(obelisk_angle) * obelisk_dist
            );

            let obelisk_uv = uv_aspect - obelisk_pos;
            let obelisk_width = 0.08;
            let obelisk_height = 0.4;

            let d_x = abs(obelisk_uv.x) - obelisk_width;
            let d_y = abs(obelisk_uv.y) - obelisk_height;
            let obelisk = smoothstep(0.02, 0.0, max(d_x, d_y));

            color += vec3<f32>(0.6, 0.8, 1.0) * obelisk * 0.3 * fade;
        }
    }

    // Vignette throughout
    let vignette = 1.0 - length(uv_aspect) * 0.5;
    color *= vignette;

    return vec4<f32>(color, 1.0);
}
