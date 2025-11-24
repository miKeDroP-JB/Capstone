// 0RB Empire - Living Particle Logo System
// "Consistency is the pattern of evolution, not static repetition"

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Responsive canvas
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Particle class
class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.radius = Math.random() * 2 + 1;
        this.opacity = Math.random() * 0.5 + 0.5;
        this.hue = Math.random() * 60 + 260; // Purple to blue range
        this.targetX = x;
        this.targetY = y;
    }

    update(state, mouseX, mouseY) {
        // Apply state-specific behavior
        switch (state) {
            case 'dormant':
                this.applyDormant();
                break;
            case 'coalescing':
                this.applyCoalescing();
                break;
            case 'active':
                this.applyActive();
                break;
            case 'dispersing':
                this.applyDispersing();
                break;
            case 'quantum':
                this.applyQuantum();
                break;
        }

        // Mouse interaction
        const dx = mouseX - this.x;
        const dy = mouseY - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 100) {
            const force = (100 - distance) / 100;
            this.vx -= (dx / distance) * force * 0.5;
            this.vy -= (dy / distance) * force * 0.5;
        }

        // Update position
        this.x += this.vx;
        this.y += this.vy;

        // Damping
        this.vx *= 0.95;
        this.vy *= 0.95;

        // Boundaries
        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

        this.x = Math.max(0, Math.min(canvas.width, this.x));
        this.y = Math.max(0, Math.min(canvas.height, this.y));
    }

    applyDormant() {
        // Random drift
        this.vx += (Math.random() - 0.5) * 0.1;
        this.vy += (Math.random() - 0.5) * 0.1;
        this.opacity = Math.min(0.8, this.opacity + 0.01);
    }

    applyCoalescing() {
        // Attraction to target position (logo shape)
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;
        this.vx += dx * 0.01;
        this.vy += dy * 0.01;
        this.opacity = Math.min(1.0, this.opacity + 0.02);
    }

    applyActive() {
        // Maintain shape with slight movement
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;
        this.vx += dx * 0.03;
        this.vy += dy * 0.03;

        // Slight oscillation
        this.vx += Math.sin(Date.now() * 0.001 + this.x * 0.01) * 0.1;
        this.vy += Math.cos(Date.now() * 0.001 + this.y * 0.01) * 0.1;

        this.opacity = 1.0;
    }

    applyDispersing() {
        // Repulsion from center
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const dx = this.x - centerX;
        const dy = this.y - centerY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
            this.vx += (dx / distance) * 0.5;
            this.vy += (dy / distance) * 0.5;
        }

        this.opacity = Math.max(0.2, this.opacity - 0.01);
    }

    applyQuantum() {
        // Superposition: multiple states at once
        // Split between random and attracted behavior
        if (Math.random() > 0.5) {
            this.applyCoalescing();
        } else {
            this.applyDormant();
        }

        // Quantum flicker
        this.opacity = 0.3 + Math.random() * 0.7;

        // Teleportation chance
        if (Math.random() < 0.001) {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
        }
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);

        // Gradient fill
        const gradient = ctx.createRadialGradient(
            this.x, this.y, 0,
            this.x, this.y, this.radius * 2
        );

        gradient.addColorStop(0, `hsla(${this.hue}, 80%, 60%, ${this.opacity})`);
        gradient.addColorStop(1, `hsla(${this.hue}, 80%, 60%, 0)`);

        ctx.fillStyle = gradient;
        ctx.fill();

        // Glow effect
        ctx.shadowBlur = 10;
        ctx.shadowColor = `hsl(${this.hue}, 80%, 60%)`;
    }
}

// Particle system
class ParticleSystem {
    constructor(count = 1000) {
        this.particles = [];
        this.state = 'coalescing';
        this.mouseX = canvas.width / 2;
        this.mouseY = canvas.height / 2;

        this.initParticles(count);
    }

    initParticles(count) {
        // Create particles arranged to form "0RB" text
        this.particles = [];

        for (let i = 0; i < count; i++) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height;

            const particle = new Particle(x, y);

            // Assign target positions to form logo
            // For v0.1, create abstract cluster pattern
            // In production, parse actual "0RB" text into particle positions

            const angle = (i / count) * Math.PI * 2;
            const radius = 100 + Math.random() * 100;

            particle.targetX = canvas.width / 2 + Math.cos(angle) * radius;
            particle.targetY = canvas.height / 2 + Math.sin(angle) * radius;

            // Add some to form letters (simplified)
            if (i % 4 === 0) {
                // "0" - circle on left
                const letterAngle = (i / count) * Math.PI * 2;
                particle.targetX = canvas.width / 2 - 200 + Math.cos(letterAngle) * 60;
                particle.targetY = canvas.height / 2 + Math.sin(letterAngle) * 80;
            } else if (i % 4 === 1) {
                // "R" - middle
                particle.targetX = canvas.width / 2 - 50 + (i % 20) * 5;
                particle.targetY = canvas.height / 2 - 80 + (i % 30) * 5;
            } else if (i % 4 === 2) {
                // "B" - right
                particle.targetX = canvas.width / 2 + 100 + (i % 20) * 5;
                particle.targetY = canvas.height / 2 - 80 + (i % 30) * 5;
            }

            this.particles.push(particle);
        }
    }

    setState(newState) {
        this.state = newState;
        document.getElementById('currentState').textContent =
            newState.charAt(0).toUpperCase() + newState.slice(1);
    }

    update() {
        for (let particle of this.particles) {
            particle.update(this.state, this.mouseX, this.mouseY);
        }
    }

    draw() {
        // Clear with fade trail
        ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw connections (in active/coalescing states)
        if (this.state === 'active' || this.state === 'coalescing') {
            ctx.strokeStyle = 'rgba(157, 78, 221, 0.1)';
            ctx.lineWidth = 0.5;

            for (let i = 0; i < this.particles.length; i++) {
                for (let j = i + 1; j < this.particles.length; j++) {
                    const p1 = this.particles[i];
                    const p2 = this.particles[j];

                    const dx = p2.x - p1.x;
                    const dy = p2.y - p1.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < 50) {
                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
            }
        }

        // Draw particles
        for (let particle of this.particles) {
            particle.draw();
        }
    }

    setMouse(x, y) {
        this.mouseX = x;
        this.mouseY = y;
    }
}

// Initialize
const system = new ParticleSystem(1000);

// Mouse tracking
canvas.addEventListener('mousemove', (e) => {
    system.setMouse(e.clientX, e.clientY);
});

// Click to cycle states
let stateIndex = 1;
const states = ['dormant', 'coalescing', 'active', 'dispersing', 'quantum'];

canvas.addEventListener('click', () => {
    stateIndex = (stateIndex + 1) % states.length;
    system.setState(states[stateIndex]);
});

// State control functions
function setStateDormant() { system.setState('dormant'); }
function setStateCoalescing() { system.setState('coalescing'); }
function setStateActive() { system.setState('active'); }
function setStateDispersing() { system.setState('dispersing'); }
function setStateQuantum() { system.setState('quantum'); }

// Animation loop
function animate() {
    system.update();
    system.draw();
    requestAnimationFrame(animate);
}

animate();

// Auto-transition demo (optional - uncomment to enable)
/*
setInterval(() => {
    const currentTime = new Date();
    const minutes = currentTime.getMinutes();
    const seconds = currentTime.getSeconds();

    // At 11:11, activate quantum state
    if (currentTime.getHours() === 11 && minutes === 11) {
        system.setState('quantum');
    }

    // Every 20 seconds, cycle through states
    const cycleStates = ['dormant', 'coalescing', 'active', 'dispersing'];
    const stateIdx = Math.floor(seconds / 15) % cycleStates.length;
    system.setState(cycleStates[stateIdx]);
}, 1000);
*/
