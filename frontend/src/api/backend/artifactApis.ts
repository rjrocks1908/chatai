import type { CodeArtifact } from "../../types/chat";
import backendInstance from "../axios/backend";

// Artifact management
export async function getArtifacts(
  sessionId: string,
  messageId: string
): Promise<{ artifacts: CodeArtifact[]; total: number }> {
  try {
    const response = await backendInstance.get<{ artifacts: CodeArtifact[]; total: number }>(
      `/artifacts/${sessionId}/${messageId}`
    );
    return response.data;
  } catch (error: unknown) {
    console.error("Error getting artifacts:", error);
    throw new Error(`API request failed: ${error}`);
  }
}

export async function getArtifact(artifactId: string): Promise<CodeArtifact> {
  try {
    const response = await backendInstance.get<CodeArtifact>(
      `/artifacts/artifacts/${artifactId}`
    );
    return response.data;
  } catch (error: unknown) {
    console.error("Error getting artifact:", error);
    throw new Error(`API request failed: ${error}`);
  }
}

export async function downloadArtifact(artifactId: string): Promise<Blob> {
  try {
    const response = await backendInstance.get(
      `/artifacts/artifacts/${artifactId}/download`,
      {
        responseType: 'blob'
      }
    );
    return response.data;
  } catch (error: unknown) {
    console.error("Error downloading artifact:", error);
    throw new Error(`API request failed: ${error}`);
  }
}
