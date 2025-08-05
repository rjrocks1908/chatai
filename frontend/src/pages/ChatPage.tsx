import React, { useEffect } from "react";
import { getArtifact, healthCheck, sendMessageStream } from "../api";
import { ArtifactsPanel } from "../components/chat/ArtifactsPanel";
import { ChatArea } from "../components/chat/ChatArea";
import { CodePreview } from "../components/chat/CodePreview";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
  addArtifacts,
  addUserMessage,
  clearChat,
  completeStreamingMessage,
  initializeSession,
  setConnected,
  setError,
  setLoading,
  setPreviewArtifacts,
  setShowArtifacts,
  setShowPreview,
  startStreamingMessage,
  toggleArtifacts,
  updateStreamingMessage,
} from "../store/slices/chatSlice";
import type { CodeArtifact, StreamChunk } from "../types/chat";
import { downloadFile, getFileExtension } from "../utils/helpers";

export const ChatPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const {
    messages,
    isLoading,
    sessionId,
    currentStreamingMessage,
    artifacts,
    showArtifacts,
    showPreview,
    previewArtifacts,
    error,
    isConnected,
  } = useAppSelector((state) => state.chat);

  // Initialize session and check connection
  useEffect(() => {
    dispatch(initializeSession());

    const checkConnection = async () => {
      try {
        await healthCheck();
        dispatch(setConnected(true));
        dispatch(setError(null));
      } catch (err) {
        console.error("Error checking connection:", err);
        dispatch(setConnected(false));
        dispatch(
          setError(
            "Unable to connect to the AI service. Please check your connection."
          )
        );
      }
    };

    checkConnection();
  }, [dispatch]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    dispatch(setLoading(true));
    dispatch(setError(null));
    dispatch(addUserMessage(content));

    // Create the streaming message ID here so we can use it in the callback
    const streamingMessageId = `assistant_${Date.now()}`;
    dispatch(startStreamingMessage(streamingMessageId));

    try {
      await sendMessageStream(
        { message: content, session_id: sessionId, stream: true },
        (chunk: StreamChunk) => {
          dispatch(updateStreamingMessage(chunk.chunk));

          if (
            chunk.has_artifacts &&
            chunk.artifacts &&
            chunk.artifacts.length > 0
          ) {
            // Use the streaming message ID we created above
            fetchArtifacts(chunk.artifacts, streamingMessageId);
          }
        },
        () => {
          dispatch(completeStreamingMessage());
          dispatch(setLoading(false));
        },
        (error: string) => {
          dispatch(setError(error));
          dispatch(setLoading(false));
        }
      );
    } catch (err) {
      dispatch(
        setError(err instanceof Error ? err.message : "Failed to send message")
      );
      dispatch(setLoading(false));
    }
  };

  const fetchArtifacts = async (artifactIds: string[], messageId: string) => {
    try {
      const artifactPromises = artifactIds.map((id) => getArtifact(id));
      const fetchedArtifacts = await Promise.all(artifactPromises);
      dispatch(addArtifacts({ messageId, artifacts: fetchedArtifacts }));
    } catch (err) {
      console.error("Failed to fetch artifacts:", err);
    }
  };

  const handlePreviewArtifact = (artifact: CodeArtifact) => {
    dispatch(setPreviewArtifacts([artifact]));
    dispatch(setShowPreview(true));
  };

  const handleClearChat = () => {
    dispatch(clearChat());
  };

  const handleDownloadAllArtifacts = async () => {
    for (const artifact of artifacts) {
      const extension = getFileExtension(artifact.language);
      const filename = `${artifact.title || "code"}.${extension}`;
      downloadFile(artifact.content, filename);
    }
  };

  const handleToggleArtifacts = () => {
    dispatch(toggleArtifacts());
  };

  const handleCloseArtifacts = () => {
    dispatch(setShowArtifacts(false));
  };

  const handleClosePreview = () => {
    dispatch(setShowPreview(false));
  };

  return (
    <div className="flex h-screen bg-gray-50 w-full overflow-hidden">
      <ChatArea
        messages={messages}
        currentStreamingMessage={currentStreamingMessage}
        isLoading={isLoading}
        isConnected={isConnected}
        sessionId={sessionId}
        artifacts={artifacts}
        showArtifacts={showArtifacts}
        onToggleArtifacts={handleToggleArtifacts}
        onClearChat={handleClearChat}
        onSendMessage={handleSendMessage}
        onPreviewArtifact={handlePreviewArtifact}
        error={error}
      />

      <ArtifactsPanel
        artifacts={artifacts}
        showArtifacts={showArtifacts}
        onClose={handleCloseArtifacts}
        onPreviewArtifact={handlePreviewArtifact}
        onDownloadAllArtifacts={handleDownloadAllArtifacts}
      />

      <CodePreview
        artifacts={previewArtifacts}
        isOpen={showPreview}
        onClose={handleClosePreview}
      />
    </div>
  );
};
