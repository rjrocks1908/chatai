import { AlertCircle } from "lucide-react";

interface ErrorBannerProps {
  error: string;
}

function ErrorBanner({ error }: ErrorBannerProps) {
  return (
    <div className="bg-red-50 border-b border-red-200 px-6 py-3">
      <div className="flex items-center gap-2 text-red-800">
        <AlertCircle className="w-4 h-4" />
        <span className="text-sm">{error}</span>
      </div>
    </div>
  );
}
export default ErrorBanner;
