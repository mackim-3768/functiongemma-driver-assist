import { Code, Database, Terminal, X, Lock } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/app/components/ui/dialog";
import { ScrollArea } from "@/app/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/app/components/ui/tabs";
import { FullContext, AIOutput } from "@/app/types";

interface EngineerModeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  contextData: FullContext;
  aiOutput: AIOutput | null;
  actionLog: string[];
}

export function EngineerModeDialog({ 
  open, 
  onOpenChange,
  contextData,
  aiOutput,
  actionLog 
}: EngineerModeDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] h-[90vh] bg-black border-2 border-cyan-500/30 text-gray-100 p-0 shadow-2xl shadow-cyan-500/20">
        {/* Header with Developer Warning */}
        <DialogHeader className="px-6 py-4 border-b-2 border-cyan-900/50 bg-gradient-to-r from-gray-950 via-cyan-950/20 to-gray-950">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-cyan-500/20 border border-cyan-500/50 rounded">
                <Code className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <DialogTitle className="text-gray-100 flex items-center gap-2 mb-1">
                  Engineer Mode
                  <span className="px-2 py-0.5 bg-amber-500/20 border border-amber-500/50 text-amber-400 text-[10px] uppercase tracking-wider rounded">
                    Debug
                  </span>
                </DialogTitle>
                <p className="text-xs text-gray-500 flex items-center gap-2">
                  <Lock className="w-3 h-3" />
                  Developer Console • Not for End Users
                </p>
              </div>
            </div>
          </div>
        </DialogHeader>

        <Tabs defaultValue="context" className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="mx-6 mt-4 bg-gray-950 border border-cyan-900/30">
            <TabsTrigger 
              value="context" 
              className="text-xs font-mono data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400 data-[state=active]:border-cyan-500/50"
            >
              <Database className="w-3 h-3 mr-1.5" />
              Context
            </TabsTrigger>
            <TabsTrigger 
              value="ai" 
              className="text-xs font-mono data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400 data-[state=active]:border-cyan-500/50"
            >
              <Sparkles className="w-3 h-3 mr-1.5" />
              AI Output
            </TabsTrigger>
            <TabsTrigger 
              value="logs" 
              className="text-xs font-mono data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400 data-[state=active]:border-cyan-500/50"
            >
              <Terminal className="w-3 h-3 mr-1.5" />
              Logs
            </TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-hidden px-6 pb-6">
            <TabsContent value="context" className="h-full mt-4">
              <ScrollArea className="h-full pr-4">
                <div className="mb-3 flex items-center gap-2 pb-2 border-b border-cyan-900/30">
                  <Database className="w-4 h-4 text-blue-400" />
                  <h3 className="text-xs uppercase tracking-wider text-gray-400 font-mono">Context Snapshot</h3>
                  <div className="ml-auto px-2 py-0.5 bg-blue-500/10 border border-blue-500/30 text-blue-400 text-[10px] uppercase tracking-wider rounded font-mono">
                    Observed
                  </div>
                </div>
                <div className="bg-gray-950 border-2 border-gray-800 rounded p-4 font-mono text-xs shadow-inner">
                  <pre className="text-green-400 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                    {JSON.stringify(contextData, null, 2)}
                  </pre>
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="ai" className="h-full mt-4">
              <ScrollArea className="h-full pr-4">
                <div className="mb-3 flex items-center gap-2 pb-2 border-b border-cyan-900/30">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-xs uppercase tracking-wider text-gray-400 font-mono">FunctionGemma Output</h3>
                  <div className="ml-auto px-2 py-0.5 bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-[10px] uppercase tracking-wider rounded font-mono">
                    AI Decision
                  </div>
                </div>
                <div className="bg-gray-950 border-2 border-cyan-900/30 rounded p-4 font-mono text-xs shadow-inner shadow-cyan-500/5">
                  {aiOutput ? (
                    <>
                      <div className="mb-4 pb-3 border-b border-cyan-900/30">
                        <div className="text-gray-500 text-[10px] mb-1">SELECTED FUNCTION:</div>
                        <div className="text-cyan-300 font-bold">{aiOutput.function_name}</div>
                        <div className="text-gray-500 text-[10px] mt-2">CONFIDENCE: {Math.round(aiOutput.confidence * 100)}%</div>
                      </div>
                      <div className="mb-4">
                        <div className="text-gray-500 text-[10px] mb-2">ACTION TOOLS:</div>
                        <pre className="text-cyan-300 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                          {JSON.stringify(aiOutput.selected_actions, null, 2)}
                        </pre>
                      </div>
                      <div className="mb-4">
                        <div className="text-gray-500 text-[10px] mb-2">REASONING:</div>
                        <div className="text-gray-400 text-xs leading-relaxed">{aiOutput.reasoning}</div>
                      </div>
                      <div>
                        <div className="text-gray-500 text-[10px] mb-2">CONTEXT FACTORS:</div>
                        <ul className="space-y-1">
                          {aiOutput.context_factors.map((factor, i) => (
                            <li key={i} className="text-gray-400 text-xs flex items-start gap-2">
                              <span className="text-cyan-500">•</span>
                              {factor}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </>
                  ) : (
                    <div className="text-gray-600 italic p-4 text-center border border-dashed border-gray-800 rounded">
                      Waiting for AI decision...
                      <div className="mt-2 text-[10px] text-gray-700">
                        Select a scenario or send a prompt to trigger AI output
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="logs" className="h-full mt-4">
              <ScrollArea className="h-full pr-4">
                <div className="mb-3 flex items-center gap-2 pb-2 border-b border-cyan-900/30">
                  <Terminal className="w-4 h-4 text-green-400" />
                  <h3 className="text-xs uppercase tracking-wider text-gray-400 font-mono">Action Execution Log</h3>
                  <div className="ml-auto px-2 py-0.5 bg-green-500/10 border border-green-500/30 text-green-400 text-[10px] uppercase tracking-wider rounded font-mono">
                    {actionLog.length} Events
                  </div>
                </div>
                <div className="bg-gray-950 border-2 border-gray-800 rounded p-4 font-mono text-xs shadow-inner">
                  {actionLog.length > 0 ? (
                    <div className="space-y-1">
                      {actionLog.map((log, index) => (
                        <div key={index} className="flex items-start gap-2 py-1 border-b border-gray-900/50 last:border-0">
                          <span className="text-gray-700 text-[10px] mt-0.5 min-w-[60px]">[{String(index + 1).padStart(3, '0')}]</span>
                          <span className="text-green-400 flex-1">{log}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-gray-600 italic p-4 text-center border border-dashed border-gray-800 rounded">
                      No actions executed yet
                      <div className="mt-2 text-[10px] text-gray-700">
                        Action logs will appear here as scenarios are triggered
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </div>
        </Tabs>

        {/* Footer with Warning */}
        <div className="px-6 py-3 border-t-2 border-amber-900/30 bg-gradient-to-r from-amber-950/20 via-transparent to-amber-950/20">
          <div className="flex items-center gap-2 text-amber-400/80 text-[10px] uppercase tracking-wider">
            <Lock className="w-3 h-3" />
            <span>Developer/Engineer Access Only • Not for Production Use</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
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