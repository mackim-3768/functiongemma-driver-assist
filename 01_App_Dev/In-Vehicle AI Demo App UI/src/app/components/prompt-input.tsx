import { Send, Sparkles } from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import { useState } from "react";

interface PromptInputProps {
  onSend: (message: string) => void;
}

export function PromptInput({ onSend }: PromptInputProps) {
  const [input, setInput] = useState("");

  const handleSubmit = () => {
    if (input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-gray-950 border-t border-gray-800 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-gray-400 uppercase tracking-wider">Natural Language Input</span>
        </div>
        
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe the situation or enter a command..."
              className="bg-gray-900 border-gray-800 text-gray-200 placeholder:text-gray-600 h-12 pr-12 focus-visible:ring-cyan-500/50 focus-visible:border-cyan-500/50"
            />
          </div>
          
          <Button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className="h-12 px-6 bg-cyan-600 hover:bg-cyan-700 text-white disabled:bg-gray-800 disabled:text-gray-600"
          >
            <Send className="w-5 h-5 mr-2" />
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
