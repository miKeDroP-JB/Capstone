// THE FOLDING WORLD
// 3iAtlas Navigation - "What was distant is now near."
//
// A non-Euclidean knowledge topology where:
// - Ideas rise as mountains
// - Problems form canyons of complexity
// - Insights shimmer as rivers of pattern
// - Creative leaps spread as auroras across the sky
//
// Interactive Parameters:
// parameters[0] = zoom (0.5 - 2.0)
// parameters[1] = fold_intensity (0.0 - 1.0)
// parameters[2] = focus_x (-1.0 - 1.0)
// parameters[3] = focus_y (-1.0 - 1.0)
// parameters[4] = flow_speed (0.0 - 2.0)
// parameters[5] = aurora_intensity (0.0 - 1.0)
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

fn fbm(p: vec2<f32>, octaves: i32) -> f32 {
    var value = 0.0;
    var amplitude = 0.5;
    var pos = p;
    for (var i = 0; i < octaves; i = i + 1) {
        value = value + amplitude * noise(pos);
        pos = pos * 2.0;
        amplitude = amplitude * 0.5;
    }
    return value;
}

fn voronoi(p: vec2<f32>) -> vec2<f32> {
    let n = floor(p);
    let f = fract(p);

    var minDist = 1.0;
    var minPoint = vec2<f32>(0.0);

    for (var j = -1; j <= 1; j = j + 1) {
        for (var i = -1; i <= 1; i = i + 1) {
            let g = vec2<f32>(f32(i), f32(j));
            let o = hash2(n + g);
            let r = g + o - f;
            let d = dot(r, r);
            if (d < minDist) {
                minDist = d;
                minPoint = n + g + o;
            }
        }
    }

    return vec2<f32>(sqrt(minDist), hash(minPoint));
}

// === FOLDING TRANSFORMATION ===

fn applyFold(p: vec2<f32>, foldIntensity: f32, focusX: f32, focusY: f32, time: f32) -> vec2<f32> {
    var folded = p;

    // Focus point offset
    let focus = vec2<f32>(focusX, focusY);
    folded = folded - focus;

    // Non-Euclidean warping
    let dist = length(folded);
    let angle = atan2(folded.y, folded.x);

    // Origami-like folding
    let foldWave = sin(dist * 5.0 - time * 0.5) * foldIntensity * 0.3;
    let rotationTwist = foldIntensity * sin(dist * 3.0) * 0.5;

    let newAngle = angle + rotationTwist;
    let newDist = dist * (1.0 + foldWave);

    folded = vec2<f32>(cos(newAngle), sin(newAngle)) * newDist;

    // Space compression (what was distant is now near)
    let compression = 1.0 - foldIntensity * 0.3 * smoothstep(0.5, 1.5, dist);
    folded = folded * compression;

    folded = folded + focus;

    return folded;
}

// === TERRAIN GENERATION ===

// Mountains (ideas)
fn mountainHeight(p: vec2<f32>) -> f32 {
    var height = 0.0;

    // 5 mountain peaks at fixed positions
    let peaks = array<vec2<f32>, 5>(
        vec2<f32>(0.3, 0.4),
        vec2<f32>(-0.5, 0.2),
        vec2<f32>(0.6, -0.3),
        vec2<f32>(-0.2, -0.5),
        vec2<f32>(0.0, 0.6)
    );

    let peakHeights = array<f32, 5>(0.7, 0.5, 0.6, 0.4, 0.55);

    for (var i = 0; i < 5; i = i + 1) {
        let dist = length(p - peaks[i]);
        let peak = peakHeights[i] * smoothstep(0.4, 0.0, dist);
        height = max(height, peak);
    }

    // Add FBM detail
    height = height + fbm(p * 4.0, 4) * 0.15;

    return height;
}

// Canyons (problems)
fn canyonDepth(p: vec2<f32>) -> f32 {
    var depth = 0.0;

    // 3 canyon lines
    let canyons = array<vec4<f32>, 3>(
        vec4<f32>(-0.8, 0.0, 0.8, -0.2),   // start.xy, end.xy
        vec4<f32>(0.0, 0.7, 0.3, -0.6),
        vec4<f32>(-0.5, -0.4, 0.6, 0.1)
    );

    let canyonWidths = array<f32, 3>(0.08, 0.06, 0.07);
    let canyonDepths = array<f32, 3>(0.5, 0.4, 0.45);

    for (var i = 0; i < 3; i = i + 1) {
        let a = canyons[i].xy;
        let b = canyons[i].zw;

        let pa = p - a;
        let ba = b - a;
        let h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
        let dist = length(pa - ba * h);

        let canyon = canyonDepths[i] * smoothstep(canyonWidths[i], 0.0, dist);
        depth = max(depth, canyon);
    }

    return depth;
}

// Rivers (insights)
fn riverFlow(p: vec2<f32>, time: f32, flowSpeed: f32) -> f32 {
    // Rivers flow through low terrain
    let terrain = mountainHeight(p) - canyonDepth(p);

    // River path follows valleys
    var riverIntensity = 0.0;

    // Multiple river channels
    for (var i = 0; i < 3; i = i + 1) {
        let fi = f32(i);

        // Winding river path
        let riverY = p.y + sin(p.x * 3.0 + fi * 2.0) * 0.2;
        let riverPath = abs(riverY - (fi - 1.0) * 0.3);

        // River flows in low terrain
        let inValley = smoothstep(0.3, 0.0, terrain);
        let riverWidth = 0.03 + inValley * 0.02;

        let river = smoothstep(riverWidth, 0.0, riverPath) * inValley;

        // Shimmer animation
        let shimmer = 0.7 + 0.3 * sin(p.x * 20.0 - time * flowSpeed * 3.0 + fi);
        riverIntensity = max(riverIntensity, river * shimmer);
    }

    // FBM flow pattern
    let flowNoise = fbm(p * 8.0 + vec2<f32>(time * flowSpeed * 0.5, 0.0), 3);
    riverIntensity = riverIntensity * (0.7 + flowNoise * 0.3);

    return riverIntensity;
}

// Auroras (creative leaps)
fn auroraIntensity(p: vec2<f32>, time: f32, intensity: f32) -> vec3<f32> {
    // Auroras appear in upper atmosphere
    let atmosphereMask = smoothstep(-0.2, 0.8, p.y);

    // Flowing curtain effect
    var aurora = vec3<f32>(0.0);

    let auroraY = p.y + fbm(vec2<f32>(p.x * 2.0 + time * 0.3, time * 0.1), 4) * 0.3;
    let curtain = smoothstep(0.1, 0.0, abs(auroraY - 0.5));

    // Color cycling
    let hueShift = p.x * 0.5 + time * 0.2;
    let auroraColor = vec3<f32>(
        0.3 + 0.3 * sin(hueShift),
        0.6 + 0.2 * sin(hueShift + 2.094),
        0.4 + 0.4 * sin(hueShift + 4.188)
    );

    aurora = auroraColor * curtain * atmosphereMask * intensity;

    // Secondary aurora layer
    let aurora2Y = p.y + fbm(vec2<f32>(p.x * 3.0 - time * 0.2, time * 0.15 + 5.0), 4) * 0.25;
    let curtain2 = smoothstep(0.08, 0.0, abs(aurora2Y - 0.6));
    let color2 = vec3<f32>(0.2, 0.8, 0.5);
    aurora = aurora + color2 * curtain2 * atmosphereMask * intensity * 0.5;

    return aurora;
}

// === MAIN RENDERER ===

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let time = uniforms.time;

    // Extract parameters
    let zoom = uniforms.parameters[0];
    let foldIntensity = uniforms.parameters[1];
    let focusX = uniforms.parameters[2];
    let focusY = uniforms.parameters[3];
    let flowSpeed = uniforms.parameters[4];
    let auroraLevel = uniforms.parameters[5];

    // Base coordinates
    let aspect = uniforms.resolution.x / uniforms.resolution.y;
    var p = (in.uv * 2.0 - 1.0);
    p.x = p.x * aspect;

    // Apply zoom
    p = p / zoom;

    // Apply non-Euclidean folding
    let foldedP = applyFold(p, foldIntensity, focusX, focusY, time);

    // === RENDER LAYERS ===

    // Background: deep space gradient
    var col = mix(
        vec3<f32>(0.02, 0.03, 0.08),
        vec3<f32>(0.05, 0.08, 0.15),
        in.uv.y
    );

    // Terrain height
    let height = mountainHeight(foldedP);
    let depth = canyonDepth(foldedP);
    let elevation = height - depth;

    // Terrain coloring
    let terrainColor = mix(
        vec3<f32>(0.1, 0.15, 0.25), // Valleys - dark blue
        vec3<f32>(0.3, 0.5, 0.7),   // Mid elevation - blue
        smoothstep(-0.2, 0.3, elevation)
    );

    // Mountain peaks glow
    let peakGlow = smoothstep(0.2, 0.5, elevation);
    let mountainColor = mix(
        terrainColor,
        vec3<f32>(0.6, 0.85, 1.0), // Brilliant insight peaks
        peakGlow
    );

    // Canyon depths glow (problems have their own light)
    let canyonGlow = smoothstep(0.0, 0.3, depth);
    let canyonColor = vec3<f32>(0.5, 0.2, 0.6); // Purple/magenta
    let finalTerrainColor = mix(mountainColor, canyonColor, canyonGlow * 0.6);

    // Apply terrain
    col = mix(col, finalTerrainColor, 0.8);

    // Contour lines (knowledge strata)
    let contourSpacing = 0.1;
    let contourLine = abs(fract(elevation / contourSpacing) - 0.5) * 2.0;
    let contour = smoothstep(0.1, 0.0, contourLine) * 0.15;
    col = col + vec3<f32>(0.3, 0.5, 0.8) * contour;

    // Rivers (insight flows)
    let river = riverFlow(foldedP, time, flowSpeed);
    let riverColor = vec3<f32>(0.4, 0.8, 1.0);
    col = mix(col, riverColor, river * 0.8);

    // River glow
    col = col + riverColor * river * 0.3;

    // Auroras (creative leaps)
    let aurora = auroraIntensity(foldedP, time, auroraLevel);
    col = col + aurora;

    // Grid overlay when folding is active (shows underlying structure)
    if (foldIntensity > 0.3) {
        let gridIntensity = (foldIntensity - 0.3) / 0.7;

        // Original space grid
        let gridSpacing = 0.2;
        let gridX = abs(fract(p.x / gridSpacing) - 0.5) * 2.0;
        let gridY = abs(fract(p.y / gridSpacing) - 0.5) * 2.0;
        let grid = min(
            smoothstep(0.05, 0.0, gridX),
            smoothstep(0.05, 0.0, gridY)
        );

        // Folded space grid
        let foldedGridX = abs(fract(foldedP.x / gridSpacing) - 0.5) * 2.0;
        let foldedGridY = abs(fract(foldedP.y / gridSpacing) - 0.5) * 2.0;
        let foldedGrid = max(
            smoothstep(0.03, 0.0, foldedGridX),
            smoothstep(0.03, 0.0, foldedGridY)
        );

        col = col + vec3<f32>(0.2, 0.4, 0.6) * grid * gridIntensity * 0.3;
        col = col + vec3<f32>(0.4, 0.6, 0.8) * foldedGrid * gridIntensity * 0.2;
    }

    // Voronoi cells for knowledge domains
    let vor = voronoi(foldedP * 3.0);
    let cellEdge = smoothstep(0.1, 0.05, vor.x);
    col = col + vec3<f32>(0.2, 0.3, 0.5) * cellEdge * 0.15;

    // Luminous possibility trees (sprouting in high-fold areas)
    if (foldIntensity > 0.5) {
        let treeIntensity = (foldIntensity - 0.5) / 0.5;

        for (var i = 0; i < 8; i = i + 1) {
            let fi = f32(i);
            let treePos = vec2<f32>(
                hash(vec2<f32>(fi, 0.0)) * 2.0 - 1.0,
                hash(vec2<f32>(0.0, fi)) * 1.5 - 0.5
            );

            let treeDist = length(foldedP - treePos);
            let treeGlow = smoothstep(0.15, 0.0, treeDist);

            // Tree trunk
            let trunkX = abs(foldedP.x - treePos.x);
            let trunkY = foldedP.y - treePos.y;
            if (trunkY > 0.0 && trunkY < 0.2 && trunkX < 0.01) {
                col = col + vec3<f32>(0.4, 0.6, 0.3) * treeIntensity * 0.5;
            }

            // Tree canopy
            let canopyCenter = treePos + vec2<f32>(0.0, 0.15);
            let canopyDist = length(foldedP - canopyCenter);
            let canopy = smoothstep(0.08, 0.02, canopyDist);
            col = col + vec3<f32>(0.5, 1.0, 0.6) * canopy * treeIntensity * 0.6;
        }
    }

    // Vignette
    let vignette = 1.0 - length(in.uv - 0.5) * 0.8;
    col = col * vignette;

    // Tone mapping
    col = col / (col + vec3<f32>(1.0));
    col = pow(col, vec3<f32>(1.0 / 2.2));

    return vec4<f32>(col, 1.0);
}
