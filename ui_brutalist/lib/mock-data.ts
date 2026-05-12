import { FightSignature, GamePlan } from "./types";

export const MOCK_SUBJECT: FightSignature = {
  fighter: "Jon Jones",
  analyzed_at: "2026-05-12T10:00:00Z",
  data_quality: {
    detection_rate_pct: 87.4,
    total_frames_analyzed: 54321,
    duration_seconds: 1810.7,
  },
  guard_signature: {
    dominant_stance: "orthodox",
    guard_height: "mid",
    chin_exposure_index: 0.12,
    lead_hand_activity: "active",
    rear_hand_position: "tight",
  },
  movement_patterns: {
    footwork_style: "angular / pivot-heavy",
    pressure_index: 0.68,
    lateral_movement_preference: "left",
    distance_management: "mid-range",
  },
  striking_tendencies: {
    jab_frequency: "high",
    power_hand_usage: 41,
    combination_length: "2-3",
    entry_patterns: ["jab → oblique kick", "feint → overhand right", "jab-jab → takedown"],
  },
  exploitable_vulnerabilities: [
    {
      vulnerability: "Drops lead hand after jab series",
      confidence: 0.82,
      tactical_counter: "Time right cross over dropped jab",
    },
    {
      vulnerability: "Wide stance reduces lateral mobility when pressured",
      confidence: 0.71,
      tactical_counter: "Circle to right side, cut off cage",
    },
    {
      vulnerability: "Telegraphs takedown entries via shoulder dip",
      confidence: 0.78,
      tactical_counter: "Sprawl drill + knee strike on level change",
    },
  ],
  camp_recommendations: [
    "400 oblique kick reps/day — primary range setter",
    "Jab-catch → counter right hand drill (200 reps)",
    "Cage-cut footwork: force right-side exposure",
    "Clinch entry defense: hand fight + underhook pummeling",
    "Cardio emphasis: sustain pressure rounds 3-5",
    "Film study: oblique kick timing windows",
  ],
  threat_assessment: {
    primary_weapon: "Oblique kick + front kick to body",
    danger_zone: "Mid-range (kick range) transitioning to clinch",
    overall_threat_level: 9,
  },
};

export const MOCK_OPPONENT: FightSignature = {
  fighter: "Stipe Miocic",
  analyzed_at: "2026-05-12T10:00:00Z",
  data_quality: {
    detection_rate_pct: 82.1,
    total_frames_analyzed: 48900,
    duration_seconds: 1630.0,
  },
  guard_signature: {
    dominant_stance: "orthodox",
    guard_height: "high",
    chin_exposure_index: 0.08,
    lead_hand_activity: "active",
    rear_hand_position: "tight",
  },
  movement_patterns: {
    footwork_style: "linear / pressure-forward",
    pressure_index: 0.74,
    lateral_movement_preference: "balanced",
    distance_management: "clinch-seeker",
  },
  striking_tendencies: {
    jab_frequency: "high",
    power_hand_usage: 58,
    combination_length: "2-3",
    entry_patterns: ["jab → body right", "double jab → overhand", "level change → clinch"],
  },
  exploitable_vulnerabilities: [
    {
      vulnerability: "Predictable jab-body-head pattern",
      confidence: 0.79,
      tactical_counter: "Parry jab → catch body → slip head",
    },
    {
      vulnerability: "Overcommits on overhand right, leaves chin",
      confidence: 0.74,
      tactical_counter: "Step outside, left hook counter",
    },
    {
      vulnerability: "Low kick defense deteriorates in rounds 4-5",
      confidence: 0.68,
      tactical_counter: "Body kick accumulation strategy",
    },
  ],
  camp_recommendations: [
    "Jab-to-body parry drill: intercept overhand entry",
    "Body kick volume: 300+ per session",
    "Clinch defense: create underhooks, disengage clean",
    "Counter-left hook on overhand: 200 reps on mitts",
    "Southpaw sparring rounds: adjust to angle",
    "Late-round conditioning: maintain precision rounds 4-5",
  ],
  threat_assessment: {
    primary_weapon: "Overhand right + clinch work",
    danger_zone: "Boxing range — inside jab distance",
    overall_threat_level: 8,
  },
};

export const MOCK_GAMEPLAN: GamePlan = {
  matchup: "Jon Jones vs Stipe Miocic",
  generated_at: "2026-05-12T10:01:00Z",
  advantage_analysis: {
    striking_edge: "Jon Jones",
    grappling_edge: "Jon Jones",
    footwork_edge: "Jon Jones",
    overall_edge: "Jon Jones",
  },
  exploitation_plan: [
    {
      opponent_weakness: "Predictable jab-body-head combination",
      our_tool: "Parry-slip-counter right hand",
      timing: "Third punch of combination",
      drill: "Parry-to-counter on mitts, 300 reps",
    },
    {
      opponent_weakness: "Overhand right overcommitment",
      our_tool: "Outside step + left hook",
      timing: "As right hand extends",
      drill: "Angle out + hook drill vs southpaw sparring partner",
    },
  ],
  danger_management: [
    {
      opponent_threat: "Overhand right KO power",
      defensive_response: "Head movement + lateral exit",
      positioning: "Stay outside boxing range or in clinch",
    },
    {
      opponent_threat: "Clinch control and dirty boxing",
      defensive_response: "Hand fight for underhook, disengage",
      positioning: "Maintain distance — oblique kick as range setter",
    },
  ],
  round_strategy: {
    rounds_1_2: "Establish oblique kick. Study timing. Avoid exchanges. Control range.",
    rounds_3_4: "Increase pressure. Body kicks accumulation. Look for takedown setups.",
    round_5: "If ahead: maintain distance, point fight. If behind: force grappling, top control.",
  },
  key_performance_indicators: [
    "Oblique kicks landed per round (target: 8+)",
    "Times opponent closes to boxing range (minimize to <5/round)",
    "Takedown attempts in rounds 3-5",
    "Head movement count on overhand attempts",
  ],
  camp_priority_drills: [
    {
      drill: "Oblique kick → jab-right hand",
      purpose: "Primary offensive sequence",
      volume: "500 reps/day",
    },
    {
      drill: "Parry overhand → outside angle hook",
      purpose: "Primary defensive counter",
      volume: "200 reps on mitts",
    },
    {
      drill: "Clinch disengage to long range",
      purpose: "Reset after opponent clinch entries",
      volume: "10 rounds sparring emphasis",
    },
  ],
};
