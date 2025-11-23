'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import VoiceOrb from '@/components/VoiceOrb';
import ControlPanel from '@/components/ControlPanel';
import ResponseDisplay from '@/components/ResponseDisplay';
import { useCompetitionStore } from '@/lib/store';

export default function Home() {
  const [isVoiceMode, setIsVoiceMode] = useState(true);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { responses, addResponse, config } = useCompetitionStore();

  const handleSubmit = async () => {
    if (!input.trim()) return;

    setIsProcessing(true);

    try {
      const response = await fetch('http://localhost:3001/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: input,
          config: {
            models: config.selectedModels,
            freeOnly: config.freeOnly,
            timeLimit: config.timeLimit,
            powerLevel: config.powerLevel,
          },
        }),
      });

      const data = await response.json();
      addResponse(data);
      setInput('');
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVoiceInput = (transcript: string) => {
    setInput(transcript);
    handleSubmit();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white overflow-hidden">
      {/* Animated Background Grid */}
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10"></div>

      {/* Control Panel Toggle */}
      <ControlPanel />

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-12 text-center"
        >
          <h1 className="text-6xl md:text-8xl font-bold mb-4 bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
            0RB BRAIN
          </h1>
          <p className="text-xl md:text-2xl text-slate-400">
            Multi-Agent Competition Intelligence
          </p>
        </motion.div>

        {/* Voice Orb or Text Input */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 1, delay: 0.2 }}
          className="mb-8"
        >
          {isVoiceMode ? (
            <VoiceOrb
              isProcessing={isProcessing}
              onTranscript={handleVoiceInput}
            />
          ) : (
            <div className="w-full max-w-2xl">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                placeholder="Enter your query..."
                className="w-full h-32 bg-slate-900/50 border border-cyan-500/30 rounded-2xl px-6 py-4 text-lg focus:outline-none focus:border-cyan-500 backdrop-blur-lg resize-none"
                disabled={isProcessing}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSubmit}
                disabled={isProcessing}
                className="mt-4 w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 px-8 py-4 rounded-xl font-semibold text-lg disabled:opacity-50"
              >
                {isProcessing ? 'Processing...' : 'Submit Query'}
              </motion.button>
            </div>
          )}
        </motion.div>

        {/* Input Mode Toggle */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="fixed bottom-8 right-8 z-50"
        >
          <button
            onClick={() => setIsVoiceMode(!isVoiceMode)}
            className="flex items-center gap-3 bg-slate-900/80 backdrop-blur-lg border border-cyan-500/30 px-6 py-3 rounded-full hover:border-cyan-500 transition-all group"
          >
            <div className="relative">
              <div className={`w-3 h-3 rounded-full ${isVoiceMode ? 'bg-red-500' : 'bg-cyan-500'} animate-pulse`}></div>
            </div>
            <span className="font-medium">
              {isVoiceMode ? 'Voice Mode' : 'Text Mode'}
            </span>
            <svg
              className="w-5 h-5 group-hover:scale-110 transition-transform"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isVoiceMode ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              )}
            </svg>
          </button>
        </motion.div>

        {/* Response Display */}
        <AnimatePresence>
          {responses.length > 0 && (
            <ResponseDisplay responses={responses} />
          )}
        </AnimatePresence>

        {/* Stats Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="fixed bottom-8 left-8 text-sm text-slate-500"
        >
          <div className="flex gap-6">
            <div>Agents: <span className="text-cyan-400 font-semibold">{config.selectedModels.length}</span></div>
            <div>Mode: <span className="text-cyan-400 font-semibold">{config.freeOnly ? 'Free' : 'All'}</span></div>
            <div>Power: <span className="text-cyan-400 font-semibold">{config.powerLevel}%</span></div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
