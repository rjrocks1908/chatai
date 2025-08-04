import React from "react";
import { ChatHeader } from "./ChatHeader";
import { MessagesContainer } from "./MessagesContainer";
import { ChatInput } from "./ChatInput";
import { cn } from "../../utils/cn";
import type { ChatMessage, CodeArtifact } from "../../types/chat";
import ErrorBanner from "../ErrorBanner";

interface ChatAreaProps {
  messages: ChatMessage[];
  currentStreamingMessage: ChatMessage | null;
  isLoading: boolean;
  isConnected: boolean;
  sessionId: string;
  artifacts: CodeArtifact[];
  showArtifacts: boolean;
  onToggleArtifacts: () => void;
  onClearChat: () => void;
  onSendMessage: (content: string) => void;
  error: string | null;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  currentStreamingMessage,
  isLoading,
  isConnected,
  sessionId,
  artifacts,
  showArtifacts,
  onToggleArtifacts,
  onClearChat,
  onSendMessage,
  error,
}) => {
  return (
    <div
      className={cn(
        "flex flex-col transition-all duration-300 ease-in-out",
        showArtifacts && artifacts.length > 0 ? "w-[60%]" : "w-full"
      )}
    >
      {/* Header */}
      <ChatHeader
        isConnected={isConnected}
        sessionId={sessionId}
        artifacts={artifacts}
        onToggleArtifacts={onToggleArtifacts}
        onClearChat={onClearChat}
      />

      {/* Error Banner */}
      {error && <ErrorBanner error={error} />}

      {/* Messages */}
      <MessagesContainer
        messages={messages}
        currentStreamingMessage={currentStreamingMessage}
        isLoading={isLoading}
      />

      {/* Input */}
      <ChatInput
        onSendMessage={onSendMessage}
        disabled={isLoading || !isConnected}
        placeholder={
          !isConnected ? "Connecting to AI service..." : "Ask me anything..."
        }
      />
    </div>
  );
};
