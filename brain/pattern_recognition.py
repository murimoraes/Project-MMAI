"""
brain/pattern_recognition.py
Analyze movement vectors, detect patterns, and generate Fight Signature reports via Claude.
Uses Tool Use for structured output and Prompt Caching to reduce cost on repeated calls.
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

Use the provided tools to submit structured analysis reports. Be precise, tactical, and use MMA-specific terminology. All analysis must be grounded in the data provided.

Key telemetry interpretation guidelines:
- left_elbow_angle_mean: Lower angles (<90°) = tight guard; Higher (>120°) = extended/dropped guard
- left_guard_height_mean / right_guard_height_mean: Positive = hand above shoulder (high guard); Negative = hand below (dropped guard)
- chin_exposure_index: Higher positive = chin tucked; Lower/negative = chin up (exposed)
- lateral_velocity_mean: Higher = more active footwork; lateral_bias positive = moving right, negative = left
- shoulder_tilt_deg_mean: Near 0° = square stance; significant tilt = bladed stance
- stance_width_mean: Wider = more grounded/less mobile; Narrower = more mobile/less stable"""

FIGHT_SIGNATURE_TOOL = {
    "name": "submit_fight_signature",
    "description": "Submit a complete structured Fight Signature report based on telemetry data analysis.",
    "input_schema": {
        "type": "object",
        "required": [
            "guard_signature",
            "movement_patterns",
            "striking_tendencies",
            "exploitable_vulnerabilities",
            "camp_recommendations",
            "threat_assessment",
        ],
        "properties": {
            "guard_signature": {
                "type": "object",
                "required": ["dominant_stance", "guard_height", "chin_exposure_index", "lead_hand_activity", "rear_hand_position"],
                "properties": {
                    "dominant_stance": {"type": "string", "enum": ["orthodox", "southpaw", "switch"]},
                    "guard_height": {"type": "string", "enum": ["high", "mid", "low"]},
                    "chin_exposure_index": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "lead_hand_activity": {"type": "string", "enum": ["passive", "active", "hyperactive"]},
                    "rear_hand_position": {"type": "string", "enum": ["tight", "extended", "dropped"]},
                },
            },
            "movement_patterns": {
                "type": "object",
                "required": ["footwork_style", "pressure_index", "lateral_movement_preference", "distance_management"],
                "properties": {
                    "footwork_style": {"type": "string"},
                    "pressure_index": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "lateral_movement_preference": {"type": "string", "enum": ["left", "right", "balanced"]},
                    "distance_management": {"type": "string", "enum": ["clinch-seeker", "mid-range", "boxer"]},
                },
            },
            "striking_tendencies": {
                "type": "object",
                "required": ["jab_frequency", "power_hand_usage", "combination_length", "entry_patterns"],
                "properties": {
                    "jab_frequency": {"type": "string", "enum": ["low", "medium", "high"]},
                    "power_hand_usage": {"type": "number", "minimum": 0, "maximum": 100},
                    "combination_length": {"type": "string", "enum": ["single", "2-3", "4+"]},
                    "entry_patterns": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                },
            },
            "exploitable_vulnerabilities": {
                "type": "array",
                "minItems": 2,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "required": ["vulnerability", "confidence", "tactical_counter"],
                    "properties": {
                        "vulnerability": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "tactical_counter": {"type": "string"},
                    },
                },
            },
            "camp_recommendations": {
                "type": "array",
                "minItems": 4,
                "maxItems": 6,
                "items": {"type": "string"},
            },
            "threat_assessment": {
                "type": "object",
                "required": ["primary_weapon", "danger_zone", "overall_threat_level"],
                "properties": {
                    "primary_weapon": {"type": "string"},
                    "danger_zone": {"type": "string"},
                    "overall_threat_level": {"type": "integer", "minimum": 1, "maximum": 10},
                },
            },
        },
    },
}

GAME_PLAN_TOOL = {
    "name": "submit_game_plan",
    "description": "Submit a structured tactical game plan for a fighter matchup.",
    "input_schema": {
        "type": "object",
        "required": [
            "advantage_analysis",
            "exploitation_plan",
            "danger_management",
            "round_strategy",
            "key_performance_indicators",
            "camp_priority_drills",
        ],
        "properties": {
            "advantage_analysis": {
                "type": "object",
                "required": ["striking_edge", "grappling_edge", "footwork_edge", "overall_edge"],
                "properties": {
                    "striking_edge": {"type": "string"},
                    "grappling_edge": {"type": "string"},
                    "footwork_edge": {"type": "string"},
                    "overall_edge": {"type": "string"},
                },
            },
            "exploitation_plan": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "object",
                    "required": ["opponent_weakness", "our_tool", "timing", "drill"],
                    "properties": {
                        "opponent_weakness": {"type": "string"},
                        "our_tool": {"type": "string"},
                        "timing": {"type": "string"},
                        "drill": {"type": "string"},
                    },
                },
            },
            "danger_management": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "object",
                    "required": ["opponent_threat", "defensive_response", "positioning"],
                    "properties": {
                        "opponent_threat": {"type": "string"},
                        "defensive_response": {"type": "string"},
                        "positioning": {"type": "string"},
                    },
                },
            },
            "round_strategy": {
                "type": "object",
                "required": ["rounds_1_2", "rounds_3_4", "round_5"],
                "properties": {
                    "rounds_1_2": {"type": "string"},
                    "rounds_3_4": {"type": "string"},
                    "round_5": {"type": "string"},
                },
            },
            "key_performance_indicators": {
                "type": "array",
                "minItems": 3,
                "items": {"type": "string"},
            },
            "camp_priority_drills": {
                "type": "array",
                "minItems": 3,
                "items": {
                    "type": "object",
                    "required": ["drill", "purpose", "volume"],
                    "properties": {
                        "drill": {"type": "string"},
                        "purpose": {"type": "string"},
                        "volume": {"type": "string"},
                    },
                },
            },
        },
    },
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

    for col in ["left_elbow_angle", "right_elbow_angle", "shoulder_tilt_deg", "hip_width"]:
        if col in detected.columns:
            series = detected[col].dropna()
            if not series.empty:
                stats[f"{col}_mean"] = round(float(series.mean()), 2)
                stats[f"{col}_std"] = round(float(series.std()), 2)
                stats[f"{col}_min"] = round(float(series.min()), 2)
                stats[f"{col}_max"] = round(float(series.max()), 2)

    if "left_wrist_y" in detected.columns and "left_shoulder_y" in detected.columns:
        left_hand_height = (detected["left_shoulder_y"] - detected["left_wrist_y"]).dropna()
        stats["left_guard_height_mean"] = round(float(left_hand_height.mean()), 4)

    if "right_wrist_y" in detected.columns and "right_shoulder_y" in detected.columns:
        right_hand_height = (detected["right_shoulder_y"] - detected["right_wrist_y"]).dropna()
        stats["right_guard_height_mean"] = round(float(right_hand_height.mean()), 4)

    if all(c in detected.columns for c in ["nose_y", "left_shoulder_y", "right_shoulder_y"]):
        shoulder_avg = (detected["left_shoulder_y"] + detected["right_shoulder_y"]) / 2
        chin_exp = (shoulder_avg - detected["nose_y"]).dropna()
        stats["chin_exposure_index"] = round(float(chin_exp.mean()), 4)

    if "left_hip_x" in detected.columns:
        hip_x = detected["left_hip_x"].dropna()
        if len(hip_x) > 1:
            velocity = hip_x.diff().dropna()
            stats["lateral_velocity_mean"] = round(float(velocity.abs().mean()), 6)
            stats["lateral_bias"] = round(float(velocity.mean()), 6)

    if "left_ankle_x" in detected.columns and "right_ankle_x" in detected.columns:
        stance = (detected["left_ankle_x"] - detected["right_ankle_x"]).abs().dropna()
        stats["stance_width_mean"] = round(float(stance.mean()), 4)

    return stats


def _get_anthropic_client():
    """Return an authenticated Anthropic client, reading from .env if needed."""
    try:
        import anthropic
    except ImportError:
        print("[ERROR] anthropic SDK not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        env_path = ROOT / ".env"
        if env_path.exists():
            for line in open(env_path):
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.strip().split("=", 1)[1]
                    break

    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set. Add it to .env or environment.")
        sys.exit(1)

    return anthropic.Anthropic(api_key=api_key)


def _call_with_tool_use(user_prompt: str, tool: dict) -> tuple[dict, dict]:
    """
    Call Claude with Tool Use + Prompt Caching.
    Returns (tool_input, usage_stats).
    The system prompt is cached to reduce cost on repeated calls.
    """
    client = _get_anthropic_client()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": user_prompt}],
    )

    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
        "cache_write_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
    }

    for block in response.content:
        if block.type == "tool_use" and block.name == tool["name"]:
            return block.input, usage

    raise RuntimeError(f"Claude did not call tool '{tool['name']}' as expected")


def generate_fight_signature(fighter: str, stats: dict, role: str = "opponent") -> dict:
    """Generate Fight Signature report via Claude Tool Use with Prompt Caching."""
    print(f"  [CLAUDE] Generating Fight Signature for {fighter}...")

    stats_str = json.dumps(stats, indent=2)
    prompt = f"""Analyze the following telemetry data for fighter: **{fighter}** (role: {role})

## Movement Telemetry Statistics
```json
{stats_str}
```

Generate a complete Fight Signature by calling submit_fight_signature. Identify at minimum 2 and maximum 5 specific vulnerabilities, and provide 4-6 actionable camp training directives."""

    result, usage = _call_with_tool_use(prompt, FIGHT_SIGNATURE_TOOL)

    report = dict(result)
    report["fighter"] = fighter
    report["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    report["data_quality"] = {
        "detection_rate_pct": stats.get("detection_rate_pct", 0.0),
        "total_frames_analyzed": stats.get("total_frames", 0),
        "duration_seconds": stats.get("duration_seconds", 0.0),
    }
    report["_meta"] = {
        "model": "claude-sonnet-4-6",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "cache_read_tokens": usage["cache_read_tokens"],
        "cache_write_tokens": usage["cache_write_tokens"],
    }

    cached = usage["cache_read_tokens"]
    if cached:
        print(f"  [CACHE] {cached:,} tokens read from cache (cost saved)")

    return report


def compare_fighters(subject_report: dict, opponent_report: dict) -> dict:
    """Cross-analyze subject vs opponent to generate tactical game plan via Tool Use."""
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

Generate a complete tactical game plan by calling submit_game_plan. Focus on concrete, actionable tactics derived from the telemetry data."""

    result, usage = _call_with_tool_use(prompt, GAME_PLAN_TOOL)

    game_plan = dict(result)
    game_plan["matchup"] = f"{subject} vs {opponent}"
    game_plan["generated_at"] = datetime.now(timezone.utc).isoformat()
    game_plan["_meta"] = {
        "model": "claude-sonnet-4-6",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "cache_read_tokens": usage["cache_read_tokens"],
        "cache_write_tokens": usage["cache_write_tokens"],
    }

    cached = usage["cache_read_tokens"]
    if cached:
        print(f"  [CACHE] {cached:,} tokens read from cache (cost saved)")

    return game_plan


def run_analysis(fighter: str, opponent: str | None = None) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()

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

    subject_out = REPORTS_DIR / f"{fighter.lower().replace(' ', '_')}_signature.json"
    with open(subject_out, "w") as f:
        json.dump(subject_report, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Report → {subject_out}")

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

        opp_out = REPORTS_DIR / f"{opponent.lower().replace(' ', '_')}_signature.json"
        with open(opp_out, "w") as f:
            json.dump(opp_report, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Report → {opp_out}")

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
