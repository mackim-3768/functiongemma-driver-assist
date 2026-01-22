import { AlertTriangle, Eye, Hand } from "lucide-react";
import { Button } from "@/app/components/ui/button";

interface Scenario {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
}

interface ScenarioPanelProps {
  onScenarioSelect: (scenarioId: string) => void;
  activeScenario: string | null;
}

export function ScenarioPanel({ onScenarioSelect, activeScenario }: ScenarioPanelProps) {
  const scenarios: Scenario[] = [
    {
      id: "lane-drowsy",
      name: "Lane Departure + Drowsiness",
      icon: <AlertTriangle className="w-5 h-5" />,
      description: "Simulates lane drift with drowsy driver"
    },
    {
      id: "drowsy-warning",
      name: "Drowsy Driver Warning",
      icon: <Eye className="w-5 h-5" />,
      description: "Driver showing signs of drowsiness"
    },
    {
      id: "hands-off",
      name: "Hands Off Steering Wheel",
      icon: <Hand className="w-5 h-5" />,
      description: "No hands detected on steering wheel"
    }
  ];

  return (
    <div className="h-full bg-gray-950 border-r border-gray-800 p-4">
      <div className="mb-6">
        <h2 className="text-sm uppercase tracking-wider text-gray-400 mb-1">Test Scenarios</h2>
        <div className="h-px bg-gradient-to-r from-cyan-500/50 to-transparent"></div>
      </div>

      <div className="space-y-3">
        {scenarios.map((scenario) => (
          <button
            key={scenario.id}
            onClick={() => onScenarioSelect(scenario.id)}
            className={`w-full text-left p-4 rounded-lg border transition-all ${
              activeScenario === scenario.id
                ? "bg-cyan-950/30 border-cyan-500/50 shadow-lg shadow-cyan-500/20"
                : "bg-gray-900/50 border-gray-800 hover:border-cyan-500/30 hover:bg-gray-900"
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
                <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></div>
              )}
            </div>
          </button>
        ))}
      </div>

      <div className="mt-6 p-3 bg-gray-900/50 border border-gray-800 rounded-lg">
        <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Status</div>
        <div className="text-sm text-gray-300">
          {activeScenario ? "Scenario Active" : "Select a scenario to begin"}
        </div>
      </div>
    </div>
  );
}
