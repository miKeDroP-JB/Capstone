// THE CELESTIAL NERVE NETWORK
// Agent Swarm Visualization - "A vast hovering galaxy of minds. A living nervous system."
//
// Features:
// - Galaxy of 10-100 agent nodes
// - Reverse-rain strand formation (rising connections)
// - Silver fire neural pathways
// - Learning shockwaves
// - "We Hear You" unified halo state
//
// Interactive Parameters:
// parameters[0] = zoom
// parameters[1] = fold_intensity (unused, for compatibility)
// parameters[2] = focus_x
// parameters[3] = focus_y
// parameters[4] = flow_speed
// parameters[5] = aurora_intensity (unused)
// parameters[6] = agent_count (10-100)
// parameters[7] = activity_level (0.0 - 1.0)
//
// Additional state tracked via progress:
// - Learning spikes triggered by progress changes
// - Command state for "We Hear You" mode
//
// This sequence loops continuously.

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

fn hash2(p: vec2<f32>) -> vec2<f32> {
    return vec2<f32>(
        fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5453),
        fract(sin(dot(p, vec2<f32>(269.5, 183.3))) * 43758.5453)
    );
}

fn hash3(p: f32) -> vec3<f32> {
    return vec3<f32>(
        fract(sin(p * 127.1) * 43758.5453),
        fract(sin(p * 311.7) * 43758.5453),
        fract(sin(p * 74.7) * 43758.5453)
    );
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
    for (var i = 0; i < 4; i = i + 1) {
        value = value + amplitude * noise(pos);
        pos = pos * 2.0;
        amplitude = amplitude * 0.5;
    }
    return value;
}

fn easeOutQuart(t: f32) -> f32 {
    let f = t - 1.0;
    return 1.0 - f * f * f * f;
}

fn easeInOutSine(t: f32) -> f32 {
    return -(cos(3.14159 * t) - 1.0) / 2.0;
}

// === AGENT NODE GENERATION ===

fn getAgentPosition(index: i32, time: f32, activityLevel: f32) -> vec2<f32> {
    let fi = f32(index);

    // Base position from hash
    let basePos = hash2(vec2<f32>(fi * 1.7, fi * 2.3)) * 2.0 - 1.0;

    // Orbital movement
    let orbitSpeed = 0.1 + hash(vec2<f32>(fi, 0.0)) * 0.2;
    let orbitRadius = 0.05 + hash(vec2<f32>(0.0, fi)) * 0.1;
    let orbitPhase = hash(vec2<f32>(fi, fi)) * 6.28318;

    let orbit = vec2<f32>(
        cos(time * orbitSpeed + orbitPhase) * orbitRadius,
        sin(time * orbitSpeed * 1.3 + orbitPhase) * orbitRadius
    );

    // Activity-based jitter
    let jitter = vec2<f32>(
        sin(time * 5.0 + fi * 3.0) * 0.02,
        cos(time * 4.0 + fi * 2.5) * 0.02
    ) * activityLevel;

    return basePos * 0.8 + orbit + jitter;
}

fn getAgentSize(index: i32, time: f32, activityLevel: f32) -> f32 {
    let fi = f32(index);
    let baseSize = 0.015 + hash(vec2<f32>(fi, 5.0)) * 0.01;

    // Pulse based on activity
    let pulse = 1.0 + 0.3 * sin(time * 3.0 + fi * 2.0) * activityLevel;

    return baseSize * pulse;
}

fn getAgentColor(index: i32, time: f32, activityLevel: f32) -> vec3<f32> {
    let fi = f32(index);

    // Base silver-white
    var color = vec3<f32>(0.8, 0.85, 0.9);

    // Activity adds warmth
    let warmth = activityLevel * 0.3;
    color = color + vec3<f32>(warmth, warmth * 0.5, 0.0);

    // Individual variation
    let hueShift = hash(vec2<f32>(fi, 7.0)) * 0.2;
    color = color + vec3<f32>(hueShift * 0.1, hueShift * 0.05, -hueShift * 0.05);

    return color;
}

// === CONNECTION RENDERING ===

fn sdLine(p: vec2<f32>, a: vec2<f32>, b: vec2<f32>, r: f32) -> f32 {
    let pa = p - a;
    let ba = b - a;
    let h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

fn renderConnection(p: vec2<f32>, a: vec2<f32>, b: vec2<f32>, time: f32, activityLevel: f32) -> vec3<f32> {
    let dist = length(a - b);
    let maxDist = 0.5; // Only connect nearby agents

    if (dist > maxDist) {
        return vec3<f32>(0.0);
    }

    let connectionStrength = (1.0 - dist / maxDist) * activityLevel;

    // Silver fire neural pathway
    let lineDist = sdLine(p, a, b, 0.002);

    // Main line
    let lineIntensity = smoothstep(0.005, 0.0, lineDist) * connectionStrength;

    // Traveling pulse (reverse rain - rising)
    let pathLength = length(b - a);
    let pathDir = normalize(b - a);
    let projDist = dot(p - a, pathDir);
    let projT = projDist / pathLength;

    // Multiple pulses traveling along connection
    var pulseIntensity = 0.0;
    for (var i = 0; i < 3; i = i + 1) {
        let fi = f32(i);
        let pulsePos = fract(time * 0.5 + fi * 0.33);
        let pulseDist = abs(projT - pulsePos);
        let pulse = smoothstep(0.15, 0.0, pulseDist) * smoothstep(0.0, 0.01, projT) * smoothstep(1.0, 0.99, projT);
        pulseIntensity = pulseIntensity + pulse;
    }

    // Silver fire color
    let silverFire = vec3<f32>(0.9, 0.95, 1.0);
    let warmFire = vec3<f32>(1.0, 0.8, 0.5);

    var color = silverFire * lineIntensity * 0.5;
    color = color + mix(silverFire, warmFire, pulseIntensity * 0.5) * pulseIntensity * connectionStrength;

    // Glow
    let glowDist = smoothstep(0.03, 0.0, lineDist);
    color = color + silverFire * glowDist * connectionStrength * 0.2;

    return color;
}

// === LEARNING SHOCKWAVE ===

fn renderLearningShockwave(p: vec2<f32>, center: vec2<f32>, time: f32, intensity: f32) -> vec3<f32> {
    let dist = length(p - center);

    // Expanding ring
    let waveSpeed = 0.8;
    let waveRadius = fract(time * 0.3) * waveSpeed;
    let waveDist = abs(dist - waveRadius);

    let wave = smoothstep(0.05, 0.0, waveDist) * (1.0 - waveRadius / waveSpeed);

    // Color: electric blue shockwave
    let waveColor = vec3<f32>(0.4, 0.7, 1.0);

    return waveColor * wave * intensity;
}

// === "WE HEAR YOU" UNIFIED HALO ===

fn renderUnifiedHalo(p: vec2<f32>, time: f32, commandState: f32) -> vec3<f32> {
    if (commandState < 0.01) {
        return vec3<f32>(0.0);
    }

    let dist = length(p);

    // Outer halo ring
    let haloRadius = 0.7 + 0.05 * sin(time * 2.0);
    let haloDist = abs(dist - haloRadius);
    let halo = smoothstep(0.03, 0.0, haloDist);

    // Inner rings
    let innerRing1 = smoothstep(0.02, 0.0, abs(dist - haloRadius * 0.7));
    let innerRing2 = smoothstep(0.015, 0.0, abs(dist - haloRadius * 0.5));

    // Radial rays
    let angle = atan2(p.y, p.x);
    let rayCount = 12.0;
    let rayAngle = fract(angle * rayCount / 6.28318 + 0.5) - 0.5;
    let ray = smoothstep(0.1, 0.0, abs(rayAngle)) * smoothstep(haloRadius * 0.3, haloRadius, dist);

    // Unified gold-white color
    let haloColor = vec3<f32>(1.0, 0.95, 0.8);

    var result = haloColor * halo;
    result = result + haloColor * innerRing1 * 0.5;
    result = result + haloColor * innerRing2 * 0.3;
    result = result + haloColor * ray * 0.4;

    // Central glow
    let centralGlow = smoothstep(0.3, 0.0, dist);
    result = result + haloColor * centralGlow * 0.3;

    // Pulsing
    let pulse = 0.8 + 0.2 * sin(time * 3.0);
    result = result * pulse;

    return result * commandState;
}

// === BACKGROUND GALAXY ===

fn renderGalaxyBackground(p: vec2<f32>, time: f32) -> vec3<f32> {
    // Deep space base
    var col = vec3<f32>(0.01, 0.02, 0.04);

    // Subtle nebula
    let nebula = fbm(p * 2.0 + time * 0.02);
    col = col + vec3<f32>(0.05, 0.03, 0.08) * nebula;

    // Background stars
    for (var i = 0; i < 50; i = i + 1) {
        let fi = f32(i);
        let starPos = hash2(vec2<f32>(fi * 1.3, fi * 2.7)) * 2.0 - 1.0;
        let starDist = length(p - starPos);
        let twinkle = 0.5 + 0.5 * sin(time * 2.0 + fi * 5.0);
        let star = smoothstep(0.008, 0.0, starDist) * twinkle * 0.5;
        col = col + vec3<f32>(0.6, 0.7, 0.9) * star;
    }

    return col;
}

// === REVERSE RAIN STRANDS ===

fn renderReverseRain(p: vec2<f32>, time: f32, activityLevel: f32) -> vec3<f32> {
    var rain = vec3<f32>(0.0);

    for (var i = 0; i < 20; i = i + 1) {
        let fi = f32(i);

        // Strand position
        let x = hash(vec2<f32>(fi, 0.0)) * 2.0 - 1.0;
        let speed = 0.3 + hash(vec2<f32>(fi, 1.0)) * 0.4;

        // Rising motion (reverse rain)
        let y = fract(time * speed + hash(vec2<f32>(fi, 2.0))) * 2.5 - 1.0;

        let strandPos = vec2<f32>(x, y);
        let strandDist = length(p - strandPos);

        // Strand length (vertical streak)
        let strandLength = 0.1 + hash(vec2<f32>(fi, 3.0)) * 0.1;
        let verticalDist = p.y - strandPos.y;

        if (verticalDist > -strandLength && verticalDist < 0.0) {
            let horizontalDist = abs(p.x - strandPos.x);
            let strand = smoothstep(0.003, 0.0, horizontalDist) *
                        smoothstep(-strandLength, 0.0, verticalDist);

            // Fade at edges
            let fade = smoothstep(-strandLength, -strandLength * 0.5, verticalDist);

            rain = rain + vec3<f32>(0.6, 0.75, 0.9) * strand * fade * activityLevel;
        }
    }

    return rain;
}

// === MAIN RENDERER ===

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let time = uniforms.time;

    // Extract parameters
    let zoom = max(uniforms.parameters[0], 0.5);
    let focusX = uniforms.parameters[2];
    let focusY = uniforms.parameters[3];
    let agentCountRaw = uniforms.parameters[6];
    let activityLevel = clamp(uniforms.parameters[7], 0.0, 1.0);

    // Agent count between 10-100
    let agentCount = i32(clamp(agentCountRaw, 10.0, 100.0));

    // Derive command state from progress (loops 0-1, high values = command mode)
    let commandState = smoothstep(0.8, 1.0, uniforms.progress) * activityLevel;

    // Derive learning spike from activity level changes
    let learningSpike = smoothstep(0.5, 1.0, activityLevel) * sin(time * 5.0) * 0.5 + 0.5;

    // Base coordinates
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    var p = (in.uv * 2.0 - 1.0);
    p.x = p.x * aspect;
    p = p / zoom;
    p = p - vec2<f32>(focusX, focusY);

    // === RENDER LAYERS ===

    // Background galaxy
    var col = renderGalaxyBackground(p, time);

    // Reverse rain strands (rising connections forming)
    col = col + renderReverseRain(p, time, activityLevel);

    // Agent connections (neural pathways)
    for (var i = 0; i < agentCount; i = i + 1) {
        let posA = getAgentPosition(i, time, activityLevel);

        // Connect to nearby agents
        for (var j = i + 1; j < agentCount; j = j + 1) {
            let posB = getAgentPosition(j, time, activityLevel);
            col = col + renderConnection(p, posA, posB, time, activityLevel);
        }
    }

    // Agent nodes
    for (var i = 0; i < agentCount; i = i + 1) {
        let pos = getAgentPosition(i, time, activityLevel);
        let size = getAgentSize(i, time, activityLevel);
        let nodeColor = getAgentColor(i, time, activityLevel);

        let dist = length(p - pos);

        // Node core
        let core = smoothstep(size, size * 0.5, dist);
        col = col + nodeColor * core;

        // Node glow
        let glow = smoothstep(size * 3.0, size, dist) * 0.3;
        col = col + nodeColor * glow;

        // Activity ring
        if (activityLevel > 0.3) {
            let ringRadius = size * 2.0;
            let ringDist = abs(dist - ringRadius);
            let ring = smoothstep(0.003, 0.0, ringDist) * (activityLevel - 0.3) / 0.7;
            col = col + nodeColor * ring * 0.5;
        }
    }

    // Learning shockwaves (emanate from random agents)
    if (learningSpike > 0.3) {
        let shockwaveAgent = i32(hash(vec2<f32>(floor(time * 0.5), 0.0)) * f32(agentCount));
        let shockwaveCenter = getAgentPosition(shockwaveAgent, time, activityLevel);
        col = col + renderLearningShockwave(p, shockwaveCenter, time, learningSpike);
    }

    // "We Hear You" unified halo
    col = col + renderUnifiedHalo(p, time, commandState);

    // Vignette
    let vignette = 1.0 - length(in.uv - 0.5) * 0.6;
    col = col * vignette;

    // Tone mapping
    col = col / (col + vec3<f32>(1.0));
    col = pow(col, vec3<f32>(1.0 / 2.2));

    return vec4<f32>(col, 1.0);
}
