import { Sparkles } from "lucide-react";
import React from "react";

export const WelcomeMessage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
        <Sparkles className="w-8 h-8 text-blue-600" />
      </div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Welcome to AI Coding Assistant
      </h2>
      <p className="text-gray-600 max-w-md">
        Ask me to create code, explain concepts, or help you build something
        amazing. I can generate code artifacts and provide live previews for
        frontend code.
      </p>
    </div>
  );
}; 