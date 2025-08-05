import React, { useRef, useEffect } from "react";
import { Message } from "./Message";
import { WelcomeMessage } from "./WelcomeMessage";
import type { ChatMessage, CodeArtifact } from "../../types/chat";

interface MessagesContainerProps {
  messages: ChatMessage[];
  currentStreamingMessage: ChatMessage | null;
  isLoading: boolean;
  onPreviewArtifact?: (artifact: CodeArtifact) => void;
}

export const MessagesContainer: React.FC<MessagesContainerProps> = ({
  messages,
  currentStreamingMessage,
  isLoading,
  onPreviewArtifact,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentStreamingMessage]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.length === 0 && !isLoading && <WelcomeMessage />}

      {messages.map((message) => (
        <Message 
          key={message.id} 
          message={message} 
          onPreviewArtifact={onPreviewArtifact}
        />
      ))}

      {currentStreamingMessage && (
        <Message 
          message={currentStreamingMessage} 
          isStreaming={true}
          onPreviewArtifact={onPreviewArtifact}
        />
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}; 