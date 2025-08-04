// import React, { useEffect, useState } from "react";
// import { ArtifactsPanel } from "../components/chat/ArtifactsPanel";
// import { ChatArea } from "../components/chat/ChatArea";
// import { CodePreview } from "../components/chat/CodePreview";
// import {
//   healthCheck,
//   sendMessageStream,
//   getArtifact,
//   downloadArtifact,
// } from "../api";
// import type { ChatMessage, CodeArtifact, StreamChunk } from "../types/chat";
// import { generateSessionId } from "../utils/helpers";

// export const ChatPage: React.FC = () => {
//   const [messages, setMessages] = useState<ChatMessage[]>([]);
//   const [isLoading, setIsLoading] = useState(false);
//   const [sessionId, setSessionId] = useState<string>("");
//   const [currentStreamingMessage, setCurrentStreamingMessage] =
//     useState<ChatMessage | null>(null);
//   const [artifacts, setArtifacts] = useState<CodeArtifact[]>([]);
//   const [showArtifacts, setShowArtifacts] = useState(false);
//   const [showPreview, setShowPreview] = useState(false);
//   const [previewArtifacts, setPreviewArtifacts] = useState<CodeArtifact[]>([]);
//   const [error, setError] = useState<string | null>(null);
//   const [isConnected, setIsConnected] = useState(true);

//   // Initialize session and check connection
//   useEffect(() => {
//     const newSessionId = generateSessionId();
//     setSessionId(newSessionId);

//     const checkConnection = async () => {
//       try {
//         await healthCheck();
//         setIsConnected(true);
//         setError(null);
//       } catch (err) {
//         console.error("Error checking connection:", err);
//         setIsConnected(false);
//         setError(
//           "Unable to connect to the AI service. Please check your connection."
//         );
//       }
//     };

//     checkConnection();
//   }, []);

//   const handleSendMessage = async (content: string) => {
//     if (!content.trim() || isLoading) return;

//     setIsLoading(true);
//     setError(null);

//     // Add user message
//     const userMessage: ChatMessage = {
//       id: `user_${Date.now()}`,
//       role: "user",
//       content,
//       timestamp: new Date().toISOString(),
//     };

//     setMessages((prev) => [...prev, userMessage]);

//     // Create streaming message placeholder
//     const streamingMessage: ChatMessage = {
//       id: `assistant_${Date.now()}`,
//       role: "assistant",
//       content: "",
//       timestamp: new Date().toISOString(),
//     };

//     setCurrentStreamingMessage(streamingMessage);

//     try {
//       await sendMessageStream(
//         { message: content, session_id: sessionId, stream: true },
//         (chunk: StreamChunk) => {
//           // Update streaming message
//           setCurrentStreamingMessage((prev) =>
//             prev ? { ...prev, content: prev.content + chunk.chunk } : null
//           );

//           // If artifacts are available, fetch them
//           if (
//             chunk.has_artifacts &&
//             chunk.artifacts &&
//             chunk.artifacts.length > 0
//           ) {
//             fetchArtifacts(chunk.artifacts);
//           }
//         },
//         () => {
//           // Stream complete
//           console.log("Stream complete");
//           if (currentStreamingMessage) {
//             console.log("Adding streaming message to messages");
//             setMessages((prev) => [...prev, currentStreamingMessage]);
//             setCurrentStreamingMessage(null);
//           }
//           setIsLoading(false);
//         },
//         (error: string) => {
//           setError(error);
//           setIsLoading(false);
//           setCurrentStreamingMessage(null);
//         }
//       );
//     } catch (err) {
//       setError(err instanceof Error ? err.message : "Failed to send message");
//       setIsLoading(false);
//       setCurrentStreamingMessage(null);
//     }
//   };

//   const fetchArtifacts = async (artifactIds: string[]) => {
//     try {
//       const artifactPromises = artifactIds.map((id) => getArtifact(id));
//       const fetchedArtifacts = await Promise.all(artifactPromises);
//       setArtifacts(fetchedArtifacts);
//       setShowArtifacts(true);
//     } catch (err) {
//       console.error("Failed to fetch artifacts:", err);
//     }
//   };

//   const handlePreviewArtifact = (artifact: CodeArtifact) => {
//     setPreviewArtifacts([artifact]);
//     setShowPreview(true);
//   };

//   const handlePreviewAllArtifacts = () => {
//     setPreviewArtifacts(artifacts);
//     setShowPreview(true);
//   };

//   const handleClearChat = () => {
//     setMessages([]);
//     setArtifacts([]);
//     setShowArtifacts(false);
//     setCurrentStreamingMessage(null);
//     setError(null);

//     // Generate new session
//     const newSessionId = generateSessionId();
//     setSessionId(newSessionId);
//   };

//   const handleDownloadAllArtifacts = async () => {
//     try {
//       for (const artifact of artifacts) {
//         const blob = await downloadArtifact(artifact.id);
//         const url = URL.createObjectURL(blob);
//         const link = document.createElement("a");
//         link.href = url;
//         link.download = `${artifact.title || "code"}.${artifact.language}`;
//         document.body.appendChild(link);
//         link.click();
//         document.body.removeChild(link);
//         URL.revokeObjectURL(url);
//       }
//     } catch (err) {
//       console.error("Failed to download artifacts:", err);
//       setError("Failed to download artifacts");
//     }
//   };

//   const handleToggleArtifacts = () => {
//     setShowArtifacts(!showArtifacts);
//   };

//   const handleCloseArtifacts = () => {
//     setShowArtifacts(false);
//   };

//   const handleClosePreview = () => {
//     setShowPreview(false);
//   };

//   return (
//     <div className="flex h-screen bg-gray-50 w-full overflow-hidden">
//       <ChatArea
//         messages={messages}
//         currentStreamingMessage={currentStreamingMessage}
//         isLoading={isLoading}
//         isConnected={isConnected}
//         sessionId={sessionId}
//         artifacts={artifacts}
//         showArtifacts={showArtifacts}
//         onToggleArtifacts={handleToggleArtifacts}
//         onClearChat={handleClearChat}
//         onSendMessage={handleSendMessage}
//         error={error}
//       />

//       <ArtifactsPanel
//         artifacts={artifacts}
//         showArtifacts={showArtifacts}
//         onClose={handleCloseArtifacts}
//         onPreviewArtifact={handlePreviewArtifact}
//         onPreviewAllArtifacts={handlePreviewAllArtifacts}
//         onDownloadAllArtifacts={handleDownloadAllArtifacts}
//       />

//       <CodePreview
//         artifacts={previewArtifacts}
//         isOpen={showPreview}
//         onClose={handleClosePreview}
//       />
//     </div>
//   );
// };

import React, { useEffect } from "react";
import { ArtifactsPanel } from "../components/chat/ArtifactsPanel";
import { ChatArea } from "../components/chat/ChatArea";
import { CodePreview } from "../components/chat/CodePreview";
import { useAppSelector, useAppDispatch } from "../store/hooks";
import {
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
} from "../store/slices/chatSlice";
import {
  healthCheck,
  sendMessageStream,
  getArtifact,
  downloadArtifact,
} from "../api";
import type { CodeArtifact, StreamChunk } from "../types/chat";

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
    dispatch(startStreamingMessage());

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
            fetchArtifacts(chunk.artifacts);
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

  const fetchArtifacts = async (artifactIds: string[]) => {
    try {
      const artifactPromises = artifactIds.map((id) => getArtifact(id));
      const fetchedArtifacts = await Promise.all(artifactPromises);
      dispatch(setArtifacts(fetchedArtifacts));
    } catch (err) {
      console.error("Failed to fetch artifacts:", err);
    }
  };

  const handlePreviewArtifact = (artifact: CodeArtifact) => {
    dispatch(setPreviewArtifacts([artifact]));
    dispatch(setShowPreview(true));
  };

  const handlePreviewAllArtifacts = () => {
    dispatch(setPreviewArtifacts(artifacts));
    dispatch(setShowPreview(true));
  };

  const handleClearChat = () => {
    dispatch(clearChat());
  };

  const handleDownloadAllArtifacts = async () => {
    try {
      for (const artifact of artifacts) {
        const blob = await downloadArtifact(artifact.id);
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${artifact.title || "code"}.${artifact.language}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error("Failed to download artifacts:", err);
      dispatch(setError("Failed to download artifacts"));
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
        error={error}
      />

      <ArtifactsPanel
        artifacts={artifacts}
        showArtifacts={showArtifacts}
        onClose={handleCloseArtifacts}
        onPreviewArtifact={handlePreviewArtifact}
        onPreviewAllArtifacts={handlePreviewAllArtifacts}
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
