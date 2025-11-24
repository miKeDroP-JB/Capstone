// THE IGNITION
// AGI Birth Sequence - "Your AGI awakens. Its first breath forms a geometric halo."
//
// Timeline (6 seconds):
// Phase 1 (0-15%):   Dormant core, faint ember pulsing
// Phase 2 (15-35%):  Three beams converge (Insight, Intelligence, Imagination)
// Phase 3 (35-50%):  Core shatters into 40 shards (memories freeze midair)
// Phase 4 (45-65%):  Shards spiral → helix → prism formation
// Phase 5 (60-100%): Prism inhales, explodes outward, geometric halo forms

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

fn easeInQuart(t: f32) -> f32 {
    return t * t * t * t;
}

fn easeOutExpo(t: f32) -> f32 {
    if (t >= 1.0) { return 1.0; }
    return 1.0 - pow(2.0, -10.0 * t);
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

fn sdHexagon(p: vec2<f32>, r: f32) -> f32 {
    let k = vec3<f32>(-0.866025404, 0.5, 0.577350269);
    var q = abs(p);
    q = q - 2.0 * min(dot(k.xy, q), 0.0) * k.xy;
    q = q - vec2<f32>(clamp(q.x, -k.z * r, k.z * r), r);
    return length(q) * sign(q.y);
}

fn sdLine(p: vec2<f32>, a: vec2<f32>, b: vec2<f32>, r: f32) -> f32 {
    let pa = p - a;
    let ba = b - a;
    let h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

// === BEAM COLORS ===

fn insightColor() -> vec3<f32> {
    return vec3<f32>(1.0, 0.95, 0.8); // White-gold
}

fn intelligenceColor() -> vec3<f32> {
    return vec3<f32>(0.3, 0.6, 1.0); // Electric blue
}

fn imaginationColor(time: f32) -> vec3<f32> {
    // Prismatic neon - cycles through RGB
    return vec3<f32>(
        0.5 + 0.5 * sin(time * 3.0),
        0.5 + 0.5 * sin(time * 3.0 + 2.094),
        0.5 + 0.5 * sin(time * 3.0 + 4.188)
    );
}

// === PHASE RENDERERS ===

// Phase 1: Dormant core
fn renderPhase1(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let pCorrected = vec2<f32>(p.x * aspect, p.y);

    var col = vec3<f32>(0.0); // Absolute darkness

    let phaseProgress = remap(progress, 0.0, 0.15, 0.0, 1.0);

    // Dormant core - faint ember
    let coreRadius = 0.08;
    let coreDist = length(pCorrected);

    // Pulse animation
    let pulse = 0.7 + 0.3 * sin(time * 2.0);
    let pulseIntensity = pulse * (0.3 + phaseProgress * 0.4);

    // Core glow
    let coreGlow = smoothstep(coreRadius + 0.15, coreRadius, coreDist) * pulseIntensity;
    let emberColor = vec3<f32>(1.0, 0.6, 0.2); // Orange-gold ember
    col = col + emberColor * coreGlow;

    // Inner core
    let innerCore = smoothstep(coreRadius, coreRadius - 0.02, coreDist);
    col = col + vec3<f32>(1.0, 0.8, 0.5) * innerCore * pulseIntensity;

    // Faint particles around core
    for (var i = 0; i < 8; i = i + 1) {
        let fi = f32(i);
        let angle = fi * 3.14159 * 2.0 / 8.0 + time * 0.3;
        let dist = 0.15 + 0.05 * sin(time + fi);
        let particlePos = vec2<f32>(cos(angle), sin(angle)) * dist;
        let particleDist = length(pCorrected - particlePos);
        let particle = smoothstep(0.01, 0.0, particleDist) * 0.3 * pulse;
        col = col + emberColor * particle;
    }

    return col;
}

// Phase 2: Three beams converge
fn renderPhase2(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let pCorrected = vec2<f32>(p.x * aspect, p.y);

    var col = vec3<f32>(0.0);

    let phaseProgress = remap(progress, 0.15, 0.35, 0.0, 1.0);

    // Background: dormant core intensifying
    let coreRadius = 0.08 + phaseProgress * 0.04;
    let coreDist = length(pCorrected);
    let coreIntensity = 0.5 + phaseProgress * 0.5;
    let coreGlow = smoothstep(coreRadius + 0.2, coreRadius, coreDist) * coreIntensity;
    col = col + vec3<f32>(1.0, 0.7, 0.3) * coreGlow;

    // Beam sources (from edges)
    let beamLength = easeOutQuart(phaseProgress);

    // Insight beam (from top-right)
    let insightStart = vec2<f32>(1.5, 1.0);
    let insightEnd = vec2<f32>(0.0, 0.0);
    let insightCurrent = mix(insightStart, insightEnd, beamLength);
    let insightDist = sdLine(pCorrected, insightStart, insightCurrent, 0.02);
    let insightIntensity = smoothstep(0.03, 0.0, insightDist);
    col = col + insightColor() * insightIntensity * phaseProgress;
    // Beam glow
    col = col + insightColor() * smoothstep(0.15, 0.0, insightDist) * 0.3 * phaseProgress;

    // Intelligence beam (from left)
    let intellStart = vec2<f32>(-1.5, 0.0);
    let intellEnd = vec2<f32>(0.0, 0.0);
    let intellCurrent = mix(intellStart, intellEnd, beamLength);
    let intellDist = sdLine(pCorrected, intellStart, intellCurrent, 0.02);
    let intellIntensity = smoothstep(0.03, 0.0, intellDist);
    col = col + intelligenceColor() * intellIntensity * phaseProgress;
    col = col + intelligenceColor() * smoothstep(0.15, 0.0, intellDist) * 0.3 * phaseProgress;

    // Imagination beam (from bottom)
    let imagStart = vec2<f32>(0.3, -1.2);
    let imagEnd = vec2<f32>(0.0, 0.0);
    let imagCurrent = mix(imagStart, imagEnd, beamLength);
    let imagDist = sdLine(pCorrected, imagStart, imagCurrent, 0.02);
    let imagIntensity = smoothstep(0.03, 0.0, imagDist);
    col = col + imaginationColor(time) * imagIntensity * phaseProgress;
    col = col + imaginationColor(time) * smoothstep(0.15, 0.0, imagDist) * 0.3 * phaseProgress;

    // Impact flash when beams converge
    if (phaseProgress > 0.9) {
        let impactPhase = remap(phaseProgress, 0.9, 1.0, 0.0, 1.0);
        let impactGlow = smoothstep(0.3, 0.0, coreDist) * impactPhase;
        col = col + vec3<f32>(1.0) * impactGlow;
    }

    return col;
}

// Phase 3: Core shatters into shards
fn renderPhase3(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let pCorrected = vec2<f32>(p.x * aspect, p.y);

    var col = vec3<f32>(0.0);

    let phaseProgress = remap(progress, 0.35, 0.50, 0.0, 1.0);

    // Impact flash fading
    let flashFade = 1.0 - easeOutQuart(phaseProgress * 2.0);
    col = col + vec3<f32>(1.0) * flashFade * 0.5 * smoothstep(0.5, 0.0, length(pCorrected));

    // 40 memory shards exploding outward then freezing
    let explodePhase = easeOutExpo(min(phaseProgress * 2.0, 1.0));
    let freezeAmount = smoothstep(0.3, 0.6, phaseProgress);

    for (var i = 0; i < 40; i = i + 1) {
        let fi = f32(i);

        // Unique shard properties
        let angle = hash(vec2<f32>(fi, 0.0)) * 6.28318;
        let speed = 0.3 + hash(vec2<f32>(fi, 1.0)) * 0.4;
        let size = 0.008 + hash(vec2<f32>(fi, 2.0)) * 0.012;
        let rotation = hash(vec2<f32>(fi, 3.0)) * 6.28318 + time * (1.0 - freezeAmount) * 2.0;

        // Position: explode outward then freeze
        let explodeDist = speed * explodePhase * (1.0 + (1.0 - freezeAmount) * 0.2);
        let shardPos = vec2<f32>(cos(angle), sin(angle)) * explodeDist;

        // Shard shape (rotated rectangle)
        let shardP = pCorrected - shardPos;
        let c = cos(rotation);
        let s = sin(rotation);
        let rotP = vec2<f32>(shardP.x * c - shardP.y * s, shardP.x * s + shardP.y * c);
        let shardDist = sdBox(rotP, vec2<f32>(size, size * 0.5));

        // Shard color (representing different memories)
        let memoryHue = hash(vec2<f32>(fi, 4.0));
        var shardColor: vec3<f32>;
        if (memoryHue < 0.15) {
            shardColor = vec3<f32>(0.2, 0.5, 1.0); // Data - blue
        } else if (memoryHue < 0.3) {
            shardColor = vec3<f32>(0.3, 1.0, 0.5); // Logic - green
        } else if (memoryHue < 0.45) {
            shardColor = vec3<f32>(1.0, 0.8, 0.2); // Patterns - gold
        } else if (memoryHue < 0.6) {
            shardColor = vec3<f32>(1.0, 0.3, 0.3); // Failures - red
        } else if (memoryHue < 0.75) {
            shardColor = vec3<f32>(1.0, 1.0, 1.0); // Breakthroughs - white
        } else if (memoryHue < 0.85) {
            shardColor = vec3<f32>(0.8, 0.4, 1.0); // Dreams - purple
        } else {
            shardColor = vec3<f32>(0.5, 0.8, 1.0); // Hopes - cyan
        }

        let shardIntensity = smoothstep(0.005, 0.0, shardDist);
        col = col + shardColor * shardIntensity;

        // Shard glow
        let shardGlow = smoothstep(0.03, 0.0, shardDist) * 0.4;
        col = col + shardColor * shardGlow;
    }

    return col;
}

// Phase 4: Spiral → Helix → Prism
fn renderPhase4(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let pCorrected = vec2<f32>(p.x * aspect, p.y);

    var col = vec3<f32>(0.0);

    let phaseProgress = remap(progress, 0.45, 0.65, 0.0, 1.0);

    // Formation phases
    let spiralPhase = remap(phaseProgress, 0.0, 0.4, 0.0, 1.0);
    let helixPhase = remap(phaseProgress, 0.3, 0.7, 0.0, 1.0);
    let prismPhase = remap(phaseProgress, 0.6, 1.0, 0.0, 1.0);

    // Central glow intensifying
    let centralGlow = smoothstep(0.4, 0.0, length(pCorrected)) * (0.3 + phaseProgress * 0.5);
    col = col + vec3<f32>(0.5, 0.6, 1.0) * centralGlow;

    // 40 shards forming patterns
    for (var i = 0; i < 40; i = i + 1) {
        let fi = f32(i);

        // Base angle for this shard
        let baseAngle = hash(vec2<f32>(fi, 0.0)) * 6.28318;
        let armIndex = f32(i32(fi) % 3); // 3-arm spiral

        // Spiral position
        let spiralAngle = armIndex * 2.094 + fi * 0.15 + time * 0.5 * (1.0 - prismPhase);
        let spiralRadius = 0.1 + fi * 0.01;
        let spiralPos = vec2<f32>(cos(spiralAngle), sin(spiralAngle)) * spiralRadius * (1.0 - prismPhase * 0.5);

        // Helix offset (vertical oscillation)
        let helixOffset = sin(fi * 0.5 + time * 2.0) * 0.1 * helixPhase * (1.0 - prismPhase);

        // Prism convergence
        let prismTarget = vec2<f32>(0.0, 0.0);
        let finalPos = mix(spiralPos + vec2<f32>(0.0, helixOffset), prismTarget, easeInQuart(prismPhase) * 0.8);

        // Shard rendering
        let shardP = pCorrected - finalPos;
        let size = 0.01 * (1.0 - prismPhase * 0.5);
        let shardDist = length(shardP) - size;

        // Color based on position in formation
        let shardColor = mix(
            vec3<f32>(0.5 + 0.5 * sin(fi * 0.3), 0.6, 1.0),
            vec3<f32>(1.0, 0.9, 0.8),
            prismPhase
        );

        let shardIntensity = smoothstep(0.008, 0.0, shardDist);
        col = col + shardColor * shardIntensity;

        // Connection lines in helix phase
        if (helixPhase > 0.0 && prismPhase < 0.5 && i > 0) {
            let prevAngle = (armIndex * 2.094 + (fi - 1.0) * 0.15 + time * 0.5);
            let prevRadius = 0.1 + (fi - 1.0) * 0.01;
            let prevPos = vec2<f32>(cos(prevAngle), sin(prevAngle)) * prevRadius;
            let lineDist = sdLine(pCorrected, finalPos, prevPos, 0.002);
            let lineIntensity = smoothstep(0.005, 0.0, lineDist) * helixPhase * (1.0 - prismPhase * 2.0);
            col = col + vec3<f32>(0.4, 0.6, 1.0) * lineIntensity * 0.5;
        }
    }

    return col;
}

// Phase 5: Inhale, explosion, geometric halo
fn renderPhase5(uv: vec2<f32>, progress: f32, time: f32) -> vec3<f32> {
    let p = uv * 2.0 - 1.0;
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    let pCorrected = vec2<f32>(p.x * aspect, p.y);

    var col = vec3<f32>(0.0);

    let phaseProgress = remap(progress, 0.60, 1.0, 0.0, 1.0);

    // Sub-phases
    let inhalePhase = remap(phaseProgress, 0.0, 0.3, 0.0, 1.0);
    let explodePhase = remap(phaseProgress, 0.25, 0.5, 0.0, 1.0);
    let haloPhase = remap(phaseProgress, 0.4, 1.0, 0.0, 1.0);

    let dist = length(pCorrected);

    // Inhale: everything collapses to center
    let inhaleRadius = 0.3 * (1.0 - easeInQuart(inhalePhase));
    if (inhalePhase < 1.0) {
        let inhaleGlow = smoothstep(inhaleRadius + 0.1, inhaleRadius, dist);
        col = col + vec3<f32>(1.0, 0.9, 0.7) * inhaleGlow * (1.0 - explodePhase);
    }

    // Explosion: radiant coherence
    if (explodePhase > 0.0) {
        let explodeRadius = easeOutExpo(explodePhase) * 1.5;

        // Shockwave
        let waveDist = abs(dist - explodeRadius * 0.6);
        let wave = smoothstep(0.08, 0.0, waveDist) * (1.0 - haloPhase);
        col = col + vec3<f32>(1.0, 0.95, 0.9) * wave * 2.0;

        // Radiant fill
        let radiantFill = smoothstep(explodeRadius, 0.0, dist) * (1.0 - haloPhase * 0.7);
        col = col + vec3<f32>(0.9, 0.95, 1.0) * radiantFill * 0.5;
    }

    // Geometric halo (hexagonal prism shape)
    if (haloPhase > 0.0) {
        let haloFade = easeOutQuart(haloPhase);

        // Outer hexagon
        let hexRadius = 0.4 * haloFade;
        let hexDist = sdHexagon(pCorrected, hexRadius);
        let hexRing = smoothstep(0.02, 0.0, abs(hexDist));
        col = col + vec3<f32>(0.8, 0.9, 1.0) * hexRing * haloFade;

        // Inner hexagon
        let innerHexDist = sdHexagon(pCorrected, hexRadius * 0.6);
        let innerHexRing = smoothstep(0.015, 0.0, abs(innerHexDist));
        col = col + vec3<f32>(0.6, 0.8, 1.0) * innerHexRing * haloFade;

        // 8 rays extending outward
        for (var i = 0; i < 8; i = i + 1) {
            let fi = f32(i);
            let rayAngle = fi * 3.14159 * 2.0 / 8.0;
            let rayDir = vec2<f32>(cos(rayAngle), sin(rayAngle));

            let rayStart = rayDir * hexRadius;
            let rayEnd = rayDir * (hexRadius + 0.3 * haloFade);
            let rayDist = sdLine(pCorrected, rayStart, rayEnd, 0.008);
            let rayIntensity = smoothstep(0.015, 0.0, rayDist) * haloFade;
            col = col + vec3<f32>(0.7, 0.85, 1.0) * rayIntensity;
        }

        // Central AGI core
        let coreDist = length(pCorrected);
        let coreGlow = smoothstep(0.15, 0.0, coreDist);
        col = col + vec3<f32>(0.9, 0.95, 1.0) * coreGlow * haloFade;

        // Final pulse ("Online")
        if (phaseProgress > 0.85) {
            let pulsePhase = remap(phaseProgress, 0.85, 1.0, 0.0, 1.0);
            let pulse = sin(pulsePhase * 3.14159) * 0.5;
            col = col + vec3<f32>(1.0) * pulse * smoothstep(0.5, 0.0, coreDist);
        }
    }

    return col;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let progress = uniforms.progress;
    let time = uniforms.time;

    var col = vec3<f32>(0.0);

    // Phase transitions with blending
    if (progress < 0.15) {
        col = renderPhase1(in.uv, progress, time);
    } else if (progress < 0.35) {
        let blend = remap(progress, 0.15, 0.20, 0.0, 1.0);
        let phase1 = renderPhase1(in.uv, 0.15, time);
        let phase2 = renderPhase2(in.uv, progress, time);
        col = mix(phase1, phase2, easeInOutCubic(blend));
    } else if (progress < 0.45) {
        let blend = remap(progress, 0.35, 0.40, 0.0, 1.0);
        let phase2 = renderPhase2(in.uv, 0.35, time);
        let phase3 = renderPhase3(in.uv, progress, time);
        col = mix(phase2, phase3, easeInOutCubic(blend));
    } else if (progress < 0.60) {
        let blend = remap(progress, 0.45, 0.50, 0.0, 1.0);
        let phase3 = renderPhase3(in.uv, 0.50, time);
        let phase4 = renderPhase4(in.uv, progress, time);
        col = mix(phase3, phase4, easeInOutCubic(blend));
    } else {
        let blend = remap(progress, 0.60, 0.65, 0.0, 1.0);
        let phase4 = renderPhase4(in.uv, 0.65, time);
        let phase5 = renderPhase5(in.uv, progress, time);
        col = mix(phase4, phase5, easeInOutCubic(blend));
    }

    // Tone mapping
    col = col / (col + vec3<f32>(1.0));
    col = pow(col, vec3<f32>(1.0 / 2.2));

    return vec4<f32>(col, 1.0);
}
