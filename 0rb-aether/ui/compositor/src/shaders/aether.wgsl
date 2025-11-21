// 0RB_AETHER Shader - Procedural Aether Field
// Metallic orb with particle field and refraction effects

struct Uniforms {
    time: f32,
    resolution: vec2<f32>,
    _padding: f32,
}

@group(0) @binding(0)
var<uniform> uniforms: Uniforms;

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
}

@vertex
fn vs_main(@builtin(vertex_index) vertex_index: u32) -> VertexOutput {
    // Fullscreen triangle
    var positions = array<vec2<f32>, 6>(
        vec2<f32>(-1.0, -1.0),
        vec2<f32>(1.0, -1.0),
        vec2<f32>(1.0, 1.0),
        vec2<f32>(-1.0, -1.0),
        vec2<f32>(1.0, 1.0),
        vec2<f32>(-1.0, 1.0),
    );

    var out: VertexOutput;
    out.position = vec4<f32>(positions[vertex_index], 0.0, 1.0);
    out.uv = positions[vertex_index] * 0.5 + 0.5;
    return out;
}

// Noise functions
fn hash(p: vec2<f32>) -> f32 {
    return fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5453);
}

fn noise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let u = f * f * (3.0 - 2.0 * f);

    return mix(
        mix(hash(i + vec2<f32>(0.0, 0.0)), hash(i + vec2<f32>(1.0, 0.0)), u.x),
        mix(hash(i + vec2<f32>(0.0, 1.0)), hash(i + vec2<f32>(1.0, 1.0)), u.x),
        u.y
    );
}

fn fbm(p: vec2<f32>) -> f32 {
    var value = 0.0;
    var amplitude = 0.5;
    var pos = p;

    for (var i = 0; i < 5; i = i + 1) {
        value = value + amplitude * noise(pos);
        pos = pos * 2.0;
        amplitude = amplitude * 0.5;
    }

    return value;
}

// SDF for sphere
fn sdSphere(p: vec3<f32>, r: f32) -> f32 {
    return length(p) - r;
}

// Raymarching
fn rayMarch(ro: vec3<f32>, rd: vec3<f32>) -> f32 {
    var t = 0.0;

    for (var i = 0; i < 64; i = i + 1) {
        let p = ro + rd * t;
        let d = sdSphere(p, 0.5);

        if (d < 0.001) {
            return t;
        }

        t = t + d;

        if (t > 10.0) {
            break;
        }
    }

    return -1.0;
}

// Normal calculation
fn calcNormal(p: vec3<f32>) -> vec3<f32> {
    let e = vec2<f32>(0.001, 0.0);
    return normalize(vec3<f32>(
        sdSphere(p + e.xyy, 0.5) - sdSphere(p - e.xyy, 0.5),
        sdSphere(p + e.yxy, 0.5) - sdSphere(p - e.yxy, 0.5),
        sdSphere(p + e.yyx, 0.5) - sdSphere(p - e.yyx, 0.5)
    ));
}

// Metallic BRDF
fn metallicShading(n: vec3<f32>, v: vec3<f32>, l: vec3<f32>) -> vec3<f32> {
    let h = normalize(l + v);
    let ndotl = max(dot(n, l), 0.0);
    let ndoth = max(dot(n, h), 0.0);
    let ndotv = max(dot(n, v), 0.0);

    // Fresnel (Schlick)
    let f0 = vec3<f32>(0.7, 0.75, 0.8); // Silver-ish
    let fresnel = f0 + (1.0 - f0) * pow(1.0 - ndotv, 5.0);

    // Specular
    let roughness = 0.15;
    let a = roughness * roughness;
    let d = a / (3.14159 * pow(ndoth * ndoth * (a - 1.0) + 1.0, 2.0));

    let specular = fresnel * d * ndotl;

    // Ambient
    let ambient = vec3<f32>(0.05, 0.07, 0.1);

    return ambient + specular;
}

// Particle field
fn particleField(uv: vec2<f32>, time: f32) -> f32 {
    var particles = 0.0;

    for (var i = 0; i < 20; i = i + 1) {
        let fi = f32(i);
        let offset = vec2<f32>(
            sin(time * 0.3 + fi * 1.7) * 0.4,
            cos(time * 0.2 + fi * 2.3) * 0.4
        );
        let pos = vec2<f32>(
            hash(vec2<f32>(fi, 0.0)) - 0.5,
            hash(vec2<f32>(0.0, fi)) - 0.5
        ) + offset;

        let d = length(uv - pos);
        let size = 0.01 + hash(vec2<f32>(fi, fi)) * 0.02;
        particles = particles + smoothstep(size, 0.0, d);
    }

    return particles;
}

// Aether glow effect
fn aetherGlow(uv: vec2<f32>, time: f32) -> vec3<f32> {
    let n = fbm(uv * 3.0 + time * 0.1);
    let glow = smoothstep(0.3, 0.7, n);

    // 0RB color palette: deep blue to cyan to white
    let c1 = vec3<f32>(0.1, 0.2, 0.4);
    let c2 = vec3<f32>(0.2, 0.6, 0.8);
    let c3 = vec3<f32>(0.8, 0.9, 1.0);

    var col = mix(c1, c2, glow);
    col = mix(col, c3, pow(glow, 3.0));

    return col * 0.5;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let uv = (in.uv - 0.5) * 2.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let uv_corrected = vec2<f32>(uv.x * aspect, uv.y);

    let time = uniforms.time;

    // Camera setup
    let ro = vec3<f32>(0.0, 0.0, 2.0);
    let rd = normalize(vec3<f32>(uv_corrected, -1.5));

    // Background: Aether field
    var col = aetherGlow(uv_corrected, time);

    // Particles
    let particles = particleField(uv_corrected, time);
    col = col + vec3<f32>(0.3, 0.5, 0.8) * particles;

    // Raymarch the orb
    let t = rayMarch(ro, rd);

    if (t > 0.0) {
        let p = ro + rd * t;
        let n = calcNormal(p);
        let v = -rd;

        // Animated light
        let lightPos = vec3<f32>(
            sin(time * 0.5) * 2.0,
            1.0 + cos(time * 0.3) * 0.5,
            2.0
        );
        let l = normalize(lightPos - p);

        // Metallic shading
        let orbCol = metallicShading(n, v, l);

        // Add noise distortion on surface
        let surfaceNoise = fbm(p.xy * 5.0 + time * 0.2) * 0.1;

        // Reflection of aether field
        let reflDir = reflect(-v, n);
        let reflUV = reflDir.xy * 0.5 + 0.5;
        let reflection = aetherGlow(reflUV, time) * 0.3;

        col = orbCol + reflection + vec3<f32>(surfaceNoise);

        // Edge glow
        let edgeFactor = 1.0 - dot(n, v);
        col = col + vec3<f32>(0.2, 0.5, 0.8) * pow(edgeFactor, 3.0);
    }

    // Vignette
    let vignette = 1.0 - length(uv) * 0.5;
    col = col * vignette;

    // Tone mapping
    col = col / (col + vec3<f32>(1.0));
    col = pow(col, vec3<f32>(1.0 / 2.2));

    return vec4<f32>(col, 1.0);
}
