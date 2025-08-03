export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  session_id: string;
  stream?: boolean;
}

export interface ChatResponse {
  message_id: string;
  content: string;
  session_id: string;
  has_artifacts: boolean;
  artifacts?: string[];
  timestamp: string;
}

export interface StreamChunk {
  chunk: string;
  message_id: string;
  session_id: string;
  is_complete: boolean;
  has_artifacts: boolean;
  artifacts?: string[];
  error?: boolean;
}

export interface CodeArtifact {
  id: string;
  title: string;
  description?: string;
  type:
    | "code"
    | "html"
    | "css"
    | "javascript"
    | "python"
    | "react"
    | "markdown"
    | "json"
    | "other";
  language: string;
  content: string;
  session_id: string;
  message_id: string;
  created_at: string;
  metadata?: Record<string, unknown>;
  is_runnable: boolean;
  preview_url?: string;
}

export interface SessionStats {
  total_messages: number;
  total_artifacts: number;
  created_at: string;
  last_updated: string;
  artifacts?: {
    total: number;
    by_type: Record<string, number>;
    by_language: Record<string, number>;
  };
}

export interface ConversationHistory {
  session_id: string;
  messages: ChatMessage[];
  total: number;
}
