// THE DESCENT INTO THE ATLAS
// Onboarding Journey - "You don't learn the system. The system learns you."
//
// Timeline (10 seconds):
// Phase 1 (0-15%):   Black → point of light → vertical tear opens
// Phase 2 (15-60%):  Fall through corridor with 12 orbiting glyphs
// Phase 3 (50-70%):  Ring of light scans down ("Calibration")
// Phase 4 (65-85%):  Corridor bursts outward into void
// Phase 5 (80-100%): Atlas sphere with crystalline obelisks appears

struct Uniforms {
    time: f32,
    progress: f32,
    resolution: vec2<f32>,
    parameters: array<f32, 8>,
}

@group(0) @binding(0)
var<uniform> uniforms: Uniforms;

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
}

@vertex
fn vs_main(@builtin(vertex_index) vertex_index: u32) -> VertexOutput {
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

// === UTILITY FUNCTIONS ===

fn hash(p: vec2<f32>) -> f32 {
    return fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5453);
}

fn hash3(p: vec3<f32>) -> f32 {
    return fract(sin(dot(p, vec3<f32>(127.1, 311.7, 74.7))) * 43758.5453);
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

// Easing functions
fn easeInOutCubic(t: f32) -> f32 {
    if (t < 0.5) {
        return 4.0 * t * t * t;
    } else {
        let f = 2.0 * t - 2.0;
        return 0.5 * f * f * f + 1.0;
    }
}

fn easeOutQuart(t: f32) -> f32 {
    let f = t - 1.0;
    return 1.0 - f * f * f * f;
}

fn easeInQuad(t: f32) -> f32 {
    return t * t;
}

// Map value from one range to another
fn remap(value: f32, inMin: f32, inMax: f32, outMin: f32, outMax: f32) -> f32 {
    return outMin + (outMax - outMin) * clamp((value - inMin) / (inMax - inMin), 0.0, 1.0);
}

// === SIGNED DISTANCE FUNCTIONS ===

fn sdCircle(p: vec2<f32>, r: f32) -> f32 {
    return length(p) - r;
}

fn sdBox(p: vec2<f32>, b: vec2<f32>) -> f32 {
    let d = abs(p) - b;
    return length(max(d, vec2<f32>(0.0))) + min(max(d.x, d.y), 0.0);
}

fn sdTriangle(p: vec2<f32>, r: f32) -> f32 {
    let k = sqrt(3.0);
    var q = p;
    q.x = abs(q.x) - r;
    q.y = q.y + r / k;
    if (q.x + k * q.y > 0.0) {
        q = vec2<f32>(q.x - k * q.y, -k * q.x - q.y) / 2.0;
    }
    q.x = q.x - clamp(q.x, -2.0 * r, 0.0);
    return -length(q) * sign(q.y);
}

fn sdCross(p: vec2<f32>, b: f32, r: f32) -> f32 {
    let q = abs(p);
    let d1 = sdBox(q, vec2<f32>(b, r));
    let d2 = sdBox(q, vec2<f32>(r, b));
    return min(d1, d2);
}

fn sdSphere(p: vec3<f32>, r: f32) -> f32 {
    return length(p) - r;
}

// === GLYPH GENERATION ===

fn glyph(p: vec2<f32>, index: i32, time: f32) -> f32 {
    // Each glyph is unique based on index
    let seed = f32(index) * 1.7;
    let glyphType = i32(hash(vec2<f32>(seed, 0.0)) * 4.0);

    // Rotation based on index and time
    let angle = seed * 0.5 + time * 0.3;
    let c = cos(angle);
    let s = sin(angle);
    let rotP = vec2<f32>(p.x * c - p.y * s, p.x * s + p.y * c);

    var d: f32;
    if (glyphType == 0) {
        d = sdCircle(rotP, 0.03);
    } else if (glyphType == 1) {
        d = sdBox(rotP, vec2<f32>(0.025, 0.025));
    } else if (glyphType == 2) {
        d = sdTriangle(rotP, 0.035);
    } else {
        d = sdCross(rotP, 0.025, 0.008);
    }

    return d;
}

// === PHASE RENDERERS ===

// Phase 1: Point of light and vertical tear
fn renderPhase1(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;
    var col = vec3<f32>(0.0);

    // Progress within phase (0-15%)
    let phaseProgress = remap(progress, 0.0, 0.15, 0.0, 1.0);

    // Point of light appears and pulses
    let pointPhase = remap(phaseProgress, 0.0, 0.3, 0.0, 1.0);
    let pointIntensity = easeOutQuart(pointPhase);
    let pulse = 1.0 + 0.3 * sin(time * 8.0);
    let pointSize = 0.01 * pointIntensity * pulse;
    let pointDist = length(p);
    let point = smoothstep(pointSize + 0.02, pointSize, pointDist) * pointIntensity;
    col = col + vec3<f32>(0.8, 0.9, 1.0) * point;

    // Vertical tear opens
    let tearPhase = remap(phaseProgress, 0.4, 1.0, 0.0, 1.0);
    if (tearPhase > 0.0) {
        let tearHeight = easeInOutCubic(tearPhase) * 0.8;
        let tearWidth = 0.02 + tearPhase * 0.03;

        // Tear SDF
        let tearDist = abs(p.x);
        let inTear = step(tearDist, tearWidth) * step(abs(p.y), tearHeight);

        // Tear glow
        let tearGlow = smoothstep(tearWidth + 0.1, tearWidth, tearDist) *
                       smoothstep(tearHeight + 0.1, tearHeight - 0.05, abs(p.y));
        col = col + vec3<f32>(0.5, 0.7, 1.0) * tearGlow * tearPhase;

        // Inner tear light
        col = col + vec3<f32>(1.0) * inTear * easeOutQuart(tearPhase);
    }

    return col;
}

// Phase 2: Fall through glyph corridor
fn renderPhase2(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let pCorrected = vec2<f32>(p.x * aspect, p.y);

    var col = vec3<f32>(0.0);

    // Progress within phase (15-60%)
    let phaseProgress = remap(progress, 0.15, 0.60, 0.0, 1.0);
    let fadeIn = easeOutQuart(remap(phaseProgress, 0.0, 0.2, 0.0, 1.0));

    // Tunnel effect - radial distance creates depth
    let tunnelDist = length(pCorrected);
    let depth = 1.0 / (tunnelDist + 0.1);

    // Tunnel walls with perspective
    let tunnelGlow = smoothstep(1.2, 0.3, tunnelDist);
    let tunnelColor = mix(
        vec3<f32>(0.05, 0.1, 0.2),
        vec3<f32>(0.2, 0.4, 0.6),
        tunnelGlow
    );
    col = tunnelColor * (0.3 + 0.2 * fbm(pCorrected * 3.0 + time * 0.5));

    // 12 orbiting glyphs
    for (var i = 0; i < 12; i = i + 1) {
        let fi = f32(i);
        let angle = fi * 3.14159 * 2.0 / 12.0 + time * 0.5 + phaseProgress * 2.0;

        // Depth oscillation
        let glyphDepth = 0.3 + 0.15 * sin(fi * 1.7 + time);
        let orbitRadius = 0.4 + glyphDepth * 0.3;

        let glyphPos = vec2<f32>(
            cos(angle) * orbitRadius,
            sin(angle) * orbitRadius
        );

        // Perspective scale based on depth
        let scale = 0.8 + glyphDepth * 0.5;
        let glyphP = (pCorrected - glyphPos) / scale;

        let d = glyph(glyphP, i, time);

        // Glyph color - cyan to white ("curious spirits")
        let glyphColor = mix(
            vec3<f32>(0.3, 0.8, 1.0),
            vec3<f32>(1.0, 1.0, 1.0),
            hash(vec2<f32>(fi, 0.5))
        );

        // Flickering based on "intent sampling"
        let flicker = 0.7 + 0.3 * sin(time * 5.0 + fi * 2.0);

        let glyphIntensity = smoothstep(0.01, 0.0, d) * flicker * fadeIn;
        col = col + glyphColor * glyphIntensity;

        // Glyph glow
        let glyphGlow = smoothstep(0.08, 0.0, d) * 0.3 * flicker * fadeIn;
        col = col + glyphColor * glyphGlow;
    }

    // Central tunnel light
    let centerLight = smoothstep(0.5, 0.0, tunnelDist) * 0.5;
    col = col + vec3<f32>(0.4, 0.6, 0.9) * centerLight * fadeIn;

    return col;
}

// Phase 3: Calibration scan
fn renderPhase3(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;

    // Keep Phase 2 as background
    var col = renderPhase2(uv, 0.60, time) * 0.7;

    // Progress within phase (50-70%)
    let phaseProgress = remap(progress, 0.50, 0.70, 0.0, 1.0);

    // Ring of light scans down
    let scanY = mix(0.8, -0.8, easeInOutCubic(phaseProgress));
    let scanDist = abs(p.y - scanY);

    // Main scan ring
    let ringIntensity = smoothstep(0.05, 0.0, scanDist);
    let ringColor = vec3<f32>(1.0, 0.95, 0.8); // Golden-white
    col = col + ringColor * ringIntensity * 2.0;

    // Scan ring glow
    let ringGlow = smoothstep(0.15, 0.0, scanDist) * 0.5;
    col = col + ringColor * ringGlow;

    // Expanding glow at scan position (the "touching your chest" moment)
    if (phaseProgress > 0.4 && phaseProgress < 0.6) {
        let touchPhase = remap(phaseProgress, 0.4, 0.6, 0.0, 1.0);
        let expandRadius = touchPhase * 0.3;
        let expandDist = length(p - vec2<f32>(0.0, scanY));
        let expandGlow = smoothstep(expandRadius + 0.1, expandRadius, expandDist);
        col = col + vec3<f32>(1.0, 0.9, 0.7) * expandGlow * sin(touchPhase * 3.14159);
    }

    return col;
}

// Phase 4: Burst outward
fn renderPhase4(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;

    var col = vec3<f32>(0.0);

    // Progress within phase (65-85%)
    let phaseProgress = remap(progress, 0.65, 0.85, 0.0, 1.0);

    // Radial explosion from center
    let dist = length(p);
    let burstRadius = easeOutQuart(phaseProgress) * 2.0;

    // Shockwave ring
    let ringDist = abs(dist - burstRadius * 0.8);
    let ring = smoothstep(0.1, 0.0, ringDist) * (1.0 - phaseProgress);
    col = col + vec3<f32>(0.6, 0.8, 1.0) * ring;

    // Expanding glow
    let expandGlow = smoothstep(burstRadius, 0.0, dist) * (1.0 - phaseProgress * 0.5);
    col = col + vec3<f32>(0.3, 0.5, 0.8) * expandGlow * 0.5;

    // Particle trails
    for (var i = 0; i < 8; i = i + 1) {
        let fi = f32(i);
        let angle = fi * 3.14159 * 2.0 / 8.0;
        let dir = vec2<f32>(cos(angle), sin(angle));
        let trailDist = dot(p, dir);
        let perpDist = length(p - dir * trailDist);

        if (trailDist > 0.0 && trailDist < burstRadius) {
            let trail = smoothstep(0.05, 0.0, perpDist) * smoothstep(0.0, burstRadius * 0.5, trailDist);
            col = col + vec3<f32>(0.5, 0.7, 1.0) * trail * (1.0 - phaseProgress);
        }
    }

    return col;
}

// Phase 5: Atlas sphere with obelisks
fn renderPhase5(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let pCorrected = vec2<f32>(p.x * aspect, p.y);

    var col = vec3<f32>(0.02, 0.03, 0.06); // Deep space background

    // Progress within phase (80-100%)
    let phaseProgress = remap(progress, 0.80, 1.0, 0.0, 1.0);
    let fadeIn = easeOutQuart(phaseProgress);

    // Background: concept constellations
    for (var i = 0; i < 30; i = i + 1) {
        let fi = f32(i);
        let starPos = vec2<f32>(
            hash(vec2<f32>(fi, 0.0)) * 4.0 - 2.0,
            hash(vec2<f32>(0.0, fi)) * 4.0 - 2.0
        );
        let starDist = length(pCorrected - starPos);
        let twinkle = 0.5 + 0.5 * sin(time * 2.0 + fi * 3.0);
        let star = smoothstep(0.02, 0.0, starDist) * twinkle * fadeIn;
        col = col + vec3<f32>(0.6, 0.7, 0.9) * star;
    }

    // Central Atlas sphere
    let sphereRadius = 0.3 * fadeIn;
    let sphereDist = length(pCorrected);

    if (sphereDist < sphereRadius + 0.1) {
        // Sphere surface with rotating terrain
        let sphereAngle = atan2(pCorrected.y, pCorrected.x) + time * 0.2;
        let latitude = asin(clamp(pCorrected.y / max(sphereDist, 0.001), -1.0, 1.0));

        // Surface detail
        let surfaceNoise = fbm(vec2<f32>(sphereAngle * 3.0, latitude * 5.0 + time * 0.1));

        // Sphere shading
        let sphereNormal = normalize(vec3<f32>(pCorrected.x, pCorrected.y, sqrt(max(0.0, sphereRadius * sphereRadius - sphereDist * sphereDist))));
        let lightDir = normalize(vec3<f32>(0.5, 0.5, 1.0));
        let diffuse = max(dot(sphereNormal, lightDir), 0.0);

        // Sphere color - islands of knowledge
        let sphereColor = mix(
            vec3<f32>(0.1, 0.3, 0.5),
            vec3<f32>(0.4, 0.7, 0.9),
            surfaceNoise
        );

        let sphereMask = smoothstep(sphereRadius, sphereRadius - 0.02, sphereDist);
        col = mix(col, sphereColor * (0.3 + diffuse * 0.7), sphereMask * fadeIn);

        // Rim lighting
        let rim = pow(1.0 - max(dot(sphereNormal, vec3<f32>(0.0, 0.0, 1.0)), 0.0), 3.0);
        col = col + vec3<f32>(0.3, 0.6, 1.0) * rim * sphereMask * fadeIn;
    }

    // 4 crystalline obelisks in corners
    let obeliskPositions = array<vec2<f32>, 4>(
        vec2<f32>(-0.7, -0.5),
        vec2<f32>(0.7, -0.5),
        vec2<f32>(-0.5, 0.6),
        vec2<f32>(0.5, 0.6)
    );

    for (var i = 0; i < 4; i = i + 1) {
        let obeliskPos = obeliskPositions[i];
        let obeliskP = pCorrected - obeliskPos;

        // Rotating obelisk
        let obeliskAngle = time * 0.5 + f32(i) * 1.57;
        let c = cos(obeliskAngle);
        let s = sin(obeliskAngle);
        let rotP = vec2<f32>(obeliskP.x * c - obeliskP.y * s, obeliskP.x * s + obeliskP.y * c);

        // Obelisk shape (tall thin rectangle)
        let obeliskDist = sdBox(rotP, vec2<f32>(0.02, 0.12));

        // Crystalline color
        let obeliskColor = mix(
            vec3<f32>(0.5, 0.8, 1.0),
            vec3<f32>(0.8, 0.9, 1.0),
            0.5 + 0.5 * sin(time * 2.0 + f32(i))
        );

        let obeliskIntensity = smoothstep(0.01, 0.0, obeliskDist) * fadeIn;
        col = col + obeliskColor * obeliskIntensity;

        // Obelisk glow
        let obeliskGlow = smoothstep(0.08, 0.0, obeliskDist) * 0.3 * fadeIn;
        col = col + obeliskColor * obeliskGlow;
    }

    // Vignette
    let vignette = 1.0 - length(p) * 0.4;
    col = col * vignette;

    return col;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let progress = uniforms.progress;
    let time = uniforms.time;

    var col = vec3<f32>(0.0);

    // Phase blending based on progress
    if (progress < 0.15) {
        col = renderPhase1(in.uv, progress, time);
    } else if (progress < 0.50) {
        let blend = remap(progress, 0.15, 0.20, 0.0, 1.0);
        let phase1 = renderPhase1(in.uv, 0.15, time);
        let phase2 = renderPhase2(in.uv, progress, time);
        col = mix(phase1, phase2, easeInOutCubic(blend));
    } else if (progress < 0.65) {
        col = renderPhase3(in.uv, progress, time);
    } else if (progress < 0.80) {
        let blend = remap(progress, 0.65, 0.70, 0.0, 1.0);
        let phase3 = renderPhase3(in.uv, 0.70, time);
        let phase4 = renderPhase4(in.uv, progress, time);
        col = mix(phase3, phase4, easeInOutCubic(blend));
    } else {
        let blend = remap(progress, 0.80, 0.85, 0.0, 1.0);
        let phase4 = renderPhase4(in.uv, 0.85, time);
        let phase5 = renderPhase5(in.uv, progress, time);
        col = mix(phase4, phase5, easeInOutCubic(blend));
    }

    // Final tone mapping
    col = col / (col + vec3<f32>(1.0));
    col = pow(col, vec3<f32>(1.0 / 2.2));

    return vec4<f32>(col, 1.0);
}
