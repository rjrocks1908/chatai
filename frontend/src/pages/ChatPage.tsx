import { Bot, Code, Sparkles, Trash2 } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import { ChatInput } from "../components/chat/ChatInput";
import { CodeArtifact as CodeArtifactComponent } from "../components/chat/CodeArtifact";
import { CodePreview } from "../components/chat/CodePreview";
import { Message } from "../components/chat/Message";
import ErrorBanner from "../components/ErrorBanner";
import type { ChatMessage, CodeArtifact, StreamChunk } from "../types/chat";
import { generateSessionId } from "../utils/helpers";
import {
  downloadArtifact,
  getArtifact,
  healthCheck,
  sendMessageStream,
} from "../api";

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const [currentStreamingMessage, setCurrentStreamingMessage] =
    useState<ChatMessage | null>(null);
  const [artifacts, setArtifacts] = useState<CodeArtifact[]>([]);
  const [showArtifacts, setShowArtifacts] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewArtifacts, setPreviewArtifacts] = useState<CodeArtifact[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Initialize session
  useEffect(() => {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentStreamingMessage]);

  // Check API connection
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await healthCheck();
        setIsConnected(true);
        setError(null);
      } catch (err) {
        console.error("Failed to check connection:", err);
        setIsConnected(false);
        setError(
          "Unable to connect to the AI service. Please check your connection."
        );
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    // Add user message
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Create streaming message placeholder
    const streamingMessage: ChatMessage = {
      id: `assistant_${Date.now()}`,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    };

    setCurrentStreamingMessage(streamingMessage);

    try {
      await sendMessageStream(
        { message: content, session_id: sessionId, stream: true },
        (chunk: StreamChunk) => {
          // Update streaming message
          setCurrentStreamingMessage((prev) =>
            prev ? { ...prev, content: prev.content + chunk.chunk } : null
          );

          // If artifacts are available, fetch them
          if (
            chunk.has_artifacts &&
            chunk.artifacts &&
            chunk.artifacts.length > 0
          ) {
            fetchArtifacts(chunk.artifacts);
          }
        },
        () => {
          // Stream complete
          if (currentStreamingMessage) {
            setMessages((prev) => [...prev, currentStreamingMessage]);
            setCurrentStreamingMessage(null);
          }
          setIsLoading(false);
        },
        (error: string) => {
          setError(error);
          setIsLoading(false);
          setCurrentStreamingMessage(null);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      setIsLoading(false);
      setCurrentStreamingMessage(null);
    }
  };

  const fetchArtifacts = async (artifactIds: string[]) => {
    try {
      const artifactPromises = artifactIds.map((id) => getArtifact(id));
      const fetchedArtifacts = await Promise.all(artifactPromises);
      setArtifacts(fetchedArtifacts);
      setShowArtifacts(true);
    } catch (err) {
      console.error("Failed to fetch artifacts:", err);
    }
  };

  const handlePreviewArtifact = (artifact: CodeArtifact) => {
    setPreviewArtifacts([artifact]);
    setShowPreview(true);
  };

  const handlePreviewAllArtifacts = () => {
    setPreviewArtifacts(artifacts);
    setShowPreview(true);
  };

  const clearChat = () => {
    setMessages([]);
    setArtifacts([]);
    setShowArtifacts(false);
    setCurrentStreamingMessage(null);
    setError(null);

    // Generate new session
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
  };

  const downloadAllArtifacts = async () => {
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
      setError("Failed to download artifacts");
    }
  };

  const hasFrontendArtifacts = artifacts.some((artifact) =>
    ["html", "css", "javascript", "react", "jsx", "tsx"].includes(
      artifact.language.toLowerCase()
    )
  );

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  AI Coding Assistant
                </h1>
                <p className="text-sm text-gray-500">
                  {isConnected ? "Connected" : "Disconnected"} • Session:{" "}
                  {sessionId.slice(0, 8)}...
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {artifacts.length > 0 && (
                <button
                  onClick={() => setShowArtifacts(!showArtifacts)}
                  className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                >
                  <Code className="w-4 h-4" />
                  {artifacts.length} Artifacts
                </button>
              )}

              <button
                onClick={clearChat}
                className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                Clear Chat
              </button>
            </div>
          </div>
        </div>

        {/* Error Banner */}
        {error && <ErrorBanner error={error} />}

        {/* Messages */}
        <div
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto p-6 space-y-4"
        >
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Welcome to AI Coding Assistant
              </h2>
              <p className="text-gray-600 max-w-md">
                Ask me to create code, explain concepts, or help you build
                something amazing. I can generate code artifacts and provide
                live previews for frontend code.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}

          {currentStreamingMessage && (
            <Message message={currentStreamingMessage} isStreaming={true} />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading || !isConnected}
          placeholder={
            !isConnected ? "Connecting to AI service..." : "Ask me anything..."
          }
        />
      </div>

      {/* Artifacts Panel */}
      {showArtifacts && artifacts.length > 0 && (
        <div className="w-96 bg-white border-l border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-gray-900">
                Generated Code
              </h2>
              <button
                onClick={() => setShowArtifacts(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">
                {artifacts.length} artifact{artifacts.length !== 1 ? "s" : ""}
              </span>

              {hasFrontendArtifacts && (
                <button
                  onClick={handlePreviewAllArtifacts}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  Preview All
                </button>
              )}

              <button
                onClick={downloadAllArtifacts}
                className="text-sm text-green-600 hover:text-green-700"
              >
                Download All
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {artifacts.map((artifact) => (
              <CodeArtifactComponent
                key={artifact.id}
                artifact={artifact}
                onPreview={handlePreviewArtifact}
              />
            ))}
          </div>
        </div>
      )}

      {/* Code Preview Modal */}
      <CodePreview
        artifacts={previewArtifacts}
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
      />
    </div>
  );
};
