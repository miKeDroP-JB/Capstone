// 3iAtlas Navigation Demo
// Simplified version showing folding landscape concept

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

let width, height;
let centerX, centerY;

function resizeCanvas() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    centerX = width / 2;
    centerY = height / 2;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Camera/View State
let camera = {
    x: 0,
    y: 0,
    z: 500,
    rotationX: 0.3,
    rotationY: 0,
    zoom: 1,
    targetZoom: 1,
    foldProgress: 0,
    foldTarget: null
};

let viewMode = 'overview';

// Mouse interaction
let mouse = {
    x: 0,
    y: 0,
    down: false,
    lastX: 0,
    lastY: 0
};

canvas.addEventListener('mousedown', (e) => {
    mouse.down = true;
    mouse.lastX = e.clientX;
    mouse.lastY = e.clientY;
});

canvas.addEventListener('mouseup', () => {
    mouse.down = false;
});

canvas.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;

    if (mouse.down) {
        const dx = e.clientX - mouse.lastX;
        const dy = e.clientY - mouse.lastY;

        camera.rotationY += dx * 0.005;
        camera.rotationX += dy * 0.005;

        // Limit vertical rotation
        camera.rotationX = Math.max(-Math.PI/2, Math.min(Math.PI/2, camera.rotationX));

        mouse.lastX = e.clientX;
        mouse.lastY = e.clientY;
    }
});

canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    camera.targetZoom *= (1 - e.deltaY * 0.001);
    camera.targetZoom = Math.max(0.5, Math.min(3, camera.targetZoom));
}, { passive: false });

canvas.addEventListener('click', (e) => {
    // Check if clicked on an island
    const clickedIsland = findIslandAt(e.clientX, e.clientY);
    if (clickedIsland) {
        foldToIsland(clickedIsland);
    }
});

// Island/Domain data
const domains = [
    { name: 'Code', color: '#4CC9F0', x: -200, y: 0, z: 0, size: 80 },
    { name: 'Business', color: '#FFD700', x: 200, y: 0, z: -100, size: 70 },
    { name: 'Science', color: '#06FFA5', x: 0, y: 0, z: 200, size: 90 },
    { name: 'Design', color: '#9D4EDD', x: 100, y: 50, z: 100, size: 60 },
    { name: 'Math', color: '#FFFFFF', x: -150, y: -30, z: -150, size: 65 },
];

// Problems (canyons)
const problems = [
    { x: 0, y: 100, z: 0, depth: 50, color: '#F72585' },
    { x: -100, y: 80, z: 100, depth: 40, color: '#F72585' },
];

// Insights (connections between domains)
const insights = [];
for (let i = 0; i < domains.length; i++) {
    for (let j = i + 1; j < domains.length; j++) {
        if (Math.random() > 0.6) {
            insights.push({
                from: domains[i],
                to: domains[j],
                strength: Math.random() * 0.5 + 0.5
            });
        }
    }
}

// Concept particles (stars)
const concepts = [];
for (let i = 0; i < 200; i++) {
    const domain = domains[Math.floor(Math.random() * domains.length)];
    concepts.push({
        x: domain.x + (Math.random() - 0.5) * 150,
        y: domain.y + (Math.random() - 0.5) * 150,
        z: domain.z + (Math.random() - 0.5) * 150,
        size: Math.random() * 2 + 0.5,
        color: domain.color,
        twinkle: Math.random() * Math.PI * 2
    });
}

// 3D projection
function project3D(x, y, z) {
    // Apply camera rotation
    let xRot = x;
    let yRot = y * Math.cos(camera.rotationX) - z * Math.sin(camera.rotationX);
    let zRot = y * Math.sin(camera.rotationX) + z * Math.cos(camera.rotationX);

    let xRot2 = xRot * Math.cos(camera.rotationY) + zRot * Math.sin(camera.rotationY);
    let zRot2 = -xRot * Math.sin(camera.rotationY) + zRot * Math.cos(camera.rotationY);

    // Apply folding transformation
    if (camera.foldTarget && camera.foldProgress > 0) {
        const dx = camera.foldTarget.x - xRot2;
        const dy = camera.foldTarget.y - yRot;
        const dz = camera.foldTarget.z - zRot2;
        xRot2 += dx * camera.foldProgress * 0.3;
        yRot += dy * camera.foldProgress * 0.3;
        zRot2 += dz * camera.foldProgress * 0.3;
    }

    // Perspective projection
    const perspective = camera.z / (camera.z + zRot2);
    const x2d = centerX + xRot2 * perspective * camera.zoom;
    const y2d = centerY + yRot * perspective * camera.zoom;

    return { x: x2d, y: y2d, scale: perspective, z: zRot2 };
}

// Drawing functions
function drawIsland(island) {
    const pos = project3D(island.x, island.y, island.z);

    if (pos.z < -camera.z) return; // Behind camera

    const size = island.size * pos.scale * camera.zoom;

    // Mountain shape (triangle)
    ctx.save();
    ctx.translate(pos.x, pos.y);

    // Glow
    const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, size * 1.5);
    gradient.addColorStop(0, island.color + '40');
    gradient.addColorStop(1, island.color + '00');
    ctx.fillStyle = gradient;
    ctx.fillRect(-size * 1.5, -size * 1.5, size * 3, size * 3);

    // Mountain
    ctx.beginPath();
    ctx.moveTo(0, -size);
    ctx.lineTo(-size * 0.7, size * 0.3);
    ctx.lineTo(size * 0.7, size * 0.3);
    ctx.closePath();

    ctx.fillStyle = island.color + '80';
    ctx.fill();

    ctx.strokeStyle = island.color;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Label
    if (viewMode === 'overview' && size > 20) {
        ctx.fillStyle = island.color;
        ctx.font = `${Math.min(14, size / 4)}px IBM Plex Mono`;
        ctx.textAlign = 'center';
        ctx.fillText(island.name, 0, size * 0.6);
    }

    ctx.restore();
}

function drawProblem(problem) {
    const pos = project3D(problem.x, problem.y, problem.z);

    if (pos.z < -camera.z) return;

    const size = problem.depth * pos.scale * camera.zoom;

    // Canyon (inverted triangle)
    ctx.save();
    ctx.translate(pos.x, pos.y);

    ctx.beginPath();
    ctx.moveTo(0, size);
    ctx.lineTo(-size * 0.5, -size * 0.3);
    ctx.lineTo(size * 0.5, -size * 0.3);
    ctx.closePath();

    ctx.fillStyle = problem.color + '40';
    ctx.fill();
    ctx.strokeStyle = problem.color;
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.restore();
}

function drawInsight(insight) {
    const from = project3D(insight.from.x, insight.from.y, insight.from.z);
    const to = project3D(insight.to.x, insight.to.y, insight.to.z);

    if (from.z < -camera.z || to.z < -camera.z) return;

    // Flowing river effect
    ctx.save();

    const gradient = ctx.createLinearGradient(from.x, from.y, to.x, to.y);
    gradient.addColorStop(0, '#FFD700' + Math.floor(insight.strength * 100).toString(16));
    gradient.addColorStop(0.5, '#FFFFFF' + Math.floor(insight.strength * 150).toString(16));
    gradient.addColorStop(1, '#4CC9F0' + Math.floor(insight.strength * 100).toString(16));

    ctx.strokeStyle = gradient;
    ctx.lineWidth = insight.strength * 2;
    ctx.setLineDash([5, 5]);

    ctx.beginPath();
    ctx.moveTo(from.x, from.y);

    // Curved path
    const midX = (from.x + to.x) / 2;
    const midY = (from.y + to.y) / 2 - 50;
    ctx.quadraticCurveTo(midX, midY, to.x, to.y);

    ctx.stroke();
    ctx.setLineDash([]);

    ctx.restore();
}

function drawConcept(concept) {
    const pos = project3D(concept.x, concept.y, concept.z);

    if (pos.z < -camera.z) return;

    const size = concept.size * pos.scale * camera.zoom;

    // Twinkling star
    const alpha = (Math.sin(Date.now() * 0.003 + concept.twinkle) + 1) / 2;

    ctx.save();
    ctx.globalAlpha = alpha * 0.8;

    ctx.fillStyle = concept.color;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, size, 0, Math.PI * 2);
    ctx.fill();

    // Glow
    const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, size * 3);
    gradient.addColorStop(0, concept.color + '80');
    gradient.addColorStop(1, concept.color + '00');
    ctx.fillStyle = gradient;
    ctx.fillRect(pos.x - size * 3, pos.y - size * 3, size * 6, size * 6);

    ctx.restore();
}

// Find island at screen coordinates
function findIslandAt(x, y) {
    for (let island of domains) {
        const pos = project3D(island.x, island.y, island.z);
        const size = island.size * pos.scale * camera.zoom;
        const dx = x - pos.x;
        const dy = y - pos.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < size) {
            return island;
        }
    }
    return null;
}

// Folding animation
function foldToIsland(island) {
    camera.foldTarget = island;
    camera.foldProgress = 0;

    // Animate fold
    const startTime = Date.now();
    const duration = 1000;

    function animateFold() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(1, elapsed / duration);

        camera.foldProgress = easeInOutCubic(progress);

        if (progress < 1) {
            requestAnimationFrame(animateFold);
        } else {
            // Hold for a moment, then unfold
            setTimeout(() => {
                unfold();
            }, 500);
        }
    }

    animateFold();
}

function unfold() {
    const startTime = Date.now();
    const duration = 800;

    function animateUnfold() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(1, elapsed / duration);

        camera.foldProgress = 1 - easeInOutCubic(progress);

        if (progress < 1) {
            requestAnimationFrame(animateUnfold);
        } else {
            camera.foldTarget = null;
            camera.foldProgress = 0;
        }
    }

    animateUnfold();
}

function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// View modes
function setViewMode(mode) {
    viewMode = mode;

    if (mode === 'overview') {
        camera.targetZoom = 1;
        camera.rotationX = 0.3;
    } else if (mode === 'detail') {
        camera.targetZoom = 2;
    } else if (mode === 'perspective') {
        camera.rotationX = 0.1;
        camera.rotationY += Math.PI / 4;
    }
}

function foldToRandom() {
    const randomIsland = domains[Math.floor(Math.random() * domains.length)];
    foldToIsland(randomIsland);
}

// Main render loop
function render() {
    // Clear with fade trail
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, width, height);

    // Smooth zoom
    camera.zoom += (camera.targetZoom - camera.zoom) * 0.1;

    // Auto-rotate slightly
    if (!mouse.down) {
        camera.rotationY += 0.001;
    }

    // Sort by depth for proper rendering
    const allObjects = [
        ...concepts.map(c => ({ type: 'concept', data: c, z: c.z })),
        ...insights.map(i => ({ type: 'insight', data: i, z: (i.from.z + i.to.z) / 2 })),
        ...problems.map(p => ({ type: 'problem', data: p, z: p.z })),
        ...domains.map(d => ({ type: 'island', data: d, z: d.z }))
    ];

    allObjects.sort((a, b) => a.z - b.z);

    // Render
    for (let obj of allObjects) {
        switch (obj.type) {
            case 'concept':
                drawConcept(obj.data);
                break;
            case 'insight':
                drawInsight(obj.data);
                break;
            case 'problem':
                drawProblem(obj.data);
                break;
            case 'island':
                drawIsland(obj.data);
                break;
        }
    }

    requestAnimationFrame(render);
}

// Start
render();

console.log('3iAtlas Navigation Demo v0.1');
console.log('Click islands to fold space toward them');
console.log('Drag to rotate, scroll to zoom');
