"""
brain/pattern_recognition.py
Analyze movement vectors, detect patterns, and generate Fight Signature reports via Claude.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data_raw"
DATA_PROCESSED = ROOT / "data_processed"
MANIFEST_PATH = DATA_RAW / "manifest.json"
REPORTS_DIR = ROOT / "data_processed" / "reports"

SYSTEM_PROMPT = """You are an elite MMA combat analyst with expertise in biomechanics, fight strategy, and pattern recognition. Your role is to analyze telemetry data extracted from fight footage and produce tactical intelligence reports.

You receive structured JSON data containing:
- Movement statistics (joint angles, velocity vectors, stance measurements)
- Guard pattern frequencies
- Detected behavioral tendencies

Your output must be a structured JSON report following the Fight Signature format. Be precise, tactical, and use MMA-specific terminology. All analysis must be grounded in the data provided."""

FIGHT_SIGNATURE_SCHEMA = {
    "fighter": "string",
    "analyzed_at": "ISO 8601 timestamp",
    "data_quality": {
        "detection_rate_pct": "float",
        "total_frames_analyzed": "int",
        "duration_seconds": "float"
    },
    "guard_signature": {
        "dominant_stance": "orthodox | southpaw | switch",
        "guard_height": "high | mid | low",
        "chin_exposure_index": "0.0-1.0 (1.0=fully exposed)",
        "lead_hand_activity": "passive | active | hyperactive",
        "rear_hand_position": "tight | extended | dropped"
    },
    "movement_patterns": {
        "footwork_style": "string",
        "pressure_index": "0.0-1.0",
        "lateral_movement_preference": "left | right | balanced",
        "distance_management": "clinch-seeker | mid-range | boxer"
    },
    "striking_tendencies": {
        "jab_frequency": "low | medium | high",
        "power_hand_usage": "percentage 0-100",
        "combination_length": "single | 2-3 | 4+",
        "entry_patterns": ["list of observed entry sequences"]
    },
    "exploitable_vulnerabilities": [
        {
            "vulnerability": "string",
            "confidence": "0.0-1.0",
            "tactical_counter": "string"
        }
    ],
    "camp_recommendations": ["list of specific training directives"],
    "threat_assessment": {
        "primary_weapon": "string",
        "danger_zone": "string",
        "overall_threat_level": "1-10"
    }
}


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print("[ERROR] manifest.json not found. Run ingestion/downloader.py first.")
        sys.exit(1)
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def _get_fighter_entries(manifest: dict, fighter: str) -> list[dict]:
    slug = fighter.lower().replace(" ", "_")
    return [
        e for e in manifest.get("entries", [])
        if e.get("fighter_slug") == slug and e.get("processed") and e.get("parquet_path")
    ]


def _compute_movement_stats(parquet_path: str) -> dict:
    """Compute aggregate movement statistics from parquet data."""
    try:
        import pandas as pd
    except ImportError:
        print("[ERROR] pandas not installed. Run: pip install pandas pyarrow")
        sys.exit(1)

    df = pd.read_parquet(parquet_path)
    detected = df[df["pose_detected"] == True].copy()

    if detected.empty:
        return {"error": "No pose detections found"}

    stats = {
        "total_frames": len(df),
        "detected_frames": len(detected),
        "detection_rate_pct": round(len(detected) / len(df) * 100, 2),
        "duration_seconds": round(df["timestamp_sec"].max(), 2),
    }

    # Guard angles
    for col in ["left_elbow_angle", "right_elbow_angle", "shoulder_tilt_deg", "hip_width"]:
        if col in detected.columns:
            series = detected[col].dropna()
            if not series.empty:
                stats[f"{col}_mean"] = round(float(series.mean()), 2)
                stats[f"{col}_std"] = round(float(series.std()), 2)
                stats[f"{col}_min"] = round(float(series.min()), 2)
                stats[f"{col}_max"] = round(float(series.max()), 2)

    # Hand height (wrist y-coordinate relative to shoulder)
    if "left_wrist_y" in detected.columns and "left_shoulder_y" in detected.columns:
        left_hand_height = (detected["left_shoulder_y"] - detected["left_wrist_y"]).dropna()
        stats["left_guard_height_mean"] = round(float(left_hand_height.mean()), 4)

    if "right_wrist_y" in detected.columns and "right_shoulder_y" in detected.columns:
        right_hand_height = (detected["right_shoulder_y"] - detected["right_wrist_y"]).dropna()
        stats["right_guard_height_mean"] = round(float(right_hand_height.mean()), 4)

    # Chin exposure (nose y relative to shoulders)
    if all(c in detected.columns for c in ["nose_y", "left_shoulder_y", "right_shoulder_y"]):
        shoulder_avg = (detected["left_shoulder_y"] + detected["right_shoulder_y"]) / 2
        chin_exp = (shoulder_avg - detected["nose_y"]).dropna()
        stats["chin_exposure_index"] = round(float(chin_exp.mean()), 4)

    # Lateral movement (hip x velocity)
    if "left_hip_x" in detected.columns:
        hip_x = detected["left_hip_x"].dropna()
        if len(hip_x) > 1:
            velocity = hip_x.diff().dropna()
            stats["lateral_velocity_mean"] = round(float(velocity.abs().mean()), 6)
            stats["lateral_bias"] = round(float(velocity.mean()), 6)

    # Stance width
    if "left_ankle_x" in detected.columns and "right_ankle_x" in detected.columns:
        stance = (detected["left_ankle_x"] - detected["right_ankle_x"]).abs().dropna()
        stats["stance_width_mean"] = round(float(stance.mean()), 4)

    return stats


def _build_analysis_prompt(fighter: str, stats: dict, role: str) -> str:
    schema_str = json.dumps(FIGHT_SIGNATURE_SCHEMA, indent=2)
    stats_str = json.dumps(stats, indent=2)

    return f"""Analyze the following telemetry data for fighter: **{fighter}** (role: {role})

## Movement Telemetry Statistics
```json
{stats_str}
```

## Instructions
Based on this telemetry data, generate a complete Fight Signature report.

Key interpretation guidelines:
- `left_elbow_angle_mean`: Lower angles (<90°) = tight guard; Higher (>120°) = extended/dropped guard
- `left_guard_height_mean` / `right_guard_height_mean`: Positive = hand above shoulder (high guard); Negative = hand below (dropped guard)
- `chin_exposure_index`: Higher positive = chin tucked; Lower/negative = chin up (exposed)
- `lateral_velocity_mean`: Higher = more active footwork; `lateral_bias` positive = moving right, negative = left
- `shoulder_tilt_deg_mean`: Near 0° = square stance; significant tilt = bladed stance
- `stance_width_mean`: Wider = more grounded/less mobile; Narrower = more mobile/less stable

Output ONLY valid JSON matching this exact schema:
```json
{schema_str}
```

Fill all fields with data-driven analysis. For `exploitable_vulnerabilities`, identify at minimum 2 and maximum 5 specific weaknesses. For `camp_recommendations`, provide 4-6 actionable training directives."""


def generate_fight_signature(fighter: str, stats: dict, role: str = "opponent") -> dict:
    """Call Claude API to generate the Fight Signature report."""
    try:
        import anthropic
    except ImportError:
        print("[ERROR] anthropic not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Check .env file
        env_path = ROOT / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        break

    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set. Create a .env file or export the variable.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"  [CLAUDE] Generating Fight Signature for {fighter}...")

    prompt = _build_analysis_prompt(fighter, stats, role)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # Extract JSON from markdown code block if present
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        report = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON parse error: {e}")
        report = {"raw_response": raw, "parse_error": str(e)}

    report["_meta"] = {
        "model": "claude-sonnet-4-6",
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    return report


def compare_fighters(subject_report: dict, opponent_report: dict) -> dict:
    """Cross-analyze subject vs opponent to generate tactical game plan."""
    try:
        import anthropic
    except ImportError:
        sys.exit(1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        env_path = ROOT / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        break

    client = anthropic.Anthropic(api_key=api_key)

    subject = subject_report.get("fighter", "Subject")
    opponent = opponent_report.get("fighter", "Opponent")

    print(f"  [CLAUDE] Generating tactical game plan: {subject} vs {opponent}...")

    prompt = f"""You are analyzing a matchup between two fighters using their Fight Signature telemetry reports.

## {subject} (OUR FIGHTER) — Fight Signature
```json
{json.dumps(subject_report, indent=2)}
```

## {opponent} (OPPONENT) — Fight Signature
```json
{json.dumps(opponent_report, indent=2)}
```

Generate a tactical game plan JSON with this structure:
{{
  "matchup": "{subject} vs {opponent}",
  "generated_at": "ISO timestamp",
  "advantage_analysis": {{
    "striking_edge": "{subject} | {opponent} | even",
    "grappling_edge": "{subject} | {opponent} | even",
    "footwork_edge": "{subject} | {opponent} | even",
    "overall_edge": "{subject} | {opponent} | even"
  }},
  "exploitation_plan": [
    {{
      "opponent_weakness": "string",
      "our_tool": "string",
      "timing": "string",
      "drill": "string"
    }}
  ],
  "danger_management": [
    {{
      "opponent_threat": "string",
      "defensive_response": "string",
      "positioning": "string"
    }}
  ],
  "round_strategy": {{
    "rounds_1_2": "string",
    "rounds_3_4": "string",
    "round_5": "string"
  }},
  "key_performance_indicators": ["list of metrics to track during fight"],
  "camp_priority_drills": [
    {{
      "drill": "string",
      "purpose": "string",
      "volume": "string"
    }}
  ]
}}

Output ONLY valid JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        game_plan = json.loads(raw)
    except json.JSONDecodeError:
        game_plan = {"raw_response": raw}

    game_plan["_meta"] = {
        "model": "claude-sonnet-4-6",
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    return game_plan


def run_analysis(fighter: str, opponent: str | None = None) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()

    # Process subject fighter
    subject_entries = _get_fighter_entries(manifest, fighter)
    if not subject_entries:
        print(f"[ERROR] No processed data found for '{fighter}'. Run cv_engine first.")
        sys.exit(1)

    print(f"\n[BRAIN] Analyzing: {fighter}")
    subject_stats = {}
    for entry in subject_entries:
        print(f"  Loading: {entry['parquet_path']}")
        s = _compute_movement_stats(entry["parquet_path"])
        for k, v in s.items():
            if k not in subject_stats:
                subject_stats[k] = v

    subject_report = generate_fight_signature(fighter, subject_stats, role="subject")
    subject_report["fighter"] = fighter

    subject_out = REPORTS_DIR / f"{fighter.lower().replace(' ', '_')}_signature.json"
    with open(subject_out, "w") as f:
        json.dump(subject_report, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Report → {subject_out}")

    # Process opponent if provided
    if opponent:
        opp_entries = _get_fighter_entries(manifest, opponent)
        if not opp_entries:
            print(f"[WARN] No processed data for opponent '{opponent}'. Skipping comparison.")
            return

        print(f"\n[BRAIN] Analyzing opponent: {opponent}")
        opp_stats = {}
        for entry in opp_entries:
            s = _compute_movement_stats(entry["parquet_path"])
            for k, v in s.items():
                if k not in opp_stats:
                    opp_stats[k] = v

        opp_report = generate_fight_signature(opponent, opp_stats, role="opponent")
        opp_report["fighter"] = opponent

        opp_out = REPORTS_DIR / f"{opponent.lower().replace(' ', '_')}_signature.json"
        with open(opp_out, "w") as f:
            json.dump(opp_report, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Report → {opp_out}")

        # Matchup analysis
        print(f"\n[BRAIN] Generating matchup analysis...")
        game_plan = compare_fighters(subject_report, opp_report)
        plan_out = REPORTS_DIR / f"gameplan_{fighter.lower().replace(' ', '_')}_vs_{opponent.lower().replace(' ', '_')}.json"
        with open(plan_out, "w") as f:
            json.dump(game_plan, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Game Plan → {plan_out}")

    print("\n[BRAIN] Analysis complete.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TELEMETRY FIGHT LAB — Brain Module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python brain/pattern_recognition.py --fighter "Jon Jones"
  python brain/pattern_recognition.py --fighter "Jon Jones" --opponent "Stipe Miocic"
        """,
    )
    parser.add_argument("--fighter", required=True, help="Subject fighter name")
    parser.add_argument("--opponent", help="Opponent fighter name (optional, enables matchup analysis)")
    args = parser.parse_args()

    run_analysis(fighter=args.fighter, opponent=args.opponent)


if __name__ == "__main__":
    main()
