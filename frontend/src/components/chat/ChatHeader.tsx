import { Bot, Code, Trash2 } from "lucide-react";
import React from "react";
import type { CodeArtifact } from "../../types/chat";

interface ChatHeaderProps {
  isConnected: boolean;
  sessionId: string;
  artifacts: CodeArtifact[];
  onToggleArtifacts: () => void;
  onClearChat: () => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  isConnected,
  sessionId,
  artifacts,
  onToggleArtifacts,
  onClearChat,
}) => {
  return (
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
              onClick={onToggleArtifacts}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors cursor-pointer"
            >
              <Code className="w-4 h-4" />
              {artifacts.length} Artifacts
            </button>
          )}

          <button
            onClick={onClearChat}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors cursor-pointer"
          >
            <Trash2 className="w-4 h-4" />
            Clear Chat
          </button>
        </div>
      </div>
    </div>
  );
}; 