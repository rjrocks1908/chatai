import type { CodeArtifact } from "../types/chat";

// Generate a unique session ID
export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Get file extension from language
export function getFileExtension(language: string): string {
  const extensions: Record<string, string> = {
    javascript: "js",
    typescript: "ts",
    python: "py",
    html: "html",
    css: "css",
    scss: "scss",
    sass: "sass",
    json: "json",
    markdown: "md",
    react: "jsx",
    jsx: "jsx",
    tsx: "tsx",
    php: "php",
    java: "java",
    csharp: "cs",
    cpp: "cpp",
    c: "c",
    rust: "rs",
    go: "go",
    ruby: "rb",
    swift: "swift",
    kotlin: "kt",
  };
  return extensions[language.toLowerCase()] || "txt";
}

// Download a file
export function downloadFile(
  content: string,
  filename: string,
  mimeType: string = "text/plain"
) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Format timestamp
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleString();
}

// Check if artifact is frontend code (can be previewed)
export function isFrontendCode(artifact: CodeArtifact): boolean {
  const frontendTypes = ["html", "css", "javascript", "react", "jsx", "tsx"];
  return (
    frontendTypes.includes(artifact.language.toLowerCase()) ||
    frontendTypes.includes(artifact.type.toLowerCase())
  );
}

// Generate preview HTML for frontend artifacts
export function generatePreviewHTML(artifacts: CodeArtifact[]): string {
  let html = "";
  let css = "";
  let js = "";

  // Extract different types of code
  artifacts.forEach((artifact) => {
    switch (artifact.language.toLowerCase()) {
      case "html":
        html += artifact.content;
        break;
      case "css":
        css += artifact.content;
        break;
      case "javascript":
      case "js":
        js += artifact.content;
        break;
      case "react":
      case "jsx":
      case "tsx":
        // For React components, we'll need to handle them differently
        // For now, just add as JS
        js += artifact.content;
        break;
    }
  });

  // If no HTML provided, create a basic structure
  if (!html) {
    html = '<div id="app"></div>';
  }

  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Preview</title>
        <style>${css}</style>
    </head>
    <body>
        ${html}
        <script>${js}</script>
    </body>
    </html>
  `;
}

// Copy text to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error("Failed to copy to clipboard:", err);
    // Fallback for older browsers
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand("copy");
      document.body.removeChild(textArea);
      return true;
    } catch (fallbackErr) {
      console.error("Failed to copy to clipboard:", fallbackErr);
      document.body.removeChild(textArea);
      return false;
    }
  }
}
