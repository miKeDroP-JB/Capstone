# 3iATLAS
## Developer Technical Specification
### Three.js Implementation Guide

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                     3iATLAS STACK                           │
├─────────────────────────────────────────────────────────────┤
│  PRESENTATION LAYER                                         │
│  ├── Three.js Scene Graph                                   │
│  ├── Custom Shaders (GLSL)                                  │
│  ├── Post-processing Pipeline                               │
│  └── UI Overlay (HTML/CSS)                                  │
├─────────────────────────────────────────────────────────────┤
│  INTERACTION LAYER                                          │
│  ├── Input Manager (Mouse/Touch/Voice/Gesture)              │
│  ├── Camera Controller (Orbit/FirstPerson/Cinematic)        │
│  ├── Raycaster (Selection/Hover)                            │
│  └── Event System                                           │
├─────────────────────────────────────────────────────────────┤
│  SIMULATION LAYER                                           │
│  ├── Graph Layout Engine                                    │
│  ├── Physics (Verlet Integration)                           │
│  ├── Particle Systems                                       │
│  └── Terrain Generator                                      │
├─────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                 │
│  ├── Brain Orchestrator Client                              │
│  ├── WebSocket Connection                                   │
│  ├── State Management                                       │
│  └── Cache/IndexedDB                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## CORE DEPENDENCIES

```json
{
  "dependencies": {
    "three": "^0.160.0",
    "postprocessing": "^6.34.0",
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.92.0",
    "@react-three/postprocessing": "^2.15.0",
    "zustand": "^4.4.0",
    "leva": "^0.9.35",
    "maath": "^0.10.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "vite-plugin-glsl": "^1.2.0",
    "@types/three": "^0.160.0"
  }
}
```

---

## MODULE 1: THE AETHER ORB

### Shader: `aether.frag.glsl`

```glsl
precision highp float;

uniform float uTime;
uniform vec3 uColor;
uniform float uMetalness;
uniform float uRoughness;

varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vUv;

// Perlin noise implementation
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

float snoise(vec3 v) {
    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

    vec3 i  = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);

    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);

    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;

    i = mod289(i);
    vec4 p = permute(permute(permute(
             i.z + vec4(0.0, i1.z, i2.z, 1.0))
           + i.y + vec4(0.0, i1.y, i2.y, 1.0))
           + i.x + vec4(0.0, i1.x, i2.x, 1.0));

    float n_ = 0.142857142857;
    vec3 ns = n_ * D.wyz - D.xzx;

    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);

    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);

    vec4 x = x_ *ns.x + ns.yyyy;
    vec4 y = y_ *ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);

    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);

    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));

    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;

    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);

    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
    p0 *= norm.x;
    p1 *= norm.y;
    p2 *= norm.z;
    p3 *= norm.w;

    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
}

// Fresnel approximation
float fresnel(vec3 viewDir, vec3 normal, float power) {
    return pow(1.0 - max(dot(viewDir, normal), 0.0), power);
}

// Aether field
float aetherField(vec3 p, float time) {
    float noise1 = snoise(p * 2.0 + vec3(time * 0.3));
    float noise2 = snoise(p * 4.0 - vec3(time * 0.2));
    float noise3 = snoise(p * 8.0 + vec3(time * 0.1));

    return noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2;
}

void main() {
    vec3 viewDir = normalize(cameraPosition - vPosition);
    vec3 normal = normalize(vNormal);

    // Base metallic color
    vec3 baseColor = vec3(0.7, 0.75, 0.8); // Silver

    // Aether displacement on surface
    float aether = aetherField(vPosition, uTime);

    // Fresnel for edge glow
    float fresnelFactor = fresnel(viewDir, normal, 3.0);

    // Metallic reflection
    vec3 reflectDir = reflect(-viewDir, normal);
    float specular = pow(max(dot(reflectDir, vec3(0.5, 1.0, 0.5)), 0.0), 32.0);

    // Combine
    vec3 color = baseColor;
    color += vec3(0.2, 0.6, 0.8) * aether * 0.3; // Cyan tint from aether
    color += vec3(1.0) * specular * (1.0 - uRoughness);
    color += vec3(0.3, 0.6, 0.9) * fresnelFactor * 0.5; // Edge glow

    // Tone mapping
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0/2.2));

    gl_FragColor = vec4(color, 1.0);
}
```

### TypeScript: `AetherOrb.ts`

```typescript
import * as THREE from 'three';
import { useFrame, useThree } from '@react-three/fiber';
import { useRef, useMemo } from 'react';

interface AetherOrbProps {
  radius?: number;
  segments?: number;
  position?: [number, number, number];
}

export function AetherOrb({
  radius = 1,
  segments = 128,
  position = [0, 0, 0]
}: AetherOrbProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uColor: { value: new THREE.Color(0.7, 0.75, 0.8) },
    uMetalness: { value: 0.9 },
    uRoughness: { value: 0.1 },
  }), []);

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.elapsedTime;
    }
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.001;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[radius, segments, segments]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={aetherVertexShader}
        fragmentShader={aetherFragmentShader}
        uniforms={uniforms}
      />
    </mesh>
  );
}
```

---

## MODULE 2: PARTICLE SYSTEM

### `ParticleField.ts`

```typescript
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { useRef, useMemo } from 'react';

const PARTICLE_COUNT = 1000;

interface ParticleFieldProps {
  radius?: number;
  color?: THREE.Color;
  speed?: number;
}

export function ParticleField({
  radius = 3,
  color = new THREE.Color(0.2, 0.6, 1.0),
  speed = 1
}: ParticleFieldProps) {
  const pointsRef = useRef<THREE.Points>(null);

  const { positions, velocities } = useMemo(() => {
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const velocities = new Float32Array(PARTICLE_COUNT * 3);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;

      // Spherical distribution
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = radius * (0.8 + Math.random() * 0.4);

      positions[i3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = r * Math.cos(phi);

      // Orbital velocities
      velocities[i3] = (Math.random() - 0.5) * 0.02;
      velocities[i3 + 1] = (Math.random() - 0.5) * 0.02;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.02;
    }

    return { positions, velocities };
  }, [radius]);

  useFrame((state, delta) => {
    if (!pointsRef.current) return;

    const posArray = pointsRef.current.geometry.attributes.position.array as Float32Array;
    const time = state.clock.elapsedTime;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;

      // Update positions with orbital motion
      const x = posArray[i3];
      const y = posArray[i3 + 1];
      const z = posArray[i3 + 2];

      // Orbit around Y axis
      const angle = Math.atan2(z, x) + delta * speed * 0.1;
      const dist = Math.sqrt(x * x + z * z);

      posArray[i3] = Math.cos(angle) * dist + Math.sin(time + i) * 0.01;
      posArray[i3 + 1] = y + Math.cos(time * 2 + i) * 0.005;
      posArray[i3 + 2] = Math.sin(angle) * dist + Math.cos(time + i) * 0.01;
    }

    pointsRef.current.geometry.attributes.position.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={PARTICLE_COUNT}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        color={color}
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}
```

---

## MODULE 3: TERRAIN GENERATOR

### `TerrainFromNetwork.ts`

```typescript
import * as THREE from 'three';
import { useMemo } from 'react';

interface NetworkNode {
  id: string;
  position: [number, number, number];
  connections: string[];
  confidence: number;
}

interface TerrainProps {
  network: NetworkNode[];
  resolution?: number;
  scale?: number;
}

export function TerrainFromNetwork({
  network,
  resolution = 256,
  scale = 10
}: TerrainProps) {

  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(scale, scale, resolution - 1, resolution - 1);
    const positions = geo.attributes.position.array as Float32Array;

    // Create heightmap from network density
    const heightmap = new Float32Array(resolution * resolution);

    // For each network node, add influence to heightmap
    for (const node of network) {
      const [nx, ny, nz] = node.position;

      // Map 3D position to 2D heightmap coordinates
      const hx = Math.floor(((nx + scale/2) / scale) * resolution);
      const hy = Math.floor(((nz + scale/2) / scale) * resolution);

      // Add Gaussian influence
      const sigma = 0.1 * scale;
      const amplitude = node.confidence;

      for (let y = 0; y < resolution; y++) {
        for (let x = 0; x < resolution; x++) {
          const dx = x - hx;
          const dy = y - hy;
          const dist2 = dx * dx + dy * dy;
          const influence = amplitude * Math.exp(-dist2 / (2 * sigma * sigma));
          heightmap[y * resolution + x] += influence;
        }
      }
    }

    // Apply heightmap to geometry
    for (let i = 0; i < positions.length / 3; i++) {
      const x = Math.floor((i % resolution));
      const y = Math.floor(i / resolution);
      positions[i * 3 + 2] = heightmap[y * resolution + x];
    }

    geo.computeVertexNormals();
    return geo;
  }, [network, resolution, scale]);

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <primitive object={geometry} attach="geometry" />
      <meshStandardMaterial
        color="#2a4a3a"
        roughness={0.8}
        metalness={0.2}
        wireframe={false}
      />
    </mesh>
  );
}
```

---

## MODULE 4: NETWORK VISUALIZATION

### `NetworkGraph.ts`

```typescript
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { useRef, useMemo, useState } from 'react';
import { Line, Html } from '@react-three/drei';

interface Node {
  id: string;
  label: string;
  position: THREE.Vector3;
  connections: string[];
  category: 'insight' | 'intelligence' | 'imagination';
}

interface NetworkGraphProps {
  nodes: Node[];
  animated?: boolean;
}

const COLORS = {
  insight: new THREE.Color(1.0, 0.84, 0.0),      // Gold
  intelligence: new THREE.Color(0.2, 0.6, 1.0),  // Blue
  imagination: new THREE.Color(1.0, 0.4, 0.8),   // Magenta/Pink
};

export function NetworkGraph({ nodes, animated = true }: NetworkGraphProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Build node map for quick lookup
  const nodeMap = useMemo(() => {
    const map = new Map<string, Node>();
    nodes.forEach(n => map.set(n.id, n));
    return map;
  }, [nodes]);

  // Generate connection lines
  const lines = useMemo(() => {
    const connections: { start: THREE.Vector3; end: THREE.Vector3; color: THREE.Color }[] = [];

    for (const node of nodes) {
      for (const connId of node.connections) {
        const connNode = nodeMap.get(connId);
        if (connNode && node.id < connId) { // Avoid duplicates
          connections.push({
            start: node.position,
            end: connNode.position,
            color: COLORS[node.category],
          });
        }
      }
    }

    return connections;
  }, [nodes, nodeMap]);

  useFrame((state) => {
    if (!animated || !groupRef.current) return;

    // Subtle breathing animation
    const scale = 1 + Math.sin(state.clock.elapsedTime * 0.5) * 0.02;
    groupRef.current.scale.setScalar(scale);
  });

  return (
    <group ref={groupRef}>
      {/* Nodes */}
      {nodes.map((node) => (
        <group key={node.id} position={node.position}>
          <mesh
            onPointerOver={() => setHoveredNode(node.id)}
            onPointerOut={() => setHoveredNode(null)}
          >
            <sphereGeometry args={[0.05, 16, 16]} />
            <meshStandardMaterial
              color={COLORS[node.category]}
              emissive={COLORS[node.category]}
              emissiveIntensity={hoveredNode === node.id ? 0.8 : 0.3}
            />
          </mesh>

          {hoveredNode === node.id && (
            <Html center>
              <div className="node-label">
                {node.label}
              </div>
            </Html>
          )}
        </group>
      ))}

      {/* Connections */}
      {lines.map((line, i) => (
        <Line
          key={i}
          points={[line.start, line.end]}
          color={line.color}
          lineWidth={1}
          transparent
          opacity={0.4}
        />
      ))}
    </group>
  );
}
```

---

## MODULE 5: THE FOLD

### `SpaceFold.ts`

```typescript
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { useRef, useEffect } from 'react';

interface FoldTarget {
  position: THREE.Vector3;
  relevance: number; // 0-1
}

interface SpaceFoldProps {
  targets: FoldTarget[];
  anchorPosition: THREE.Vector3;
  foldStrength?: number;
  duration?: number;
}

export function useSpaceFold({
  targets,
  anchorPosition,
  foldStrength = 1,
  duration = 1.5
}: SpaceFoldProps) {
  const foldProgress = useRef(0);
  const isActive = useRef(false);
  const originalPositions = useRef<THREE.Vector3[]>([]);
  const targetPositions = useRef<THREE.Vector3[]>([]);

  const startFold = () => {
    isActive.current = true;
    foldProgress.current = 0;

    // Store original positions
    originalPositions.current = targets.map(t => t.position.clone());

    // Calculate target positions (fold toward anchor based on relevance)
    targetPositions.current = targets.map(target => {
      const direction = new THREE.Vector3()
        .subVectors(anchorPosition, target.position)
        .normalize();

      const distance = target.position.distanceTo(anchorPosition);
      const foldDistance = distance * (1 - target.relevance) * foldStrength;

      return target.position.clone().add(
        direction.multiplyScalar(distance - foldDistance)
      );
    });
  };

  const unfold = () => {
    targetPositions.current = originalPositions.current;
    foldProgress.current = 1;
    isActive.current = true;
  };

  useFrame((_, delta) => {
    if (!isActive.current) return;

    foldProgress.current += delta / duration;

    if (foldProgress.current >= 1) {
      foldProgress.current = 1;
      isActive.current = false;
    }

    // Ease-in-out cubic
    const t = foldProgress.current;
    const eased = t < 0.5
      ? 4 * t * t * t
      : 1 - Math.pow(-2 * t + 2, 3) / 2;

    // Interpolate positions
    targets.forEach((target, i) => {
      target.position.lerpVectors(
        originalPositions.current[i],
        targetPositions.current[i],
        eased
      );
    });
  });

  return { startFold, unfold, progress: foldProgress };
}
```

---

## MODULE 6: POST-PROCESSING

### `PostProcessing.tsx`

```typescript
import { EffectComposer, Bloom, Vignette, ChromaticAberration } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';

interface PostProcessingProps {
  bloomIntensity?: number;
  vignetteIntensity?: number;
}

export function PostProcessing({
  bloomIntensity = 1.5,
  vignetteIntensity = 0.5
}: PostProcessingProps) {
  return (
    <EffectComposer>
      <Bloom
        intensity={bloomIntensity}
        luminanceThreshold={0.6}
        luminanceSmoothing={0.9}
        mipmapBlur
      />
      <Vignette
        offset={0.3}
        darkness={vignetteIntensity}
        blendFunction={BlendFunction.NORMAL}
      />
      <ChromaticAberration
        offset={[0.001, 0.001]}
        blendFunction={BlendFunction.NORMAL}
      />
    </EffectComposer>
  );
}
```

---

## MODULE 7: SCENE COMPOSITION

### `Atlas.tsx`

```typescript
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, Environment } from '@react-three/drei';
import { Suspense } from 'react';

import { AetherOrb } from './AetherOrb';
import { ParticleField } from './ParticleField';
import { NetworkGraph } from './NetworkGraph';
import { TerrainFromNetwork } from './TerrainFromNetwork';
import { PostProcessing } from './PostProcessing';

export function Atlas() {
  return (
    <Canvas
      camera={{ position: [0, 5, 10], fov: 60 }}
      gl={{
        antialias: true,
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.2
      }}
    >
      <color attach="background" args={['#0a0a1a']} />

      <Suspense fallback={null}>
        {/* Lighting */}
        <ambientLight intensity={0.2} />
        <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
        <pointLight position={[0, 5, 0]} intensity={0.5} color="#4080ff" />

        {/* Environment */}
        <Stars radius={100} depth={50} count={5000} factor={4} />
        <fog attach="fog" args={['#0a0a1a', 10, 50]} />

        {/* Core Elements */}
        <AetherOrb position={[0, 2, 0]} radius={0.8} />
        <ParticleField radius={2} speed={0.5} />

        {/* Network (populated from data) */}
        {/* <NetworkGraph nodes={networkData} animated /> */}

        {/* Terrain (generated from network) */}
        {/* <TerrainFromNetwork network={networkData} scale={20} /> */}

        {/* Controls */}
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          minDistance={2}
          maxDistance={50}
        />

        {/* Post-processing */}
        <PostProcessing bloomIntensity={1.2} />
      </Suspense>
    </Canvas>
  );
}
```

---

## API INTEGRATION

### `BrainClient.ts`

```typescript
interface Intent {
  category: string;
  confidence: number;
  action: string;
}

interface BrainResponse {
  intent: Intent;
  result: any;
  timestamp: number;
}

class BrainClient {
  private baseUrl: string;
  private ws: WebSocket | null = null;

  constructor(baseUrl: string = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
  }

  async parseIntent(query: string): Promise<Intent> {
    const response = await fetch(`${this.baseUrl}/api/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    return response.json();
  }

  async executeQuery(query: string): Promise<BrainResponse> {
    const response = await fetch(`${this.baseUrl}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    return response.json();
  }

  connectWebSocket(onMessage: (data: any) => void) {
    this.ws = new WebSocket(`ws://${new URL(this.baseUrl).host}/ws`);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      this.ws?.close();
    };
  }
}

export const brainClient = new BrainClient();
```

---

## PERFORMANCE GUIDELINES

### Frame Budget (60fps = 16.67ms)

| Component | Target | Max |
|-----------|--------|-----|
| Scene update | 2ms | 4ms |
| Particle system | 1ms | 2ms |
| Network graph | 2ms | 4ms |
| Post-processing | 3ms | 5ms |
| GPU render | 6ms | 8ms |
| **Total** | **14ms** | **23ms** |

### Optimization Techniques

1. **GPU Instancing** — For repeated geometries (particles, nodes)
2. **LOD System** — Reduce detail at distance
3. **Frustum Culling** — Already automatic in Three.js
4. **Texture Atlasing** — Combine small textures
5. **Shader Complexity** — Simplify for mobile
6. **Web Workers** — Offload physics calculations

### Memory Management

```typescript
// Dispose resources when unmounting
useEffect(() => {
  return () => {
    geometry.dispose();
    material.dispose();
    texture?.dispose();
  };
}, []);
```

---

## GETTING STARTED

### 1. Clone and Install

```bash
git clone https://github.com/your-org/3iatlas.git
cd 3iatlas
npm install
```

### 2. Development Server

```bash
npm run dev
```

### 3. Build for Production

```bash
npm run build
npm run preview
```

### 4. Run with Brain Orchestrator

```bash
# Terminal 1: Start Brain
cd 0rb-aether/core/brain
cargo run

# Terminal 2: Start 3iAtlas
npm run dev
```

---

## FILE STRUCTURE

```
3iatlas/
├── src/
│   ├── components/
│   │   ├── AetherOrb.tsx
│   │   ├── ParticleField.tsx
│   │   ├── NetworkGraph.tsx
│   │   ├── TerrainFromNetwork.tsx
│   │   └── PostProcessing.tsx
│   ├── shaders/
│   │   ├── aether.vert.glsl
│   │   ├── aether.frag.glsl
│   │   ├── particle.vert.glsl
│   │   └── terrain.frag.glsl
│   ├── hooks/
│   │   ├── useSpaceFold.ts
│   │   ├── useNetwork.ts
│   │   └── useBrain.ts
│   ├── lib/
│   │   ├── BrainClient.ts
│   │   └── utils.ts
│   ├── stores/
│   │   └── atlasStore.ts
│   ├── Atlas.tsx
│   ├── App.tsx
│   └── main.tsx
├── public/
│   └── assets/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## CONTACT

**Project:** 3iATLAS Developer SDK
**Version:** 0.1.0
**License:** MIT

---

*From abstract to visceral.*
*From code to cosmos.*

**3iAtlas: Where thought becomes space.**
