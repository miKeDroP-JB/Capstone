//! Particle system for Aether field effects

use bytemuck::{Pod, Zeroable};
use rand::Rng;

#[repr(C)]
#[derive(Copy, Clone, Debug, Pod, Zeroable)]
pub struct Particle {
    pub position: [f32; 3],
    pub velocity: [f32; 3],
    pub life: f32,
    pub size: f32,
}

pub struct ParticleSystem {
    pub particles: Vec<Particle>,
    pub max_particles: usize,
}

impl ParticleSystem {
    pub fn new(max_particles: usize) -> Self {
        let mut rng = rand::thread_rng();
        let particles = (0..max_particles)
            .map(|_| Particle {
                position: [
                    rng.gen_range(-1.0..1.0),
                    rng.gen_range(-1.0..1.0),
                    rng.gen_range(-1.0..1.0),
                ],
                velocity: [
                    rng.gen_range(-0.01..0.01),
                    rng.gen_range(-0.01..0.01),
                    rng.gen_range(-0.01..0.01),
                ],
                life: rng.gen_range(0.0..1.0),
                size: rng.gen_range(0.01..0.05),
            })
            .collect();

        Self { particles, max_particles }
    }

    pub fn update(&mut self, dt: f32) {
        let mut rng = rand::thread_rng();

        for p in &mut self.particles {
            // Update position
            p.position[0] += p.velocity[0] * dt;
            p.position[1] += p.velocity[1] * dt;
            p.position[2] += p.velocity[2] * dt;

            // Decay life
            p.life -= dt * 0.1;

            // Respawn if dead
            if p.life <= 0.0 {
                p.position = [
                    rng.gen_range(-1.0..1.0),
                    rng.gen_range(-1.0..1.0),
                    rng.gen_range(-1.0..1.0),
                ];
                p.velocity = [
                    rng.gen_range(-0.01..0.01),
                    rng.gen_range(-0.01..0.01),
                    rng.gen_range(-0.01..0.01),
                ];
                p.life = 1.0;
            }

            // Boundary wrap
            for i in 0..3 {
                if p.position[i] > 1.5 {
                    p.position[i] = -1.5;
                } else if p.position[i] < -1.5 {
                    p.position[i] = 1.5;
                }
            }
        }
    }
}
