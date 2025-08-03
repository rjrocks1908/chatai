import backendInstance from "../axios/backend";

// Health check
export async function healthCheck(): Promise<{
  status: string;
  version: string;
  api_key_configured: boolean;
}> {
  try {
    const response = await backendInstance.get<{
      status: string;
      version: string;
      api_key_configured: boolean;
    }>("/health");
    return response.data;
  } catch (error: unknown) {
    console.error("Error checking health:", error);
    throw new Error(`API request failed: ${error}`);
  }
}
