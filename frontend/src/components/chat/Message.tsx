import React, { useEffect, useState } from "react";
import type { ChatMessage, CodeArtifact } from "../../types/chat";
import { cn } from "../../utils/cn";
import {
  downloadFile,
  formatTimestamp,
  getFileExtension,
  isFrontendCode,
} from "../../utils/helpers";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { User, Bot, Code, Download, Eye } from "lucide-react";
import { useAppSelector } from "../../store/hooks";

interface MessageProps {
  message: ChatMessage;
  isStreaming?: boolean;
  onPreviewArtifact?: (artifact: CodeArtifact) => void;
}

export const Message: React.FC<MessageProps> = ({
  message,
  isStreaming = false,
  onPreviewArtifact,
}) => {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";

  const { messageArtifacts } = useAppSelector((state) => state.chat);
  const [isPreviewed, setIsPreviewed] = useState(false);

  useEffect(() => {
    if (messageArtifacts[message.id]) {
      setIsPreviewed(messageArtifacts[message.id].some(isFrontendCode));
    }
  }, [messageArtifacts, message.id]);

  const handleDownload = (artifact: CodeArtifact) => {
    const extension = getFileExtension(artifact.language);
    const filename = `${artifact.title || "code"}.${extension}`;
    downloadFile(artifact.content, filename);
  };

  return (
    <div
      className={cn(
        "flex gap-4 p-4 transition-colors",
        isUser
          ? "bg-blue-50 border-l-4 border-blue-500"
          : "bg-gray-50 border-l-4 border-gray-300",
        isStreaming && isAssistant && "animate-pulse"
      )}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
        ) : (
          <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <span className="font-medium text-sm">
            {isUser ? "You" : "AI Assistant"}
          </span>
          <span className="text-xs text-gray-500">
            {formatTimestamp(message.timestamp)}
          </span>
          {isStreaming && isAssistant && (
            <span className="text-xs text-blue-500 animate-pulse">
              typing...
            </span>
          )}
        </div>

        {/* Content */}
        <div className="prose prose-sm max-w-none">
          {isAssistant ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                code({ inline, className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || "");
                  return !inline && match ? (
                    <pre className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto">
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                  ) : (
                    <code
                      className="bg-gray-200 px-1 py-0.5 rounded text-sm"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                pre({ children }) {
                  return <div className="my-4">{children}</div>;
                },
                p({ children }) {
                  return <p className="mb-4 last:mb-0">{children}</p>;
                },
                ul({ children }) {
                  return (
                    <ul className="list-disc list-inside mb-4 space-y-1">
                      {children}
                    </ul>
                  );
                },
                ol({ children }) {
                  return (
                    <ol className="list-decimal list-inside mb-4 space-y-1">
                      {children}
                    </ol>
                  );
                },
                blockquote({ children }) {
                  return (
                    <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-600 mb-4">
                      {children}
                    </blockquote>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          ) : (
            <div className="text-gray-900 whitespace-pre-wrap">
              {message.content}
            </div>
          )}
        </div>

        {/* Artifacts Section */}
        {messageArtifacts[message.id] && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Code className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">
                Generated Code ({messageArtifacts[message.id].length})
              </span>
            </div>
            <div className="space-y-2">
              {messageArtifacts[message.id].map((artifact) => (
                <div
                  key={artifact.id}
                  className="flex items-center justify-between p-2 bg-white rounded border border-blue-100"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {artifact.title || `Code (${artifact.language})`}
                    </div>
                    {artifact.description && (
                      <div className="text-xs text-gray-500 truncate">
                        {artifact.description}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-1 ml-2">
                    {onPreviewArtifact && isPreviewed && (
                      <button
                        onClick={() => onPreviewArtifact(artifact)}
                        className="p-1 text-blue-600 hover:text-blue-700 hover:bg-blue-100 rounded transition-colors cursor-pointer"
                        title="Preview"
                      >
                        <Eye className="w-3 h-3" />
                      </button>
                    )}

                    <button
                      onClick={() => handleDownload(artifact)}
                      className="p-1 text-green-600 hover:text-green-700 hover:bg-green-100 rounded transition-colors cursor-pointer"
                      title="Download"
                    >
                      <Download className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
