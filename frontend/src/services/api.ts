// Create a unified API service object for backward compatibility
import * as chatApis from "../api/backend/chatApis";
import * as artifactApis from "../api/backend/artifactApis";
import * as healthApis from "../api/backend/healthApis";

export const apiService = {
  // Chat methods
  sendMessage: chatApis.sendMessage,
  sendMessageStream: chatApis.sendMessageStream,
  getSessionHistory: chatApis.getSessionHistory,
  clearSession: chatApis.clearSession,
  getSessionStats: chatApis.getSessionStats,

  // Artifact methods
  getArtifacts: artifactApis.getArtifacts,
  getArtifact: artifactApis.getArtifact,
  downloadArtifact: artifactApis.downloadArtifact,

  // Health methods
  healthCheck: healthApis.healthCheck,
};

export default apiService;
