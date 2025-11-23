'use client';

import { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial } from '@react-three/drei';
import { motion } from 'framer-motion';
import * as THREE from 'three';

interface VoiceOrbProps {
  isProcessing: boolean;
  onTranscript: (text: string) => void;
}

function AnimatedOrb({ isProcessing }: { isProcessing: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.getElapsedTime() * 0.2;
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.3;

      // Pulse effect when processing
      if (isProcessing) {
        const scale = 1 + Math.sin(state.clock.getElapsedTime() * 3) * 0.1;
        meshRef.current.scale.setScalar(scale);
      }
    }
  });

  return (
    <Sphere
      ref={meshRef}
      args={[1, 64, 64]}
      scale={hovered ? 1.1 : 1}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <MeshDistortMaterial
        color={isProcessing ? "#00ffff" : "#0099ff"}
        attach="material"
        distort={isProcessing ? 0.6 : 0.3}
        speed={isProcessing ? 3 : 1}
        roughness={0.2}
        metalness={0.8}
      />
    </Sphere>
  );
}

export default function VoiceOrb({ isProcessing, onTranscript }: VoiceOrbProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Web Speech API setup
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event: any) => {
        const current = event.resultIndex;
        const transcriptText = event.results[current][0].transcript;
        setTranscript(transcriptText);

        if (event.results[current].isFinal) {
          onTranscript(transcriptText);
          setTranscript('');
          setIsListening(false);
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onTranscript]);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  return (
    <div className="relative">
      {/* 3D Orb */}
      <div
        className="w-80 h-80 cursor-pointer"
        onClick={toggleListening}
      >
        <Canvas camera={{ position: [0, 0, 3], fov: 50 }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <pointLight position={[-10, -10, -5]} intensity={0.5} color="#00ffff" />
          <AnimatedOrb isProcessing={isProcessing || isListening} />
        </Canvas>
      </div>

      {/* Status Indicator */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 w-full text-center"
      >
        {isListening && (
          <div className="flex flex-col items-center gap-2">
            <div className="flex gap-1">
              {[...Array(3)].map((_, i) => (
                <motion.div
                  key={i}
                  className="w-1 h-8 bg-cyan-400 rounded-full"
                  animate={{
                    scaleY: [1, 1.5, 1],
                  }}
                  transition={{
                    duration: 0.5,
                    repeat: Infinity,
                    delay: i * 0.1,
                  }}
                />
              ))}
            </div>
            <p className="text-cyan-400 text-sm font-medium">Listening...</p>
          </div>
        )}

        {transcript && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-slate-300 text-sm mt-2 px-4"
          >
            "{transcript}"
          </motion.p>
        )}

        {!isListening && !isProcessing && (
          <p className="text-slate-500 text-sm">Click orb to speak</p>
        )}

        {isProcessing && (
          <div className="flex items-center justify-center gap-2">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-ping"></div>
            <p className="text-cyan-400 text-sm">Processing...</p>
          </div>
        )}
      </motion.div>

      {/* Glow Effect */}
      <div className="absolute inset-0 bg-cyan-500/20 blur-3xl rounded-full -z-10 animate-pulse"></div>
    </div>
  );
}
