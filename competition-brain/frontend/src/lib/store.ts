import { create } from 'zustand';

interface CompetitionConfig {
  selectedModels: string[];
  freeOnly: boolean;
  timeLimit: number;
  powerLevel: number;
}

interface Response {
  id: string;
  query: string;
  synthesized: string;
  individual: Array<{
    model: string;
    response: string;
    confidence: number;
    time: number;
  }>;
  totalTime: number;
  timestamp: Date;
}

interface CompetitionStore {
  config: CompetitionConfig;
  responses: Response[];
  updateConfig: (config: Partial<CompetitionConfig>) => void;
  toggleModel: (modelId: string) => void;
  addResponse: (response: Response) => void;
  clearResponses: () => void;
}

export const useCompetitionStore = create<CompetitionStore>((set) => ({
  config: {
    selectedModels: ['gpt-4-turbo', 'claude-3-opus', 'gemini-ultra'],
    freeOnly: false,
    timeLimit: 60,
    powerLevel: 80,
  },
  responses: [],

  updateConfig: (newConfig) =>
    set((state) => ({
      config: { ...state.config, ...newConfig },
    })),

  toggleModel: (modelId) =>
    set((state) => ({
      config: {
        ...state.config,
        selectedModels: state.config.selectedModels.includes(modelId)
          ? state.config.selectedModels.filter((id) => id !== modelId)
          : [...state.config.selectedModels, modelId],
      },
    })),

  addResponse: (response) =>
    set((state) => ({
      responses: [...state.responses, response],
    })),

  clearResponses: () => set({ responses: [] }),
}));
