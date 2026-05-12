export interface GuardSignature {
  dominant_stance: "orthodox" | "southpaw" | "switch";
  guard_height: "high" | "mid" | "low";
  chin_exposure_index: number;
  lead_hand_activity: "passive" | "active" | "hyperactive";
  rear_hand_position: "tight" | "extended" | "dropped";
}

export interface MovementPatterns {
  footwork_style: string;
  pressure_index: number;
  lateral_movement_preference: "left" | "right" | "balanced";
  distance_management: "clinch-seeker" | "mid-range" | "boxer";
}

export interface StrikingTendencies {
  jab_frequency: "low" | "medium" | "high";
  power_hand_usage: number;
  combination_length: "single" | "2-3" | "4+";
  entry_patterns: string[];
}

export interface Vulnerability {
  vulnerability: string;
  confidence: number;
  tactical_counter: string;
}

export interface ThreatAssessment {
  primary_weapon: string;
  danger_zone: string;
  overall_threat_level: number;
}

export interface FightSignature {
  fighter: string;
  analyzed_at: string;
  data_quality: {
    detection_rate_pct: number;
    total_frames_analyzed: number;
    duration_seconds: number;
  };
  guard_signature: GuardSignature;
  movement_patterns: MovementPatterns;
  striking_tendencies: StrikingTendencies;
  exploitable_vulnerabilities: Vulnerability[];
  camp_recommendations: string[];
  threat_assessment: ThreatAssessment;
  _meta?: {
    model: string;
    input_tokens: number;
    output_tokens: number;
    generated_at: string;
  };
}

export interface ExploitationPlan {
  opponent_weakness: string;
  our_tool: string;
  timing: string;
  drill: string;
}

export interface DangerManagement {
  opponent_threat: string;
  defensive_response: string;
  positioning: string;
}

export interface CampDrill {
  drill: string;
  purpose: string;
  volume: string;
}

export interface GamePlan {
  matchup: string;
  generated_at: string;
  advantage_analysis: {
    striking_edge: string;
    grappling_edge: string;
    footwork_edge: string;
    overall_edge: string;
  };
  exploitation_plan: ExploitationPlan[];
  danger_management: DangerManagement[];
  round_strategy: {
    rounds_1_2: string;
    rounds_3_4: string;
    round_5: string;
  };
  key_performance_indicators: string[];
  camp_priority_drills: CampDrill[];
}
