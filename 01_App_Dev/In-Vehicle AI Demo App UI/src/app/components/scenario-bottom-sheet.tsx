import { AlertTriangle, Eye, Hand, X } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/app/components/ui/sheet";

interface Scenario {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
}

interface ScenarioBottomSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onScenarioSelect: (scenarioId: string) => void;
  activeScenario: string | null;
}

export function ScenarioBottomSheet({ 
  open, 
  onOpenChange, 
  onScenarioSelect,
  activeScenario 
}: ScenarioBottomSheetProps) {
  const scenarios: Scenario[] = [
    {
      id: "lane-drowsy",
      name: "Lane Departure + Drowsiness",
      icon: <AlertTriangle className="w-5 h-5" />,
      description: "Lane drift with drowsy driver"
    },
    {
      id: "drowsy-warning",
      name: "Drowsy Driver Warning",
      icon: <Eye className="w-5 h-5" />,
      description: "Critical drowsiness detected"
    },
    {
      id: "hands-off",
      name: "Hands Off Steering Wheel",
      icon: <Hand className="w-5 h-5" />,
      description: "No hands on steering wheel"
    },
    {
      id: "collision-risk",
      name: "Forward Collision Risk",
      icon: <AlertTriangle className="w-5 h-5" />,
      description: "High collision risk ahead"
    }
  ];

  const handleSelect = (scenarioId: string) => {
    onScenarioSelect(scenarioId);
    onOpenChange(false);
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="bg-gray-950 border-t border-gray-800 h-[60vh]">
        <SheetHeader className="mb-4">
          <SheetTitle className="text-gray-100 flex items-center gap-2">
            <div className="w-1 h-5 bg-cyan-500 rounded-full"></div>
            Test Scenarios
          </SheetTitle>
          <p className="text-xs text-gray-500">Select a scenario to simulate</p>
        </SheetHeader>

        <div className="space-y-3 pb-6">
          {scenarios.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => handleSelect(scenario.id)}
              className={`w-full text-left p-4 rounded-lg border transition-all ${
                activeScenario === scenario.id
                  ? "bg-cyan-950/30 border-cyan-500/50 shadow-lg shadow-cyan-500/20"
                  : "bg-gray-900/50 border-gray-800 hover:border-cyan-500/30 active:bg-gray-900"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded ${activeScenario === scenario.id ? "bg-cyan-500/20 text-cyan-400" : "bg-gray-800 text-gray-400"}`}>
                  {scenario.icon}
                </div>
                <div className="flex-1">
                  <div className={`font-medium mb-1 ${activeScenario === scenario.id ? "text-cyan-400" : "text-gray-200"}`}>
                    {scenario.name}
                  </div>
                  <div className="text-xs text-gray-500">{scenario.description}</div>
                </div>
                {activeScenario === scenario.id && (
                  <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse mt-1"></div>
                )}
              </div>
            </button>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
}