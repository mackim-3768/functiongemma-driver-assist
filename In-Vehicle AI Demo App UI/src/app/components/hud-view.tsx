import { Activity, Eye, Hand, Gauge, Shield, AlertTriangle, Cloud, Clock, Radio, Camera } from "lucide-react";
import { FullContext } from "@/app/types";

interface HUDViewProps {
  context: FullContext;
}

export function HUDView({ context }: HUDViewProps) {
  const getLaneColor = () => {
    if (context.lane_departure.departed) {
      return context.lane_departure.confidence > 0.7 ? "text-red-400 border-red-500/50 bg-red-500/10" : "text-amber-400 border-amber-500/50 bg-amber-500/10";
    }
    return "text-green-400 border-green-500/50 bg-green-500/10";
  };

  const getDrowsinessColor = () => {
    if (context.drowsiness.drowsy) {
      return context.drowsiness.confidence > 0.7 ? "text-red-400 border-red-500/50 bg-red-500/10" : "text-amber-400 border-amber-500/50 bg-amber-500/10";
    }
    return "text-green-400 border-green-500/50 bg-green-500/10";
  };

  const getCollisionColor = () => {
    switch (context.collision_risk.risk_level) {
      case "high": return "text-red-400 border-red-500/50 bg-red-500/10";
      case "medium": return "text-amber-400 border-amber-500/50 bg-amber-500/10";
      default: return "text-green-400 border-green-500/50 bg-green-500/10";
    }
  };

  const getFatigueColor = () => {
    switch (context.fatigue.fatigue_risk) {
      case "high": return "text-red-400";
      case "medium": return "text-amber-400";
      default: return "text-green-400";
    }
  };

  return (
    <div className="relative w-full h-full bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 rounded-lg overflow-hidden">
      {/* Road visualization */}
      <div className="absolute inset-0 flex items-end justify-center pb-12">
        <svg width="100%" height="100%" viewBox="0 0 400 300" className="opacity-20">
          <line x1="100" y1="300" x2="150" y2="100" stroke="#444" strokeWidth="2" />
          <line x1="200" y1="300" x2="200" y2="100" stroke="#888" strokeWidth="2" strokeDasharray="10,10" />
          <line x1="300" y1="300" x2="250" y2="100" stroke="#444" strokeWidth="2" />
        </svg>
      </div>

      {/* HUD Overlays - Context Indicators */}
      <div className="absolute inset-0 p-2">
        {/* Row 1: Critical Safety Indicators */}
        <div className="flex gap-1.5 mb-1.5">
          {/* Lane Departure */}
          <div className={`flex-1 backdrop-blur-md border-2 rounded p-1.5 flex items-center justify-center gap-1.5 ${getLaneColor()}`}>
            <Activity className="w-5 h-5" />
            <div className="flex flex-col items-center">
              <div className="font-mono text-[9px] font-bold tracking-wider">
                {context.lane_departure.departed ? "DEPT" : "OK"}
              </div>
              <div className="font-mono text-[8px] opacity-70">
                {Math.round(context.lane_departure.confidence * 100)}%
              </div>
            </div>
          </div>

          {/* Drowsiness */}
          <div className={`flex-1 backdrop-blur-md border-2 rounded p-1.5 flex items-center justify-center gap-1.5 ${getDrowsinessColor()}`}>
            <Eye className="w-5 h-5" />
            <div className="flex flex-col items-center">
              <div className="font-mono text-[9px] font-bold tracking-wider">
                {context.drowsiness.drowsy ? "DRWS" : "OK"}
              </div>
              <div className="font-mono text-[8px] opacity-70">
                {Math.round(context.drowsiness.confidence * 100)}%
              </div>
            </div>
          </div>

          {/* Collision Risk */}
          <div className={`flex-1 backdrop-blur-md border-2 rounded p-1.5 flex items-center justify-center gap-1.5 ${getCollisionColor()}`}>
            <Shield className="w-5 h-5" />
            <div className="flex flex-col items-center">
              <div className="font-mono text-[9px] font-bold tracking-wider uppercase">
                {context.collision_risk.risk_level === "low" ? "OK" : context.collision_risk.risk_level.substring(0, 3)}
              </div>
              <div className="font-mono text-[8px] opacity-70">
                {Math.round(context.collision_risk.risk_score * 100)}%
              </div>
            </div>
          </div>
        </div>

        {/* Row 2: Vehicle State */}
        <div className="flex gap-1.5 mb-1.5">
          {/* Steering Grip */}
          <div className={`backdrop-blur-md border-2 rounded p-1.5 flex items-center justify-center gap-1.5 ${
            context.steering_grip.hands_on 
              ? "text-green-400 border-green-500/50 bg-green-500/10" 
              : "text-red-400 border-red-500/50 bg-red-500/10"
          }`}>
            <Hand className="w-5 h-5" />
            <div className="font-mono text-[9px] font-bold tracking-wider">
              {context.steering_grip.hands_on ? "ON" : "OFF"}
            </div>
          </div>

          {/* Speed */}
          <div className="flex-1 backdrop-blur-md border-2 border-cyan-500/50 bg-cyan-500/10 rounded p-1.5 flex items-center justify-center gap-2 text-cyan-400">
            <Gauge className="w-5 h-5" />
            <div className="flex items-baseline gap-1">
              <div className="font-mono text-xl font-bold">{context.vehicle_speed.speed_kph}</div>
              <div className="text-[8px] font-medium opacity-70">KPH</div>
            </div>
          </div>

          {/* LKA Status */}
          <div className={`backdrop-blur-md border-2 rounded p-1.5 flex items-center justify-center gap-1.5 ${
            context.lane_keep_assist.enabled 
              ? "text-cyan-400 border-cyan-500/50 bg-cyan-500/10" 
              : "text-gray-500 border-gray-700/50 bg-gray-800/10"
          }`}>
            <Activity className="w-5 h-5" />
            <div className="font-mono text-[9px] font-bold tracking-wider">LKA</div>
          </div>
        </div>

        {/* Bottom Row: Environment & System Status */}
        <div className="absolute bottom-2 left-2 right-2 flex gap-1.5">
          {/* Environment */}
          <div className="backdrop-blur-md border border-gray-700/50 bg-gray-900/30 rounded p-1.5 flex items-center gap-1.5 text-gray-400">
            <Cloud className="w-4 h-4" />
            <div className="font-mono text-[8px] uppercase">{context.environment.weather}</div>
          </div>

          {/* Fatigue */}
          <div className={`backdrop-blur-md border border-gray-700/50 bg-gray-900/30 rounded p-1.5 flex items-center gap-1.5 ${getFatigueColor()}`}>
            <Clock className="w-4 h-4" />
            <div className="font-mono text-[8px]">{context.fatigue.driving_minutes}m</div>
          </div>

          {/* Sensor Health */}
          <div className={`backdrop-blur-md border border-gray-700/50 bg-gray-900/30 rounded p-1.5 flex items-center gap-1.5 ${
            context.sensor_health.camera_ok && context.sensor_health.ai_model_confidence > 0.8
              ? "text-green-400"
              : "text-amber-400"
          }`}>
            <Camera className="w-4 h-4" />
            <div className="font-mono text-[8px]">{Math.round(context.sensor_health.ai_model_confidence * 100)}%</div>
          </div>

          {/* Last Warning */}
          {context.warning_history.last_warning_type !== "none" && (
            <div className="backdrop-blur-md border border-amber-700/50 bg-amber-900/20 rounded p-1.5 flex items-center gap-1.5 text-amber-400">
              <AlertTriangle className="w-4 h-4" />
              <div className="font-mono text-[8px]">{context.warning_history.seconds_ago}s ago</div>
            </div>
          )}
        </div>

        {/* Center - Observer Indicator */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
          <div className="text-center opacity-10">
            <div className="w-16 h-16 mx-auto border-2 border-cyan-400/40 rounded-full flex items-center justify-center">
              <div className="w-10 h-10 border border-cyan-400/50 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
