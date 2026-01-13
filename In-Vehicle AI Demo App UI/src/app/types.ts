// Context Data Types
export interface LaneDepartureContext {
  departed: boolean;
  confidence: number;
}

export interface DrowsinessContext {
  drowsy: boolean;
  confidence: number;
}

export interface SteeringGripContext {
  hands_on: boolean;
}

export interface VehicleSpeedContext {
  speed_kph: number;
}

export interface LaneKeepAssistContext {
  enabled: boolean;
}

export interface CollisionRiskContext {
  risk_level: "low" | "medium" | "high";
  risk_score: number;
}

export interface EnvironmentContext {
  weather: "clear" | "rain" | "snow" | "fog" | "windy" | "unknown";
  road_condition: "dry" | "wet" | "icy" | "snowy" | "unknown";
  visibility: "good" | "moderate" | "poor" | "unknown";
}

export interface FatigueContext {
  driving_minutes: number;
  fatigue_risk: "low" | "medium" | "high";
}

export interface WarningHistoryContext {
  last_warning_type: "lane_departure" | "drowsiness" | "forward_collision" | "steering_grip" | "none";
  seconds_ago: number;
}

export interface SensorHealthContext {
  camera_ok: boolean;
  ai_model_confidence: number;
}

export interface FullContext {
  lane_departure: LaneDepartureContext;
  drowsiness: DrowsinessContext;
  steering_grip: SteeringGripContext;
  vehicle_speed: VehicleSpeedContext;
  lane_keep_assist: LaneKeepAssistContext;
  collision_risk: CollisionRiskContext;
  environment: EnvironmentContext;
  fatigue: FatigueContext;
  warning_history: WarningHistoryContext;
  sensor_health: SensorHealthContext;
  timestamp: string;
}

// Action Tool Types
export interface SteeringVibrationAction {
  type: "steering_vibration";
  intensity: "low" | "medium" | "high";
}

export interface NavigationWarningAction {
  type: "navigation_warning";
  message: string;
  level: "info" | "warning" | "critical";
}

export interface DrowsinessAlertAction {
  type: "drowsiness_alert_sound";
  volume_percent: number;
}

export interface ClusterWarningAction {
  type: "cluster_visual_warning";
  message: string;
  level: "normal" | "warning" | "critical";
}

export interface HUDWarningAction {
  type: "hud_warning_overlay";
  message: string;
  level: "normal" | "warning" | "critical";
}

export interface VoicePromptAction {
  type: "voice_prompt";
  message: string;
  level: "normal" | "warning" | "critical";
}

export interface EscalationAction {
  type: "warning_escalation";
  level: "normal" | "warning" | "critical";
}

export interface RestRecommendationAction {
  type: "rest_recommendation";
  reason: string;
}

export interface SafetyLoggingAction {
  type: "safety_event_logging";
  message: string;
}

export interface SafeModeAction {
  type: "request_safe_mode";
  reason: string;
}

export type VehicleAction = 
  | SteeringVibrationAction
  | NavigationWarningAction
  | DrowsinessAlertAction
  | ClusterWarningAction
  | HUDWarningAction
  | VoicePromptAction
  | EscalationAction
  | RestRecommendationAction
  | SafetyLoggingAction
  | SafeModeAction;

export interface AIOutput {
  function_name: string;
  selected_actions: VehicleAction[];
  confidence: number;
  reasoning: string;
  context_factors: string[];
}
