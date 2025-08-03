import React, { useState } from "react";
import type { CodeArtifact as CodeArtifactType } from "../../types/chat";
import {
  getFileExtension,
  downloadFile,
  copyToClipboard,
} from "../../utils/helpers";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { tomorrow } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Download, Copy, Check, Eye, FileCode } from "lucide-react";

interface CodeArtifactProps {
  artifact: CodeArtifactType;
  onPreview?: (artifact: CodeArtifactType) => void;
}

export const CodeArtifact: React.FC<CodeArtifactProps> = ({
  artifact,
  onPreview,
}) => {
  const [copied, setCopied] = useState(false);
  // const [showPreview, setShowPreview] = useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(artifact.content);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    const extension = getFileExtension(artifact.language);
    const filename = `${artifact.title || "code"}.${extension}`;
    downloadFile(artifact.content, filename);
  };

  const handlePreview = () => {
    if (onPreview) {
      onPreview(artifact);
    }
  };

  const canPreview =
    artifact.language.toLowerCase() === "html" ||
    artifact.language.toLowerCase() === "css" ||
    artifact.language.toLowerCase() === "javascript";

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <FileCode className="w-5 h-5 text-gray-600" />
          <div>
            <h3 className="font-medium text-gray-900">{artifact.title}</h3>
            <p className="text-sm text-gray-500">
              {artifact.language} • {artifact.content.length} characters
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {canPreview && (
            <button
              onClick={handlePreview}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
              title="Preview"
            >
              <Eye className="w-4 h-4" />
            </button>
          )}

          <button
            onClick={handleCopy}
            className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors"
            title="Copy to clipboard"
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-600" />
            ) : (
              <Copy className="w-4 h-4" />
            )}
          </button>

          <button
            onClick={handleDownload}
            className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            title="Download"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Description */}
      {artifact.description && (
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
          <p className="text-sm text-gray-600">{artifact.description}</p>
        </div>
      )}

      {/* Code Content */}
      <div className="relative">
        <SyntaxHighlighter
          language={artifact.language.toLowerCase()}
          style={tomorrow}
          customStyle={{
            margin: 0,
            borderRadius: 0,
            fontSize: "14px",
            lineHeight: "1.5",
          }}
          showLineNumbers
          wrapLines
        >
          {artifact.content}
        </SyntaxHighlighter>
      </div>

      {/* Metadata */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Created: {new Date(artifact.created_at).toLocaleString()}</span>
          <span>ID: {artifact.id.slice(0, 8)}...</span>
        </div>
      </div>
    </div>
  );
};
