import { ChevronLeft, ChevronRight, Code, Database, Terminal } from "lucide-react";
import { useState } from "react";
import { ScrollArea } from "@/app/components/ui/scroll-area";

interface DebugPanelProps {
  contextData: object;
  aiOutput: object | null;
  actionLog: string[];
}

export function DebugPanel({ contextData, aiOutput, actionLog }: DebugPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className={`h-full bg-gray-950 border-l border-gray-800 transition-all duration-300 ${isCollapsed ? "w-12" : "w-96"}`}>
      {/* Collapse Toggle */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute top-4 -left-3 bg-gray-900 border border-gray-800 rounded-full p-1 hover:bg-gray-800 transition-colors z-10"
      >
        {isCollapsed ? (
          <ChevronLeft className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {!isCollapsed && (
        <div className="h-full flex flex-col p-4">
          <div className="mb-6">
            <h2 className="text-sm uppercase tracking-wider text-gray-400 mb-1 flex items-center gap-2">
              <Code className="w-4 h-4" />
              Debug Console
            </h2>
            <div className="h-px bg-gradient-to-r from-cyan-500/50 to-transparent"></div>
          </div>

          <ScrollArea className="flex-1">
            {/* Context Snapshot */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-4 h-4 text-blue-400" />
                <h3 className="text-xs uppercase tracking-wider text-gray-400">Context Snapshot</h3>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 font-mono text-xs">
                <pre className="text-gray-300 overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(contextData, null, 2)}
                </pre>
              </div>
            </div>

            {/* FunctionGemma Output */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs uppercase tracking-wider text-gray-400">FunctionGemma Output</h3>
              </div>
              <div className="bg-gray-900 border border-cyan-900/50 rounded-lg p-3 font-mono text-xs">
                {aiOutput ? (
                  <pre className="text-cyan-300 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(aiOutput, null, 2)}
                  </pre>
                ) : (
                  <div className="text-gray-600 italic">Waiting for AI decision...</div>
                )}
              </div>
            </div>

            {/* Action Execution Log */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Terminal className="w-4 h-4 text-green-400" />
                <h3 className="text-xs uppercase tracking-wider text-gray-400">Action Log</h3>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 font-mono text-xs">
                {actionLog.length > 0 ? (
                  <div className="space-y-1">
                    {actionLog.map((log, index) => (
                      <div key={index} className="text-green-400">
                        <span className="text-gray-600">[{new Date().toLocaleTimeString()}]</span> {log}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-600 italic">No actions executed yet</div>
                )}
              </div>
            </div>
          </ScrollArea>
        </div>
      )}

      {isCollapsed && (
        <div className="h-full flex flex-col items-center justify-center gap-4 py-8">
          <Code className="w-5 h-5 text-gray-600 rotate-90" />
          <div className="text-xs text-gray-600 uppercase tracking-wider [writing-mode:vertical-rl] rotate-180">
            Debug
          </div>
        </div>
      )}
    </div>
  );
}

function Sparkles({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M12 3v18" />
      <path d="M9 6.5h6" />
      <path d="M7.5 9h9" />
      <path d="M9 17.5h6" />
      <path d="M7.5 15h9" />
    </svg>
  );
}
