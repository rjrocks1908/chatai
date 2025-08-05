import React from "react";
import { CodeArtifact as CodeArtifactComponent } from "./CodeArtifact";
import { cn } from "../../utils/cn";
import type { CodeArtifact } from "../../types/chat";
import { X } from "lucide-react";

interface ArtifactsPanelProps {
  artifacts: CodeArtifact[];
  showArtifacts: boolean;
  onClose: () => void;
  onPreviewArtifact: (artifact: CodeArtifact) => void;
  onDownloadAllArtifacts: () => void;
}

export const ArtifactsPanel: React.FC<ArtifactsPanelProps> = ({
  artifacts,
  showArtifacts,
  onClose,
  onPreviewArtifact,
  onDownloadAllArtifacts,
}) => {
  return (
    <div
      className={cn(
        "bg-white border-l border-gray-200 flex flex-col transition-all duration-300 ease-in-out",
        showArtifacts && artifacts.length > 0
          ? "w-[40%] translate-x-0 opacity-100"
          : "w-0 translate-x-full opacity-0"
      )}
    >
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">
            Generated Code
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-4 h-4 cursor-pointer" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">
            {artifacts.length} artifact{artifacts.length !== 1 ? "s" : ""}
          </span>

          <button
            onClick={onDownloadAllArtifacts}
            className="text-sm text-green-600 hover:text-green-700 transition-colors cursor-pointer"
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
            onPreview={onPreviewArtifact}
          />
        ))}
      </div>
    </div>
  );
};
