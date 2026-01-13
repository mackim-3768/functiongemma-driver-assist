import { MessageSquare, List } from "lucide-react";
import { Button } from "@/app/components/ui/button";

interface BottomActionBarProps {
  onScenariosClick: () => void;
  onPromptClick: () => void;
}

export function BottomActionBar({ onScenariosClick, onPromptClick }: BottomActionBarProps) {
  return (
    <div className="bg-gray-950 border-t border-gray-800 px-4 py-3">
      <div className="flex gap-3 max-w-md mx-auto">
        <Button
          onClick={onScenariosClick}
          className="flex-1 h-12 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-200 hover:text-cyan-400 hover:border-cyan-500/50"
        >
          <List className="w-5 h-5 mr-2" />
          Scenarios
        </Button>
        
        <Button
          onClick={onPromptClick}
          className="flex-1 h-12 bg-cyan-600 hover:bg-cyan-700 text-white"
        >
          <MessageSquare className="w-5 h-5 mr-2" />
          Prompt
        </Button>
      </div>
    </div>
  );
}
