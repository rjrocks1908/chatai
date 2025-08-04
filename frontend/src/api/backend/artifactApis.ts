import type { CodeArtifact } from "../../types/chat";
import backendInstance from "../axios/backend";

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
        responseType: "blob",
      }
    );
    return response.data;
  } catch (error: unknown) {
    console.error("Error downloading artifact:", error);
    throw new Error(`API request failed: ${error}`);
  }
}
