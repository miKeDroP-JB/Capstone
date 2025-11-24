// THE ASCENSION SEQUENCE
// OS Reveal - "The Impossible is Now Operational."
//
// Timeline (12 seconds):
// Phase 1 (0-10%):   White flash reset - everything washes to pure white
// Phase 2 (10-30%):  Sacred geometry rune draws itself at center
// Phase 3 (25-60%):  OS city rises from below:
//                    - 12 towers of varying heights
//                    - 8 plazas (circular gathering points)
//                    - 6 bridges connecting structures
//                    - Flowing data rivers
//                    - 4 vortices at cardinal points
// Phase 4 (55-85%):  Camera pulls back revealing colossal organism structure
// Phase 5 (80-100%): Final state - "The Impossible is Now Operational"

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

fn easeOutQuart(t: f32) -> f32 {
    let f = t - 1.0;
    return 1.0 - f * f * f * f;
}

fn easeInOutCubic(t: f32) -> f32 {
    if (t < 0.5) {
        return 4.0 * t * t * t;
    } else {
        let f = 2.0 * t - 2.0;
        return 0.5 * f * f * f + 1.0;
    }
}

fn easeOutExpo(t: f32) -> f32 {
    if (t >= 1.0) { return 1.0; }
    return 1.0 - pow(2.0, -10.0 * t);
}

fn easeInQuad(t: f32) -> f32 {
    return t * t;
}

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

fn sdLine(p: vec2<f32>, a: vec2<f32>, b: vec2<f32>, r: f32) -> f32 {
    let pa = p - a;
    let ba = b - a;
    let h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

fn sdHexagon(p: vec2<f32>, r: f32) -> f32 {
    let k = vec3<f32>(-0.866025404, 0.5, 0.577350269);
    var q = abs(p);
    q = q - 2.0 * min(dot(k.xy, q), 0.0) * k.xy;
    q = q - vec2<f32>(clamp(q.x, -k.z * r, k.z * r), r);
    return length(q) * sign(q.y);
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

// === SACRED GEOMETRY RUNE ===

fn drawSacredRune(p: vec2<f32>, drawProgress: f32, time: f32) -> vec3<f32> {
    var col = vec3<f32>(0.0);

    let runeColor = vec3<f32>(0.8, 0.9, 1.0);
    let glowColor = vec3<f32>(0.4, 0.6, 1.0);

    // Outer circle (draws 0-20%)
    let outerCircleProgress = remap(drawProgress, 0.0, 0.2, 0.0, 1.0);
    if (outerCircleProgress > 0.0) {
        let angle = atan2(p.y, p.x) + 3.14159;
        let angleProgress = angle / 6.28318;
        if (angleProgress < outerCircleProgress) {
            let outerDist = abs(sdCircle(p, 0.35));
            let outer = smoothstep(0.008, 0.0, outerDist);
            col = col + runeColor * outer;
            col = col + glowColor * smoothstep(0.05, 0.0, outerDist) * 0.3;
        }
    }

    // Inner hexagon (draws 20-40%)
    let hexProgress = remap(drawProgress, 0.2, 0.4, 0.0, 1.0);
    if (hexProgress > 0.0) {
        let hexDist = abs(sdHexagon(p, 0.25 * hexProgress));
        let hex = smoothstep(0.006, 0.0, hexDist);
        col = col + runeColor * hex;
        col = col + glowColor * smoothstep(0.04, 0.0, hexDist) * 0.3;
    }

    // Six radial lines (draws 40-60%)
    let linesProgress = remap(drawProgress, 0.4, 0.6, 0.0, 1.0);
    if (linesProgress > 0.0) {
        for (var i = 0; i < 6; i = i + 1) {
            let fi = f32(i);
            let angle = fi * 3.14159 * 2.0 / 6.0;
            let dir = vec2<f32>(cos(angle), sin(angle));

            let lineStart = dir * 0.1;
            let lineEnd = dir * 0.35 * linesProgress;
            let lineDist = sdLine(p, lineStart, lineEnd, 0.003);
            let line = smoothstep(0.005, 0.0, lineDist);
            col = col + runeColor * line;
        }
    }

    // Central triangle (draws 60-80%)
    let triProgress = remap(drawProgress, 0.6, 0.8, 0.0, 1.0);
    if (triProgress > 0.0) {
        let triDist = abs(sdTriangle(p, 0.12 * triProgress));
        let tri = smoothstep(0.005, 0.0, triDist);
        col = col + runeColor * tri;
    }

    // Central dot (draws 80-100%)
    let dotProgress = remap(drawProgress, 0.8, 1.0, 0.0, 1.0);
    if (dotProgress > 0.0) {
        let dotDist = sdCircle(p, 0.03 * dotProgress);
        let dot = smoothstep(0.01, 0.0, dotDist);
        col = col + runeColor * dot * 2.0;
        // Pulsing glow
        let pulse = 0.5 + 0.5 * sin(time * 4.0);
        col = col + glowColor * smoothstep(0.1, 0.0, dotDist) * pulse * dotProgress;
    }

    return col;
}

// === OS CITY STRUCTURES ===

fn drawTower(p: vec2<f32>, basePos: vec2<f32>, height: f32, width: f32, riseAmount: f32) -> vec3<f32> {
    var col = vec3<f32>(0.0);

    // Tower rises from below
    let towerBottom = basePos.y - 0.5;
    let towerTop = mix(towerBottom, basePos.y + height, riseAmount);

    let towerP = p - vec2<f32>(basePos.x, (towerBottom + towerTop) * 0.5);
    let towerHeight = (towerTop - towerBottom) * 0.5;

    let towerDist = sdBox(towerP, vec2<f32>(width, towerHeight));

    // Tower body
    let towerIntensity = smoothstep(0.005, 0.0, towerDist);
    let towerColor = vec3<f32>(0.3, 0.5, 0.7);
    col = col + towerColor * towerIntensity;

    // Tower glow
    col = col + vec3<f32>(0.4, 0.6, 0.9) * smoothstep(0.05, 0.0, towerDist) * 0.3;

    // Tower top beacon
    if (riseAmount > 0.8) {
        let beaconPos = vec2<f32>(basePos.x, towerTop);
        let beaconDist = length(p - beaconPos);
        let beacon = smoothstep(0.015, 0.0, beaconDist);
        col = col + vec3<f32>(0.8, 0.9, 1.0) * beacon * (riseAmount - 0.8) / 0.2;
    }

    return col;
}

fn drawPlaza(p: vec2<f32>, center: vec2<f32>, radius: f32, visibility: f32) -> vec3<f32> {
    var col = vec3<f32>(0.0);

    let dist = length(p - center);

    // Plaza circle
    let plazaDist = abs(dist - radius);
    let plaza = smoothstep(0.008, 0.0, plazaDist) * visibility;
    col = col + vec3<f32>(0.5, 0.7, 0.9) * plaza;

    // Inner glow
    let innerGlow = smoothstep(radius, radius * 0.3, dist) * visibility * 0.3;
    col = col + vec3<f32>(0.3, 0.5, 0.8) * innerGlow;

    return col;
}

fn drawBridge(p: vec2<f32>, start: vec2<f32>, end: vec2<f32>, buildProgress: f32) -> vec3<f32> {
    var col = vec3<f32>(0.0);

    // Bridge builds from start to end
    let currentEnd = mix(start, end, buildProgress);
    let bridgeDist = sdLine(p, start, currentEnd, 0.006);

    let bridge = smoothstep(0.008, 0.0, bridgeDist);
    col = col + vec3<f32>(0.6, 0.75, 0.9) * bridge;

    // Bridge glow
    col = col + vec3<f32>(0.4, 0.6, 0.9) * smoothstep(0.03, 0.0, bridgeDist) * 0.2;

    return col;
}

fn drawDataRiver(p: vec2<f32>, time: f32, flowIntensity: f32) -> vec3<f32> {
    var col = vec3<f32>(0.0);

    // Multiple flowing rivers
    for (var i = 0; i < 4; i = i + 1) {
        let fi = f32(i);

        // River path
        let riverY = (fi - 1.5) * 0.25;
        let waveOffset = sin(p.x * 8.0 + time * 2.0 + fi * 2.0) * 0.05;
        let riverDist = abs(p.y - riverY - waveOffset);

        let riverWidth = 0.02;
        let river = smoothstep(riverWidth, 0.0, riverDist) * flowIntensity;

        // Flowing particles
        let flowX = fract(p.x * 3.0 - time * 0.5 + fi * 0.25);
        let flowPulse = smoothstep(0.0, 0.5, flowX) * smoothstep(1.0, 0.5, flowX);

        let riverColor = vec3<f32>(0.3, 0.7, 1.0);
        col = col + riverColor * river * (0.5 + flowPulse * 0.5);
    }

    return col;
}

fn drawVortex(p: vec2<f32>, center: vec2<f32>, time: f32, intensity: f32) -> vec3<f32> {
    var col = vec3<f32>(0.0);

    let vp = p - center;
    let dist = length(vp);
    let angle = atan2(vp.y, vp.x);

    // Spiral arms
    let spiralAngle = angle + dist * 10.0 - time * 2.0;
    let spiral = 0.5 + 0.5 * sin(spiralAngle * 3.0);

    let vortexIntensity = smoothstep(0.15, 0.0, dist) * spiral * intensity;
    let vortexColor = vec3<f32>(0.5, 0.3, 0.8);
    col = col + vortexColor * vortexIntensity;

    // Central glow
    let centralGlow = smoothstep(0.08, 0.0, dist) * intensity;
    col = col + vec3<f32>(0.7, 0.5, 1.0) * centralGlow * 0.5;

    return col;
}

// === COLOSSAL ORGANISM ===

fn drawOrganismOutline(p: vec2<f32>, scale: f32, visibility: f32, time: f32) -> vec3<f32> {
    var col = vec3<f32>(0.0);

    // Scale coordinates
    let sp = p / scale;

    // Organic boundary (wavy circle)
    let dist = length(sp);
    let waveAngle = atan2(sp.y, sp.x);
    let wave = 0.7 + 0.1 * sin(waveAngle * 6.0 + time * 0.5);

    let boundaryDist = abs(dist - wave);
    let boundary = smoothstep(0.02 / scale, 0.0, boundaryDist) * visibility;

    // Bioluminescent color
    let bioColor = mix(
        vec3<f32>(0.3, 0.6, 0.8),
        vec3<f32>(0.5, 0.8, 0.6),
        0.5 + 0.5 * sin(waveAngle * 3.0 + time)
    );

    col = col + bioColor * boundary;

    // Internal veins
    for (var i = 0; i < 8; i = i + 1) {
        let fi = f32(i);
        let veinAngle = fi * 3.14159 * 2.0 / 8.0;
        let veinDir = vec2<f32>(cos(veinAngle), sin(veinAngle));

        let veinP = sp - veinDir * 0.3;
        let veinDist = sdLine(sp, vec2<f32>(0.0), veinDir * wave * 0.9, 0.008 / scale);
        let vein = smoothstep(0.015 / scale, 0.0, veinDist) * visibility * 0.5;
        col = col + bioColor * vein;
    }

    // Breathing pulse
    let pulse = 0.5 + 0.3 * sin(time * 1.5);
    let innerGlow = smoothstep(wave, 0.0, dist) * visibility * pulse * 0.2;
    col = col + bioColor * innerGlow;

    return col;
}

// === PHASE RENDERERS ===

fn renderPhase1(uv: vec2<f32>, progress: f32) -> vec3<f32> {
    // White flash reset
    let phaseProgress = remap(progress, 0.0, 0.10, 0.0, 1.0);

    // Flash peaks at 50% then fades
    var intensity: f32;
    if (phaseProgress < 0.5) {
        intensity = easeOutQuart(phaseProgress * 2.0);
    } else {
        intensity = 1.0 - easeInQuad((phaseProgress - 0.5) * 2.0);
    }

    return vec3<f32>(1.0) * intensity;
}

fn renderPhase2(p: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    // Sacred geometry rune draws itself
    let phaseProgress = remap(progress, 0.10, 0.30, 0.0, 1.0);

    // Fade in background
    var col = vec3<f32>(0.02, 0.03, 0.05) * phaseProgress;

    // Draw the rune
    col = col + drawSacredRune(p, phaseProgress, time);

    return col;
}

fn renderPhase3(p: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    // OS city rises
    let phaseProgress = remap(progress, 0.25, 0.60, 0.0, 1.0);

    // Background
    var col = vec3<f32>(0.02, 0.03, 0.06);

    // Keep faint rune
    col = col + drawSacredRune(p, 1.0, time) * 0.2;

    // 12 towers at various positions
    let towerPositions = array<vec2<f32>, 12>(
        vec2<f32>(-0.6, 0.0), vec2<f32>(-0.4, 0.1), vec2<f32>(-0.2, -0.05),
        vec2<f32>(0.0, 0.15), vec2<f32>(0.2, 0.0), vec2<f32>(0.4, 0.1),
        vec2<f32>(0.6, -0.05), vec2<f32>(-0.5, -0.2), vec2<f32>(-0.1, -0.15),
        vec2<f32>(0.1, -0.2), vec2<f32>(0.3, -0.1), vec2<f32>(0.5, -0.15)
    );

    let towerHeights = array<f32, 12>(
        0.3, 0.25, 0.35, 0.4, 0.28, 0.32,
        0.27, 0.22, 0.38, 0.3, 0.25, 0.33
    );

    for (var i = 0; i < 12; i = i + 1) {
        let towerDelay = f32(i) * 0.05;
        let towerProgress = remap(phaseProgress, towerDelay, towerDelay + 0.4, 0.0, 1.0);
        col = col + drawTower(p, towerPositions[i], towerHeights[i], 0.025, easeOutQuart(towerProgress));
    }

    // 8 plazas
    let plazaPositions = array<vec2<f32>, 8>(
        vec2<f32>(-0.5, 0.05), vec2<f32>(-0.1, 0.1), vec2<f32>(0.3, 0.05),
        vec2<f32>(0.55, 0.0), vec2<f32>(-0.3, -0.15), vec2<f32>(0.0, -0.1),
        vec2<f32>(0.25, -0.18), vec2<f32>(0.5, -0.12)
    );

    for (var i = 0; i < 8; i = i + 1) {
        let plazaProgress = remap(phaseProgress, 0.2, 0.6, 0.0, 1.0);
        col = col + drawPlaza(p, plazaPositions[i], 0.06, easeOutQuart(plazaProgress));
    }

    // 6 bridges
    let bridgeStarts = array<vec2<f32>, 6>(
        vec2<f32>(-0.5, 0.05), vec2<f32>(-0.1, 0.1), vec2<f32>(0.3, 0.05),
        vec2<f32>(-0.3, -0.15), vec2<f32>(0.0, -0.1), vec2<f32>(0.25, -0.18)
    );
    let bridgeEnds = array<vec2<f32>, 6>(
        vec2<f32>(-0.1, 0.1), vec2<f32>(0.3, 0.05), vec2<f32>(0.55, 0.0),
        vec2<f32>(0.0, -0.1), vec2<f32>(0.25, -0.18), vec2<f32>(0.5, -0.12)
    );

    for (var i = 0; i < 6; i = i + 1) {
        let bridgeDelay = 0.3 + f32(i) * 0.08;
        let bridgeProgress = remap(phaseProgress, bridgeDelay, bridgeDelay + 0.3, 0.0, 1.0);
        col = col + drawBridge(p, bridgeStarts[i], bridgeEnds[i], easeOutQuart(bridgeProgress));
    }

    // Data rivers
    let riverProgress = remap(phaseProgress, 0.4, 0.8, 0.0, 1.0);
    col = col + drawDataRiver(p, time, easeOutQuart(riverProgress));

    // 4 vortices at cardinal points
    let vortexPositions = array<vec2<f32>, 4>(
        vec2<f32>(0.0, 0.5), vec2<f32>(0.0, -0.5),
        vec2<f32>(0.7, 0.0), vec2<f32>(-0.7, 0.0)
    );

    for (var i = 0; i < 4; i = i + 1) {
        let vortexProgress = remap(phaseProgress, 0.5, 0.9, 0.0, 1.0);
        col = col + drawVortex(p, vortexPositions[i], time, easeOutQuart(vortexProgress));
    }

    return col;
}

fn renderPhase4(p: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    // Camera pulls back - reveal colossal organism
    let phaseProgress = remap(progress, 0.55, 0.85, 0.0, 1.0);

    // Zoom out effect
    let scale = 1.0 + phaseProgress * 1.5;
    let zoomedP = p * scale;

    // Render city at smaller scale
    var col = renderPhase3(zoomedP, 0.60, time) * (1.0 - phaseProgress * 0.3);

    // Organism outline emerges
    col = col + drawOrganismOutline(p, 1.0 + phaseProgress * 0.5, easeOutQuart(phaseProgress), time);

    return col;
}

fn renderPhase5(p: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    // Final state - "The Impossible is Now Operational"
    let phaseProgress = remap(progress, 0.80, 1.0, 0.0, 1.0);

    // Full organism view
    let scale = 2.5;
    let zoomedP = p * scale;

    // Background
    var col = vec3<f32>(0.02, 0.03, 0.05);

    // City at small scale inside organism
    col = col + renderPhase3(zoomedP, 0.60, time) * 0.5;

    // Full organism
    col = col + drawOrganismOutline(p, 1.5, 1.0, time);

    // Final radiant state
    let finalGlow = easeOutQuart(phaseProgress);
    let dist = length(p);

    // Radiant halo
    let haloRadius = 0.8;
    let haloDist = abs(dist - haloRadius);
    let halo = smoothstep(0.05, 0.0, haloDist) * finalGlow;
    col = col + vec3<f32>(0.8, 0.9, 1.0) * halo;

    // Central brilliance
    let centralBrilliance = smoothstep(0.5, 0.0, dist) * finalGlow * 0.4;
    col = col + vec3<f32>(0.9, 0.95, 1.0) * centralBrilliance;

    // Pulsing "operational" indicator
    let operationalPulse = 0.7 + 0.3 * sin(time * 3.0);
    let operationalGlow = smoothstep(0.15, 0.0, dist) * finalGlow * operationalPulse;
    col = col + vec3<f32>(1.0, 0.95, 0.9) * operationalGlow;

    return col;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let progress = uniforms.progress;
    let time = uniforms.time;

    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    var p = (in.uv * 2.0 - 1.0);
    p.x = p.x * aspect;

    var col = vec3<f32>(0.0);

    // Phase transitions
    if (progress < 0.10) {
        col = renderPhase1(in.uv, progress);
    } else if (progress < 0.25) {
        let blend = remap(progress, 0.10, 0.15, 0.0, 1.0);
        let phase1 = renderPhase1(in.uv, 0.10);
        let phase2 = renderPhase2(p, progress, time);
        col = mix(phase1, phase2, easeInOutCubic(blend));
    } else if (progress < 0.55) {
        let blend = remap(progress, 0.25, 0.30, 0.0, 1.0);
        let phase2 = renderPhase2(p, 0.30, time);
        let phase3 = renderPhase3(p, progress, time);
        col = mix(phase2, phase3, easeInOutCubic(blend));
    } else if (progress < 0.80) {
        let blend = remap(progress, 0.55, 0.60, 0.0, 1.0);
        let phase3 = renderPhase3(p, 0.60, time);
        let phase4 = renderPhase4(p, progress, time);
        col = mix(phase3, phase4, easeInOutCubic(blend));
    } else {
        let blend = remap(progress, 0.80, 0.85, 0.0, 1.0);
        let phase4 = renderPhase4(p, 0.85, time);
        let phase5 = renderPhase5(p, progress, time);
        col = mix(phase4, phase5, easeInOutCubic(blend));
    }

    // Vignette
    let vignette = 1.0 - length(in.uv - 0.5) * 0.5;
    col = col * vignette;

    // Tone mapping
    col = col / (col + vec3<f32>(1.0));
    col = pow(col, vec3<f32>(1.0 / 2.2));

    return vec4<f32>(col, 1.0);
}
