import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { ChatMessage, CodeArtifact } from '../../types/chat';
import { generateSessionId } from '../../utils/helpers';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  sessionId: string;
  currentStreamingMessage: ChatMessage | null;
  artifacts: CodeArtifact[];
  showArtifacts: boolean;
  showPreview: boolean;
  previewArtifacts: CodeArtifact[];
  error: string | null;
  isConnected: boolean;
}

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  sessionId: '',
  currentStreamingMessage: null,
  artifacts: [],
  showArtifacts: false,
  showPreview: false,
  previewArtifacts: [],
  error: null,
  isConnected: true,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    initializeSession: (state) => {
      state.sessionId = generateSessionId();
    },
    addUserMessage: (state, action: PayloadAction<string>) => {
      const userMessage: ChatMessage = {
        id: `user_${Date.now()}`,
        role: 'user',
        content: action.payload,
        timestamp: new Date().toISOString(),
      };
      state.messages.push(userMessage);
    },
    startStreamingMessage: (state) => {
      const streamingMessage: ChatMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
      };
      state.currentStreamingMessage = streamingMessage;
    },
    updateStreamingMessage: (state, action: PayloadAction<string>) => {
      if (state.currentStreamingMessage) {
        state.currentStreamingMessage.content += action.payload;
      }
    },
    completeStreamingMessage: (state) => {
      if (state.currentStreamingMessage) {
        state.messages.push(state.currentStreamingMessage);
        state.currentStreamingMessage = null;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },
    setArtifacts: (state, action: PayloadAction<CodeArtifact[]>) => {
      state.artifacts = action.payload;
      state.showArtifacts = true;
    },
    toggleArtifacts: (state) => {
      state.showArtifacts = !state.showArtifacts;
    },
    setShowArtifacts: (state, action: PayloadAction<boolean>) => {
      state.showArtifacts = action.payload;
    },
    setShowPreview: (state, action: PayloadAction<boolean>) => {
      state.showPreview = action.payload;
    },
    setPreviewArtifacts: (state, action: PayloadAction<CodeArtifact[]>) => {
      state.previewArtifacts = action.payload;
    },
    clearChat: (state) => {
      state.messages = [];
      state.artifacts = [];
      state.showArtifacts = false;
      state.currentStreamingMessage = null;
      state.error = null;
      state.sessionId = generateSessionId();
    },
  },
});

export const {
  initializeSession,
  addUserMessage,
  startStreamingMessage,
  updateStreamingMessage,
  completeStreamingMessage,
  setLoading,
  setError,
  setConnected,
  setArtifacts,
  toggleArtifacts,
  setShowArtifacts,
  setShowPreview,
  setPreviewArtifacts,
  clearChat,
} = chatSlice.actions;

export default chatSlice.reducer;