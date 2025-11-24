"use client";

/**
 * 0r8 Particle Canvas
 * Three-pillar particle system with mouse interaction
 */

import { useEffect, useRef, useCallback } from "react";
import { COLORS } from "@/lib/constants";
import type { Pillar } from "@/types";

interface Particle {
  x: number;
  y: number;
  size: number;
  baseSize: number;
  speedX: number;
  speedY: number;
  type: Pillar;
  color: { r: number; g: number; b: number };
  opacity: number;
  angle?: number;
  angleSpeed?: number;
}

interface ParticleCanvasProps {
  particleCount?: number;
  connectDistance?: number;
  className?: string;
}

export function ParticleCanvas({
  particleCount = 120,
  connectDistance = 100,
  className = "",
}: ParticleCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const mouseRef = useRef({ x: 0, y: 0, radius: 150 });
  const animationRef = useRef<number>();

  const createParticle = useCallback(
    (type: Pillar, width: number, height: number): Particle => {
      const color = COLORS[type].rgb;

      const baseParticle = {
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * 2 + 1,
        baseSize: 0,
        type,
        color,
        opacity: Math.random() * 0.5 + 0.2,
        speedX: 0,
        speedY: 0,
      };

      baseParticle.baseSize = baseParticle.size;

      // Type-specific behavior
      switch (type) {
        case "nous":
          // Fast, linear, purposeful
          baseParticle.speedX = (Math.random() - 0.5) * 2;
          baseParticle.speedY = (Math.random() - 0.5) * 2;
          break;
        case "anima":
          // Organic, flowing, rising like smoke
          baseParticle.speedX = (Math.random() - 0.5) * 1;
          baseParticle.speedY = -Math.random() * 0.5 - 0.2;
          (baseParticle as Particle).angle = Math.random() * Math.PI * 2;
          (baseParticle as Particle).angleSpeed = (Math.random() - 0.5) * 0.02;
          break;
        case "holos":
          // Deliberate, grounding
          baseParticle.speedX = (Math.random() - 0.5) * 0.8;
          baseParticle.speedY = (Math.random() - 0.5) * 0.8;
          break;
      }

      return baseParticle as Particle;
    },
    []
  );

  const initParticles = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const types: Pillar[] = ["nous", "anima", "holos"];
    particlesRef.current = [];

    for (let i = 0; i < particleCount; i++) {
      const type = types[i % 3];
      particlesRef.current.push(
        createParticle(type, canvas.width, canvas.height)
      );
    }
  }, [particleCount, createParticle]);

  const updateParticle = useCallback(
    (particle: Particle, width: number, height: number) => {
      // Type-specific movement
      if (particle.type === "anima" && particle.angle !== undefined) {
        particle.angle += particle.angleSpeed || 0;
        particle.x += Math.sin(particle.angle) * 0.5;
      }

      particle.x += particle.speedX;
      particle.y += particle.speedY;

      // Mouse interaction
      const mouse = mouseRef.current;
      if (mouse.x && mouse.y) {
        const dx = mouse.x - particle.x;
        const dy = mouse.y - particle.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < mouse.radius) {
          const force = (mouse.radius - dist) / mouse.radius;
          const angle = Math.atan2(dy, dx);

          // Gentle attraction
          particle.x += Math.cos(angle) * force * 0.5;
          particle.y += Math.sin(angle) * force * 0.5;
          particle.size = particle.baseSize * (1 + force);
        } else {
          particle.size = particle.baseSize;
        }
      }

      // Boundary wrapping
      if (particle.x < 0) particle.x = width;
      if (particle.x > width) particle.x = 0;
      if (particle.y < 0) particle.y = height;
      if (particle.y > height) particle.y = 0;
    },
    []
  );

  const drawParticle = useCallback(
    (ctx: CanvasRenderingContext2D, particle: Particle) => {
      const { x, y, size, color, opacity } = particle;

      // Main particle
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${opacity})`;
      ctx.fill();

      // Glow effect
      ctx.beginPath();
      ctx.arc(x, y, size * 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${opacity * 0.2})`;
      ctx.fill();
    },
    []
  );

  const drawConnections = useCallback(
    (ctx: CanvasRenderingContext2D, particles: Particle[]) => {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectDistance) {
            const opacity = (1 - dist / connectDistance) * 0.15;

            // Blend colors
            const c1 = particles[i].color;
            const c2 = particles[j].color;
            const r = Math.round((c1.r + c2.r) / 2);
            const g = Math.round((c1.g + c2.g) / 2);
            const b = Math.round((c1.b + c2.b) / 2);

            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${opacity})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
    },
    [connectDistance]
  );

  const animate = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Update and draw
    drawConnections(ctx, particlesRef.current);

    for (const particle of particlesRef.current) {
      updateParticle(particle, canvas.width, canvas.height);
      drawParticle(ctx, particle);
    }

    animationRef.current = requestAnimationFrame(animate);
  }, [updateParticle, drawParticle, drawConnections]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    };

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current.x = e.clientX;
      mouseRef.current.y = e.clientY;
    };

    const handleMouseLeave = () => {
      mouseRef.current.x = 0;
      mouseRef.current.y = 0;
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);

    animate();

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [initParticles, animate]);

  return (
    <canvas
      ref={canvasRef}
      className={`fixed inset-0 pointer-events-none z-0 ${className}`}
    />
  );
}
