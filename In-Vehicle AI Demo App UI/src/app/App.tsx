import { useState } from "react";
import { Settings, Info, Cpu } from "lucide-react";
import { HUDView } from "@/app/components/hud-view";
import { ActionPanel } from "@/app/components/action-panel";
import { ScenarioBottomSheet } from "@/app/components/scenario-bottom-sheet";
import { EngineerModeDialog } from "@/app/components/engineer-mode-dialog";
import { PromptDialog } from "@/app/components/prompt-dialog";
import { BottomActionBar } from "@/app/components/bottom-action-bar";
import { Button } from "@/app/components/ui/button";
import { FullContext, AIOutput, VehicleAction } from "@/app/types";

export default function App() {
  // Context State (observed sensor/AI data)
  const [context, setContext] = useState<FullContext>({
    lane_departure: { departed: false, confidence: 0.95 },
    drowsiness: { drowsy: false, confidence: 0.98 },
    steering_grip: { hands_on: true },
    vehicle_speed: { speed_kph: 105 },
    lane_keep_assist: { enabled: true },
    collision_risk: { risk_level: "low", risk_score: 0.15 },
    environment: { weather: "clear", road_condition: "dry", visibility: "good" },
    fatigue: { driving_minutes: 45, fatigue_risk: "low" },
    warning_history: { last_warning_type: "none", seconds_ago: 0 },
    sensor_health: { camera_ok: true, ai_model_confidence: 0.96 },
    timestamp: new Date().toISOString()
  });

  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [actionLog, setActionLog] = useState<string[]>([]);
  const [aiOutput, setAiOutput] = useState<AIOutput | null>(null);
  const [triggeredActions, setTriggeredActions] = useState<VehicleAction[]>([]);

  // UI State
  const [scenariosOpen, setScenariosOpen] = useState(false);
  const [promptOpen, setPromptOpen] = useState(false);
  const [engineerModeOpen, setEngineerModeOpen] = useState(false);

  const addActionLog = (log: string) => {
    setActionLog(prev => [...prev, log].slice(-50));
  };

  const triggerActions = (actions: VehicleAction[]) => {
    setTriggeredActions(actions);
    actions.forEach(action => {
      addActionLog(`Executed: ${action.type}`);
    });
    // Clear after 5 seconds
    setTimeout(() => setTriggeredActions([]), 5000);
  };

  const handleScenarioSelect = (scenarioId: string) => {
    setActiveScenario(scenarioId);
    
    switch (scenarioId) {
      case "lane-drowsy":
        // Context: Lane departure + drowsiness detected
        setContext({
          ...context,
          lane_departure: { departed: true, confidence: 0.87 },
          drowsiness: { drowsy: true, confidence: 0.82 },
          steering_grip: { hands_on: true },
          vehicle_speed: { speed_kph: 110 },
          fatigue: { driving_minutes: 120, fatigue_risk: "medium" },
          warning_history: { last_warning_type: "lane_departure", seconds_ago: 45 },
          timestamp: new Date().toISOString()
        });

        // AI selects action tools
        const laneDrowsyActions: VehicleAction[] = [
          { type: "steering_vibration", intensity: "medium" },
          { type: "drowsiness_alert_sound", volume_percent: 70 },
          { type: "cluster_visual_warning", message: "Lane departure detected", level: "warning" },
          { type: "rest_recommendation", reason: "Driver showing drowsiness with lane departure" }
        ];

        setAiOutput({
          function_name: "handle_lane_departure_with_drowsiness",
          selected_actions: laneDrowsyActions,
          confidence: 0.89,
          reasoning: "Driver showing drowsiness (82% confidence) combined with lane departure (87% confidence). Multi-modal alerts recommended: steering vibration, audible warning, and rest recommendation.",
          context_factors: [
            "Lane departure detected with high confidence",
            "Driver drowsiness confirmed by AI vision model",
            "Driving duration: 120 minutes indicates potential fatigue",
            "Last warning was 45 seconds ago - escalation needed"
          ]
        });

        triggerActions(laneDrowsyActions);
        addActionLog("Scenario: Lane Departure + Drowsiness");
        break;
        
      case "drowsy-warning":
        // Context: Critical drowsiness only
        setContext({
          ...context,
          lane_departure: { departed: false, confidence: 0.96 },
          drowsiness: { drowsy: true, confidence: 0.94 },
          steering_grip: { hands_on: true },
          vehicle_speed: { speed_kph: 105 },
          fatigue: { driving_minutes: 180, fatigue_risk: "high" },
          warning_history: { last_warning_type: "drowsiness", seconds_ago: 120 },
          timestamp: new Date().toISOString()
        });

        const drowsyActions: VehicleAction[] = [
          { type: "drowsiness_alert_sound", volume_percent: 85 },
          { type: "voice_prompt", message: "Driver drowsiness detected. Please take a break.", level: "critical" },
          { type: "hud_warning_overlay", message: "DROWSINESS ALERT", level: "critical" },
          { type: "rest_recommendation", reason: "Critical drowsiness level detected" },
          { type: "safety_event_logging", message: "Critical drowsiness event at 18:34" }
        ];

        setAiOutput({
          function_name: "handle_critical_drowsiness",
          selected_actions: drowsyActions,
          confidence: 0.94,
          reasoning: "Critical drowsiness detected with 94% confidence. Driver has been driving for 180 minutes with high fatigue risk. Multi-modal escalation required with rest stop recommendation.",
          context_factors: [
            "Drowsiness confidence: 94% (critical threshold)",
            "Driving duration: 180 minutes without break",
            "High fatigue risk level",
            "Previous drowsiness warning 2 minutes ago",
            "Lane position currently stable"
          ]
        });

        triggerActions(drowsyActions);
        addActionLog("Scenario: Critical Drowsiness Warning");
        break;
        
      case "hands-off":
        // Context: Hands off steering wheel
        setContext({
          ...context,
          lane_departure: { departed: false, confidence: 0.95 },
          drowsiness: { drowsy: false, confidence: 0.92 },
          steering_grip: { hands_on: false },
          vehicle_speed: { speed_kph: 115 },
          lane_keep_assist: { enabled: true },
          warning_history: { last_warning_type: "steering_grip", seconds_ago: 8 },
          timestamp: new Date().toISOString()
        });

        const handsOffActions: VehicleAction[] = [
          { type: "steering_vibration", intensity: "low" },
          { type: "cluster_visual_warning", message: "Place hands on steering wheel", level: "warning" },
          { type: "warning_escalation", level: "warning" }
        ];

        setAiOutput({
          function_name: "handle_hands_off_steering",
          selected_actions: handsOffActions,
          confidence: 0.91,
          reasoning: "No hands detected on steering wheel while LKA is active. Driver appears alert but needs reminder to maintain manual control readiness. Escalating warning level.",
          context_factors: [
            "Steering wheel grip sensor: no contact detected",
            "Lane Keep Assist is active",
            "Driver appears alert (no drowsiness)",
            "Previous hands-off warning 8 seconds ago",
            "Speed: 115 kph requires attention"
          ]
        });

        triggerActions(handsOffActions);
        addActionLog("Scenario: Hands Off Steering Wheel");
        break;

      case "collision-risk":
        // Context: Forward collision risk
        setContext({
          ...context,
          lane_departure: { departed: false, confidence: 0.97 },
          drowsiness: { drowsy: false, confidence: 0.96 },
          steering_grip: { hands_on: true },
          vehicle_speed: { speed_kph: 100 },
          collision_risk: { risk_level: "high", risk_score: 0.85 },
          warning_history: { last_warning_type: "forward_collision", seconds_ago: 2 },
          timestamp: new Date().toISOString()
        });

        const collisionActions: VehicleAction[] = [
          { type: "steering_vibration", intensity: "high" },
          { type: "navigation_warning", message: "COLLISION RISK", level: "critical" },
          { type: "hud_warning_overlay", message: "BRAKE NOW", level: "critical" },
          { type: "voice_prompt", message: "Collision risk ahead. Brake immediately.", level: "critical" },
          { type: "safety_event_logging", message: "High collision risk event" }
        ];

        setAiOutput({
          function_name: "handle_collision_risk",
          selected_actions: collisionActions,
          confidence: 0.93,
          reasoning: "High collision risk detected (85% score). Immediate driver attention required. All available warning modalities activated for maximum alert.",
          context_factors: [
            "Collision risk score: 85% (high)",
            "Vehicle speed: 100 kph",
            "Driver alert and hands on wheel",
            "Rapid escalation needed within 2 seconds"
          ]
        });

        triggerActions(collisionActions);
        addActionLog("Scenario: Forward Collision Risk");
        break;
        
      default:
        break;
    }
  };

  const handlePromptSend = (message: string) => {
    addActionLog(`User prompt: "${message}"`);
    
    // Simple NLP simulation
    const lowerMsg = message.toLowerCase();
    if (lowerMsg.includes("drowsy") || lowerMsg.includes("tired") || lowerMsg.includes("sleep")) {
      handleScenarioSelect("drowsy-warning");
    } else if (lowerMsg.includes("lane") || lowerMsg.includes("drift")) {
      handleScenarioSelect("lane-drowsy");
    } else if (lowerMsg.includes("hand") || lowerMsg.includes("grip") || lowerMsg.includes("wheel")) {
      handleScenarioSelect("hands-off");
    } else if (lowerMsg.includes("collision") || lowerMsg.includes("crash") || lowerMsg.includes("brake")) {
      handleScenarioSelect("collision-risk");
    } else {
      addActionLog(`AI processing: "${message}"`);
    }
  };

  return (
    <div className="h-screen w-screen bg-black text-gray-100 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="bg-gray-950 border-b border-gray-800 px-4 py-2.5 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-gradient-to-br from-cyan-500 to-blue-600 rounded flex items-center justify-center">
            <Cpu className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold">FunctionGemma Demo</h1>
            <p className="text-[10px] text-gray-500">AI Action Selection • Observer View</p>
          </div>
        </div>
        
        <Button
          onClick={() => setEngineerModeOpen(true)}
          variant="ghost"
          size="sm"
          className="h-8 px-3 text-gray-400 hover:text-cyan-400 hover:bg-gray-900 border border-transparent hover:border-cyan-500/30 gap-1.5"
        >
          <Settings className="w-4 h-4" />
          <span className="text-[10px] uppercase tracking-wider font-mono hidden sm:inline">Engineer</span>
        </Button>
      </header>

      {/* Main Content - Context Visualization */}
      <div className="flex-1 p-3 overflow-hidden relative">
        <HUDView context={context} />
        <ActionPanel actions={triggeredActions} visible={triggeredActions.length > 0} />
      </div>

      {/* Flow Indicator */}
      <div className="bg-gray-950/50 border-t border-gray-800/50 px-4 py-1.5 flex items-center justify-center gap-3">
        <div className="text-[9px] font-mono text-blue-400 uppercase flex items-center gap-1">
          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
          Context Observed
        </div>
        <div className="text-gray-600">→</div>
        <div className="text-[9px] font-mono text-cyan-400 uppercase flex items-center gap-1">
          <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div>
          AI Selects Actions
        </div>
        <div className="text-gray-600">→</div>
        <div className="text-[9px] font-mono text-green-400 uppercase flex items-center gap-1">
          <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
          Vehicle Executes
        </div>
      </div>

      {/* Disclaimer Bar */}
      <div className="bg-amber-950/30 border-t border-amber-900/50 px-4 py-2 flex items-center gap-2">
        <Info className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <p className="text-[10px] text-amber-200/80">
          Demo: AI observes context and selects actions. Does NOT drive or control vehicle autonomously.
        </p>
      </div>

      {/* Bottom Action Bar */}
      <BottomActionBar
        onScenariosClick={() => setScenariosOpen(true)}
        onPromptClick={() => setPromptOpen(true)}
      />

      {/* Modals */}
      <ScenarioBottomSheet
        open={scenariosOpen}
        onOpenChange={setScenariosOpen}
        onScenarioSelect={handleScenarioSelect}
        activeScenario={activeScenario}
      />

      <PromptDialog
        open={promptOpen}
        onOpenChange={setPromptOpen}
        onSend={handlePromptSend}
      />

      <EngineerModeDialog
        open={engineerModeOpen}
        onOpenChange={setEngineerModeOpen}
        contextData={context}
        aiOutput={aiOutput}
        actionLog={actionLog}
      />
    </div>
  );
}
