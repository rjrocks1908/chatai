import type { ChatRequest, StreamChunk } from "../../types/chat";
import backendInstance from "../axios/backend";

export async function sendMessageStream(
  request: ChatRequest,
  onChunk: (chunk: StreamChunk) => void,
  onComplete: () => void,
  onError: (error: string) => void
): Promise<void> {
  try {
    const response = await fetch(
      `${backendInstance.defaults.baseURL}/chat/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      }
    );

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
            if (chunk.chunk.includes("Error")) {
              onError(chunk.chunk);
              return;
            }
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
