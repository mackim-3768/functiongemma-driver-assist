import { Send, Sparkles, X } from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/app/components/ui/dialog";
import { useState } from "react";

interface PromptDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSend: (message: string) => void;
}

export function PromptDialog({ open, onOpenChange, onSend }: PromptDialogProps) {
  const [input, setInput] = useState("");

  const handleSubmit = () => {
    if (input.trim()) {
      onSend(input);
      setInput("");
      onOpenChange(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] bg-gray-950 border-cyan-900/50 text-gray-100">
        <DialogHeader>
          <DialogTitle className="text-gray-100 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            Natural Language Input
          </DialogTitle>
          <p className="text-xs text-gray-500">Describe a situation or enter a command</p>
        </DialogHeader>

        <div className="mt-4">
          <div className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., 'Driver appears drowsy and drifting left'"
              className="bg-gray-900 border-gray-800 text-gray-200 placeholder:text-gray-600 h-12 focus-visible:ring-cyan-500/50 focus-visible:border-cyan-500/50"
              autoFocus
            />
            
            <Button
              onClick={handleSubmit}
              disabled={!input.trim()}
              className="h-12 px-6 bg-cyan-600 hover:bg-cyan-700 text-white disabled:bg-gray-800 disabled:text-gray-600"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>

          <div className="mt-4 space-y-2">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Examples:</p>
            <div className="space-y-1">
              {[
                "Driver is drowsy",
                "Lane departure detected",
                "Hands off steering wheel"
              ].map((example, i) => (
                <button
                  key={i}
                  onClick={() => setInput(example)}
                  className="block w-full text-left text-xs text-gray-400 hover:text-cyan-400 p-2 rounded bg-gray-900/30 hover:bg-gray-900/50 transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
