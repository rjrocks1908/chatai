import type { 
  ChatRequest, 
  ChatResponse, 
  StreamChunk, 
  ConversationHistory, 
  SessionStats 
} from "../../types/chat";
import backendInstance from "../axios/backend";

// Chat endpoints
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await backendInstance.post<ChatResponse>(
      "/chat/chat",
      request
    );
    return response.data;
  } catch (error: unknown) {
    console.error("Error sending message:", error);
    throw new Error(`API request failed: ${error}`);
  }
}

export async function sendMessageStream(
  request: ChatRequest,
  onChunk: (chunk: StreamChunk) => void,
  onComplete: () => void,
  onError: (error: string) => void
): Promise<void> {
  try {
    const response = await fetch(`${backendInstance.defaults.baseURL}/chat/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Stream request failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("No response body");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            onComplete();
            return;
          }

          try {
            const chunk: StreamChunk = JSON.parse(data);
            onChunk(chunk);
          } catch (e) {
            console.error("Failed to parse chunk:", e);
          }
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error.message : "Unknown error");
  }
}

// Session management
export async function getSessionHistory(
  sessionId: string,
  limit: number = 50
): Promise<ConversationHistory> {
  try {
    const response = await backendInstance.get<ConversationHistory>(
      `/chat/sessions/${sessionId}/history?limit=${limit}`
    );
    return response.data;
  } catch (error: unknown) {
    console.error("Error getting session history:", error);
    throw new Error(`API request failed: ${error}`);
  }
}

export async function clearSession(
  sessionId: string
): Promise<{ message: string; session_id: string }> {
  try {
    const response = await backendInstance.delete<{ message: string; session_id: string }>(
      `/chat/sessions/${sessionId}`
    );
    return response.data;
  } catch (error: unknown) {
    console.error("Error clearing session:", error);
    throw new Error(`API request failed: ${error}`);
  }
}

export async function getSessionStats(sessionId: string): Promise<SessionStats> {
  try {
    const response = await backendInstance.get<SessionStats>(
      `/chat/sessions/${sessionId}/stats`
    );
    return response.data;
  } catch (error: unknown) {
    console.error("Error getting session stats:", error);
    throw new Error(`API request failed: ${error}`);
  }
}
