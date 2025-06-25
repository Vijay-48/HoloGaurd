
import { toast } from "sonner";

// Re-export toast from sonner for compatibility
export { toast };

// Simple hook for consistency with existing code
export const useToast = () => {
  return { toast };
};
