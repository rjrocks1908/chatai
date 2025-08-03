import React, { useState, useEffect, useRef } from "react";
import type { CodeArtifact } from "../../types/chat";
import { cn } from "../../utils/cn";
import { generatePreviewHTML } from "../../utils/helpers";
import { X, RefreshCw, ExternalLink } from "lucide-react";

interface CodePreviewProps {
  artifacts: CodeArtifact[];
  isOpen: boolean;
  onClose: () => void;
}

export const CodePreview: React.FC<CodePreviewProps> = ({
  artifacts,
  isOpen,
  onClose,
}) => {
  const [previewHtml, setPreviewHtml] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (isOpen && artifacts.length > 0) {
      generatePreview();
    }
  }, [isOpen, artifacts]);

  const generatePreview = () => {
    setIsLoading(true);
    const html = generatePreviewHTML(artifacts);
    setPreviewHtml(html);

    // Small delay to ensure iframe is ready
    setTimeout(() => {
      setIsLoading(false);
    }, 100);
  };

  const refreshPreview = () => {
    generatePreview();
  };

  const openInNewTab = () => {
    const blob = new Blob([previewHtml], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-900">
              Code Preview
            </h2>
            <span className="text-sm text-gray-500">
              {artifacts.length} artifact{artifacts.length !== 1 ? "s" : ""}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={refreshPreview}
              disabled={isLoading}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors disabled:opacity-50"
              title="Refresh preview"
            >
              <RefreshCw
                className={cn("w-4 h-4", isLoading && "animate-spin")}
              />
            </button>

            <button
              onClick={openInNewTab}
              className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors"
              title="Open in new tab"
            >
              <ExternalLink className="w-4 h-4" />
            </button>

            <button
              onClick={onClose}
              className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
              title="Close preview"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Preview Content */}
        <div className="flex-1 relative">
          {isLoading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
              <div className="flex items-center gap-2">
                <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
                <span className="text-gray-600">Generating preview...</span>
              </div>
            </div>
          ) : (
            <iframe
              ref={iframeRef}
              srcDoc={previewHtml}
              className="w-full h-full border-0"
              title="Code Preview"
              sandbox="allow-scripts allow-same-origin"
            />
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center gap-4">
              <span>
                Preview generated from {artifacts.length} code artifact
                {artifacts.length !== 1 ? "s" : ""}
              </span>
              <span>•</span>
              <span>Click refresh to update</span>
            </div>
            <div className="flex items-center gap-2">
              {artifacts.map((artifact) => (
                <span
                  key={artifact.id}
                  className="px-2 py-1 bg-white border border-gray-200 rounded text-xs"
                >
                  {artifact.language}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
