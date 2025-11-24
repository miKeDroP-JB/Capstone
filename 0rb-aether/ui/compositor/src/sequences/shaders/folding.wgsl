// "The Folding World"
// 3iAtlas navigation - non-Euclidean knowledge topology that folds and reveals

struct Uniforms {
    time: f32,
    progress: f32,
    resolution: vec2<f32>,
    parameters: array<f32, 8>,
    // parameters[0] = zoom level (0.5 - 2.0)
    // parameters[1] = fold intensity (0.0 - 1.0)
    // parameters[2] = domain focus X (-1.0 - 1.0)
    // parameters[3] = domain focus Y (-1.0 - 1.0)
    // parameters[4] = insight flow speed (0.0 - 2.0)
    // parameters[5] = creative aurora intensity (0.0 - 1.0)
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
    let p3 = fract(vec3<f32>(p.xyx) * vec3<f32>(0.1031, 0.1030, 0.0973));
    let p4 = p3 + dot(p3, p3.yzx + 33.33);
    return fract((p4.x + p4.y) * p4.z);
}

fn hash22(p: vec2<f32>) -> vec2<f32> {
    let p3 = fract(vec3<f32>(p.xyx) * vec3<f32>(0.1031, 0.1030, 0.0973));
    let p4 = p3 + dot(p3, p3.yzx + 33.33);
    return fract((p4.xx + p4.yz) * p4.zy);
}

// Perlin-like noise
fn noise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let u = f * f * (3.0 - 2.0 * f);

    let a = hash12(i);
    let b = hash12(i + vec2<f32>(1.0, 0.0));
    let c = hash12(i + vec2<f32>(0.0, 1.0));
    let d = hash12(i + vec2<f32>(1.0, 1.0));

    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

// Fractional Brownian Motion
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

// Distance field for knowledge peaks (mountains)
fn mountain(p: vec2<f32>, height: f32, spread: f32) -> f32 {
    let dist = length(p) / spread;
    return height * exp(-dist * dist * 2.0);
}

// Distance field for problem canyons
fn canyon(p: vec2<f32>, depth: f32, width: f32) -> f32 {
    let x_dist = abs(p.x) / width;
    let y_influence = 1.0 - abs(p.y) * 0.5;
    return -depth * exp(-x_dist * x_dist * 3.0) * max(0.0, y_influence);
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let uv = (in.uv - 0.5) * 2.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    var uv_aspect = vec2<f32>(uv.x * aspect, uv.y);

    let t = uniforms.time;

    // Apply zoom
    let zoom = select(uniforms.parameters[0], 1.0, uniforms.parameters[0] == 0.0);
    uv_aspect = uv_aspect / zoom;

    // Apply focus offset
    let focus = vec2<f32>(uniforms.parameters[2], uniforms.parameters[3]);
    uv_aspect = uv_aspect - focus;

    // Fold intensity
    let fold_intensity = uniforms.parameters[1];

    // Non-Euclidean warping - the "folding" effect
    var warped_uv = uv_aspect;

    if fold_intensity > 0.0 {
        // Create folding waves
        let fold_freq = 3.0;
        let fold_x = sin(uv_aspect.y * fold_freq + t * 0.5) * fold_intensity * 0.3;
        let fold_y = sin(uv_aspect.x * fold_freq - t * 0.5) * fold_intensity * 0.3;

        warped_uv += vec2<f32>(fold_x, fold_y);

        // Add rotation twist based on distance from center
        let dist_from_center = length(uv_aspect);
        let twist_angle = dist_from_center * fold_intensity * 0.5;
        warped_uv = warped_uv * rot2D(twist_angle);
    }

    var color = vec3<f32>(0.0);
    var height = 0.0;

    // Base terrain using FBM (creates organic landscape)
    let terrain_height = fbm(warped_uv * 2.0 + t * 0.1, 6) * 0.5;
    height += terrain_height;

    // Knowledge mountains (ideas rise like mountains)
    let num_mountains = 5.0;
    for (var i = 0.0; i < num_mountains; i += 1.0) {
        let seed = i * 23.7;
        let mountain_pos = (hash22(vec2<f32>(seed, seed + 1.0)) - 0.5) * 3.0;
        let mountain_height = 0.3 + hash12(vec2<f32>(seed + 2.0, seed)) * 0.4;
        let mountain_spread = 0.3 + hash12(vec2<f32>(seed + 3.0, seed)) * 0.3;

        let m = mountain(warped_uv - mountain_pos, mountain_height, mountain_spread);
        height += m;

        // Mountain peaks glow (brilliant insights)
        if m > 0.2 {
            let peak_color = vec3<f32>(0.7, 0.9, 1.0);
            let peak_glow = pow((m - 0.2) / 0.4, 2.0);
            color += peak_color * peak_glow * 0.5;
        }
    }

    // Problem canyons (complexity chasms)
    let num_canyons = 3.0;
    for (var i = 0.0; i < num_canyons; i += 1.0) {
        let seed = i * 17.3 + 100.0;
        let canyon_pos_y = (hash12(vec2<f32>(seed, seed)) - 0.5) * 2.5;
        let canyon_angle = hash12(vec2<f32>(seed + 1.0, seed)) * 3.14159;
        let canyon_depth = 0.2 + hash12(vec2<f32>(seed + 2.0, seed)) * 0.2;
        let canyon_width = 0.2 + hash12(vec2<f32>(seed + 3.0, seed)) * 0.3;

        let canyon_uv = (warped_uv - vec2<f32>(0.0, canyon_pos_y)) * rot2D(canyon_angle);
        let c = canyon(canyon_uv, canyon_depth, canyon_width);
        height += c;

        // Canyon depths glow differently (problems have their own light)
        if c < -0.1 {
            let depth_color = vec3<f32>(0.8, 0.4, 0.6);
            let depth_glow = pow((-c - 0.1) / 0.3, 2.0);
            color += depth_color * depth_glow * 0.3;
        }
    }

    // Convert height to color (topographic visualization)
    let height_clamped = clamp(height, -0.5, 1.0);

    // Color based on elevation
    var terrain_color = vec3<f32>(0.0);
    if height_clamped < 0.0 {
        // Below sea level - blue to purple (depths)
        terrain_color = mix(
            vec3<f32>(0.1, 0.2, 0.4),
            vec3<f32>(0.3, 0.1, 0.3),
            -height_clamped * 2.0
        );
    } else if height_clamped < 0.3 {
        // Low lands - teal to green
        terrain_color = mix(
            vec3<f32>(0.2, 0.4, 0.4),
            vec3<f32>(0.3, 0.6, 0.5),
            height_clamped / 0.3
        );
    } else if height_clamped < 0.6 {
        // Mid elevation - green to yellow
        terrain_color = mix(
            vec3<f32>(0.3, 0.6, 0.5),
            vec3<f32>(0.6, 0.7, 0.4),
            (height_clamped - 0.3) / 0.3
        );
    } else {
        // High peaks - yellow to white (brilliant insights)
        terrain_color = mix(
            vec3<f32>(0.6, 0.7, 0.4),
            vec3<f32>(0.9, 0.95, 1.0),
            (height_clamped - 0.6) / 0.4
        );
    }

    color += terrain_color;

    // Insight rivers (flowing patterns of understanding)
    let flow_speed = select(uniforms.parameters[4], 1.0, uniforms.parameters[4] == 0.0);
    let river_flow = fbm(warped_uv * 4.0 + vec2<f32>(t * flow_speed * 0.3, 0.0), 4);
    let river_mask = smoothstep(0.45, 0.55, river_flow);

    // Rivers follow low-lands
    let river_elevation_mask = smoothstep(0.2, 0.0, height_clamped);
    let river_strength = river_mask * river_elevation_mask;

    let river_color = vec3<f32>(0.4, 0.8, 1.0);
    color = mix(color, river_color, river_strength * 0.6);

    // River flow animation (shimmering)
    let river_shimmer = sin(river_flow * 10.0 + t * 2.0) * 0.5 + 0.5;
    color += river_color * river_strength * river_shimmer * 0.3;

    // Creative leap auroras (possibilities spreading across sky)
    let aurora_intensity = select(uniforms.parameters[5], 0.7, uniforms.parameters[5] == 0.0);
    if aurora_intensity > 0.0 {
        let aurora_uv = warped_uv * 0.5 + vec2<f32>(t * 0.1, 0.0);
        let aurora_pattern = fbm(aurora_uv * 2.0, 3);
        let aurora_mask = smoothstep(0.3, 0.7, aurora_pattern) * smoothstep(-0.5, 0.5, uv.y);

        // Aurora color shifts
        let aurora_shift = t * 0.5;
        let aurora_color = vec3<f32>(
            sin(aurora_shift) * 0.5 + 0.5,
            sin(aurora_shift + 2.094) * 0.5 + 0.5,
            sin(aurora_shift + 4.189) * 0.5 + 0.5
        ) * 0.7 + 0.3;

        color += aurora_color * aurora_mask * aurora_intensity * 0.4;
    }

    // Contour lines (knowledge strata)
    let contour_freq = 10.0;
    let contour = abs(fract(height_clamped * contour_freq) - 0.5) * 2.0;
    let contour_line = smoothstep(0.9, 1.0, contour);
    color += vec3<f32>(0.5, 0.7, 0.9) * contour_line * 0.3;

    // Grid overlay (when folding, show the underlying structure)
    if fold_intensity > 0.3 {
        let grid_freq = 8.0;
        let grid_x = abs(fract(warped_uv.x * grid_freq) - 0.5) * 2.0;
        let grid_y = abs(fract(warped_uv.y * grid_freq) - 0.5) * 2.0;
        let grid = max(
            smoothstep(0.95, 1.0, grid_x),
            smoothstep(0.95, 1.0, grid_y)
        );

        color += vec3<f32>(0.7, 0.8, 1.0) * grid * fold_intensity * 0.5;
    }

    // Ambient lighting (three-point lighting for depth)
    let light_angle = atan2(uv_aspect.y, uv_aspect.x);
    let rim_light = pow(max(0.0, sin(light_angle - t * 0.2)), 2.0) * 0.2;
    color += vec3<f32>(0.6, 0.8, 1.0) * rim_light;

    // Vignette
    let vignette = 1.0 - length(uv) * 0.4;
    color *= vignette;

    return vec4<f32>(color, 1.0);
}
