/**
 * 0r8 Chat State Management
 */

import { create } from "zustand";
import type { Message, Conversation, ThreeIWeights, DemigodId, DomainId } from "@/types";

interface ChatState {
  // Current conversation
  conversationId: string | null;
  messages: Message[];
  isLoading: boolean;

  // Conversation list
  conversations: Conversation[];

  // Actions
  setConversationId: (id: string | null) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, content: string) => void;
  setMessages: (messages: Message[]) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;

  // Conversation management
  addConversation: (conversation: Conversation) => void;
  setConversations: (conversations: Conversation[]) => void;
  deleteConversation: (id: string) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  conversationId: null,
  messages: [],
  isLoading: false,
  conversations: [],

  // Actions
  setConversationId: (id) => set({ conversationId: id }),

  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  updateMessage: (id, content) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content } : msg
      ),
    }));
  },

  setMessages: (messages) => set({ messages }),

  setLoading: (loading) => set({ isLoading: loading }),

  clearMessages: () => set({ messages: [], conversationId: null }),

  addConversation: (conversation) => {
    set((state) => ({
      conversations: [conversation, ...state.conversations],
    }));
  },

  setConversations: (conversations) => set({ conversations }),

  deleteConversation: (id) => {
    set((state) => ({
      conversations: state.conversations.filter((c) => c.id !== id),
      conversationId: state.conversationId === id ? null : state.conversationId,
      messages: state.conversationId === id ? [] : state.messages,
    }));
  },
}));
