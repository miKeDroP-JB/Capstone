'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCompetitionStore } from '@/lib/store';

const AVAILABLE_MODELS = [
  // Free Models
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI', free: true, power: 60 },
  { id: 'claude-instant', name: 'Claude Instant', provider: 'Anthropic', free: true, power: 65 },
  { id: 'llama-2-70b', name: 'Llama 2 70B', provider: 'Meta', free: true, power: 70 },
  { id: 'mistral-7b', name: 'Mistral 7B', provider: 'Mistral', free: true, power: 55 },

  // Paid Models
  { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', provider: 'OpenAI', free: false, power: 95 },
  { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'Anthropic', free: false, power: 98 },
  { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'Anthropic', free: false, power: 90 },
  { id: 'gemini-ultra', name: 'Gemini Ultra', provider: 'Google', free: false, power: 93 },
  { id: 'grok-1', name: 'Grok-1', provider: 'xAI', free: false, power: 88 },
  { id: 'command-r-plus', name: 'Command R+', provider: 'Cohere', free: false, power: 85 },
];

export default function ControlPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const { config, updateConfig, toggleModel } = useCompetitionStore();

  const filteredModels = config.freeOnly
    ? AVAILABLE_MODELS.filter(m => m.free)
    : AVAILABLE_MODELS;

  return (
    <>
      {/* Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-8 right-8 z-50 bg-slate-900/80 backdrop-blur-lg border border-cyan-500/30 p-4 rounded-full hover:border-cyan-500 transition-all"
      >
        <svg
          className="w-6 h-6 text-cyan-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
          />
        </svg>
      </motion.button>

      {/* Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            />

            {/* Panel Content */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25 }}
              className="fixed right-0 top-0 h-full w-full max-w-lg bg-slate-900/95 backdrop-blur-xl border-l border-cyan-500/30 z-50 overflow-y-auto"
            >
              <div className="p-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                  <h2 className="text-2xl font-bold text-cyan-400">Agent Control</h2>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="text-slate-400 hover:text-white"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {/* Free/Paid Toggle */}
                <div className="mb-8">
                  <label className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium text-slate-300">Free Models Only</span>
                    <button
                      onClick={() => updateConfig({ freeOnly: !config.freeOnly })}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        config.freeOnly ? 'bg-cyan-500' : 'bg-slate-700'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          config.freeOnly ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </label>
                </div>

                {/* Time Slider */}
                <div className="mb-8">
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Time Limit: {config.timeLimit}s
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="300"
                    value={config.timeLimit}
                    onChange={(e) => updateConfig({ timeLimit: parseInt(e.target.value) })}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>Fast (5s)</span>
                    <span>Thorough (300s)</span>
                  </div>
                </div>

                {/* Power Slider */}
                <div className="mb-8">
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Power Level: {config.powerLevel}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.powerLevel}
                    onChange={(e) => updateConfig({ powerLevel: parseInt(e.target.value) })}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>Efficient</span>
                    <span>Maximum</span>
                  </div>
                </div>

                {/* Model Selection */}
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">
                    Select Models ({config.selectedModels.length}/{filteredModels.length})
                  </h3>

                  <div className="space-y-2">
                    {filteredModels.map((model) => (
                      <motion.button
                        key={model.id}
                        whileHover={{ x: 4 }}
                        onClick={() => toggleModel(model.id)}
                        className={`w-full text-left p-4 rounded-lg border transition-all ${
                          config.selectedModels.includes(model.id)
                            ? 'bg-cyan-500/20 border-cyan-500'
                            : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-white">{model.name}</span>
                              {model.free && (
                                <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full">
                                  FREE
                                </span>
                              )}
                            </div>
                            <div className="text-sm text-slate-400 mt-1">{model.provider}</div>
                          </div>

                          {/* Power Indicator */}
                          <div className="flex items-center gap-2">
                            <div className="text-xs text-slate-500">{model.power}%</div>
                            <div className={`w-4 h-4 rounded-full border-2 ${
                              config.selectedModels.includes(model.id)
                                ? 'border-cyan-500 bg-cyan-500'
                                : 'border-slate-600'
                            }`}>
                              {config.selectedModels.includes(model.id) && (
                                <svg className="w-full h-full text-white" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Quick Presets */}
                <div className="mt-8 pt-8 border-t border-slate-700">
                  <h3 className="text-lg font-semibold text-white mb-4">Quick Presets</h3>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => {
                        updateConfig({
                          selectedModels: filteredModels.slice(0, 3).map(m => m.id),
                          powerLevel: 50,
                          timeLimit: 30,
                        });
                      }}
                      className="px-4 py-3 bg-blue-500/20 border border-blue-500/50 rounded-lg hover:bg-blue-500/30 transition-colors"
                    >
                      <div className="text-sm font-medium">Fast</div>
                      <div className="text-xs text-slate-400">3 models, 30s</div>
                    </button>

                    <button
                      onClick={() => {
                        updateConfig({
                          selectedModels: filteredModels.map(m => m.id),
                          powerLevel: 100,
                          timeLimit: 120,
                        });
                      }}
                      className="px-4 py-3 bg-purple-500/20 border border-purple-500/50 rounded-lg hover:bg-purple-500/30 transition-colors"
                    >
                      <div className="text-sm font-medium">Max Power</div>
                      <div className="text-xs text-slate-400">All models, 120s</div>
                    </button>

                    <button
                      onClick={() => {
                        const freeModels = AVAILABLE_MODELS.filter(m => m.free).map(m => m.id);
                        updateConfig({
                          selectedModels: freeModels,
                          freeOnly: true,
                          powerLevel: 70,
                        });
                      }}
                      className="px-4 py-3 bg-green-500/20 border border-green-500/50 rounded-lg hover:bg-green-500/30 transition-colors"
                    >
                      <div className="text-sm font-medium">Free Only</div>
                      <div className="text-xs text-slate-400">No cost</div>
                    </button>

                    <button
                      onClick={() => {
                        const topModels = AVAILABLE_MODELS
                          .sort((a, b) => b.power - a.power)
                          .slice(0, 5)
                          .map(m => m.id);
                        updateConfig({
                          selectedModels: topModels,
                          freeOnly: false,
                          powerLevel: 95,
                          timeLimit: 180,
                        });
                      }}
                      className="px-4 py-3 bg-red-500/20 border border-red-500/50 rounded-lg hover:bg-red-500/30 transition-colors"
                    >
                      <div className="text-sm font-medium">Competition</div>
                      <div className="text-xs text-slate-400">Top 5, max</div>
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
