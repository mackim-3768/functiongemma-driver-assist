import { VehicleAction } from "@/app/types";
import { 
  Hand, 
  Navigation, 
  Volume2, 
  Gauge as GaugeIcon, 
  Eye, 
  MessageSquare, 
  TrendingUp, 
  Coffee, 
  FileText, 
  ShieldAlert 
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface ActionPanelProps {
  actions: VehicleAction[];
  visible: boolean;
}

export function ActionPanel({ actions, visible }: ActionPanelProps) {
  const getActionIcon = (action: VehicleAction) => {
    switch (action.type) {
      case "steering_vibration": return <Hand className="w-4 h-4" />;
      case "navigation_warning": return <Navigation className="w-4 h-4" />;
      case "drowsiness_alert_sound": return <Volume2 className="w-4 h-4" />;
      case "cluster_visual_warning": return <GaugeIcon className="w-4 h-4" />;
      case "hud_warning_overlay": return <Eye className="w-4 h-4" />;
      case "voice_prompt": return <MessageSquare className="w-4 h-4" />;
      case "warning_escalation": return <TrendingUp className="w-4 h-4" />;
      case "rest_recommendation": return <Coffee className="w-4 h-4" />;
      case "safety_event_logging": return <FileText className="w-4 h-4" />;
      case "request_safe_mode": return <ShieldAlert className="w-4 h-4" />;
      default: return <GaugeIcon className="w-4 h-4" />;
    }
  };

  const getActionLabel = (action: VehicleAction) => {
    switch (action.type) {
      case "steering_vibration": return `Wheel Vibration (${action.intensity})`;
      case "navigation_warning": return `Nav Warning (${action.level})`;
      case "drowsiness_alert_sound": return `Alert Sound (${action.volume_percent}%)`;
      case "cluster_visual_warning": return `Cluster Warning`;
      case "hud_warning_overlay": return `HUD Warning`;
      case "voice_prompt": return `Voice Prompt`;
      case "warning_escalation": return `Escalate to ${action.level}`;
      case "rest_recommendation": return `Rest Break`;
      case "safety_event_logging": return `Log Event`;
      case "request_safe_mode": return `Safe Mode`;
      default: return "Unknown Action";
    }
  };

  const getActionColor = (action: VehicleAction) => {
    if ("level" in action) {
      switch (action.level) {
        case "critical": return "border-red-500/50 bg-red-500/10 text-red-400";
        case "warning": return "border-amber-500/50 bg-amber-500/10 text-amber-400";
        default: return "border-cyan-500/50 bg-cyan-500/10 text-cyan-400";
      }
    }
    if (action.type === "steering_vibration") {
      switch (action.intensity) {
        case "high": return "border-red-500/50 bg-red-500/10 text-red-400";
        case "medium": return "border-amber-500/50 bg-amber-500/10 text-amber-400";
        default: return "border-cyan-500/50 bg-cyan-500/10 text-cyan-400";
      }
    }
    return "border-cyan-500/50 bg-cyan-500/10 text-cyan-400";
  };

  return (
    <AnimatePresence>
      {visible && actions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          className="absolute top-2 right-2 max-w-[200px] z-10"
        >
          <div className="backdrop-blur-md bg-black/80 border-2 border-cyan-500/50 rounded-lg p-2 shadow-xl shadow-cyan-500/20">
            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-cyan-500/30">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
              <div className="text-[10px] font-mono uppercase tracking-wider text-cyan-400">Actions Triggered</div>
            </div>
            <div className="space-y-1.5 max-h-[200px] overflow-y-auto">
              {actions.map((action, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`backdrop-blur-sm border rounded p-1.5 flex items-center gap-2 ${getActionColor(action)}`}
                >
                  {getActionIcon(action)}
                  <div className="flex-1 font-mono text-[8px] leading-tight">
                    {getActionLabel(action)}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
