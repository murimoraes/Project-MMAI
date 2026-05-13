"""
Gera dados de telemetria sintéticos realistas para simular saída do cv_engine.
Usa distribuições estatísticas baseadas em footage real de MMA.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent
DATA_RAW = ROOT / "data_raw"
DATA_PROCESSED = ROOT / "data_processed"
MANIFEST_PATH = DATA_RAW / "manifest.json"

LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
]

def gen_fighter_telemetry(
    fighter_slug: str,
    entry_id: str,
    fps: float = 30.0,
    duration_s: float = 60.0,
    profile: dict = None,
):
    """Gera parquet de telemetria com perfil de estilo de luta customizável."""
    rng = np.random.default_rng(hash(fighter_slug) % 2**31)
    n_frames = int(fps * duration_s)

    # Perfil padrão (guarda média, movimento balanceado)
    p = {
        "guard_height": 0.15,       # wrist above shoulder (positive = high guard)
        "chin_tuck": 0.10,          # nose below shoulder avg
        "elbow_angle_l": 95.0,      # left elbow mean angle
        "elbow_angle_r": 100.0,
        "stance_width": 0.28,
        "lateral_bias": 0.0,        # positive = moving right
        "pressure": 0.6,
        "detection_rate": 0.85,
    }
    if profile:
        p.update(profile)

    t = np.linspace(0, duration_s, n_frames)
    records = []

    # Base landmarks (normalized 0-1 viewport)
    base = {
        "nose_x": 0.50, "nose_y": 0.25,
        "left_shoulder_x": 0.42, "left_shoulder_y": 0.38,
        "right_shoulder_x": 0.58, "right_shoulder_y": 0.38,
        "left_elbow_x": 0.35, "left_elbow_y": 0.50,
        "right_elbow_x": 0.65, "right_elbow_y": 0.50,
        "left_wrist_x": 0.38, "left_wrist_y": 0.38 - p["guard_height"],
        "right_wrist_x": 0.62, "right_wrist_y": 0.38 - p["guard_height"],
        "left_hip_x": 0.44, "left_hip_y": 0.60,
        "right_hip_x": 0.56, "right_hip_y": 0.60,
        "left_knee_x": 0.42, "left_knee_y": 0.75,
        "right_knee_x": 0.58, "right_knee_y": 0.75,
        "left_ankle_x": 0.44 - p["stance_width"] / 2, "left_ankle_y": 0.90,
        "right_ankle_x": 0.56 + p["stance_width"] / 2, "right_ankle_y": 0.90,
    }

    # Lateral drift (footwork simulation)
    lateral_drift = np.cumsum(
        rng.normal(p["lateral_bias"] * 0.001, 0.002, n_frames)
    )
    lateral_drift -= lateral_drift.mean()
    lateral_drift = np.clip(lateral_drift, -0.15, 0.15)

    for i in range(n_frames):
        detected = rng.random() < p["detection_rate"]

        row = {
            "frame": i,
            "timestamp_sec": round(t[i], 4),
            "pose_detected": detected,
        }

        if detected:
            drift = lateral_drift[i]
            noise = rng.normal(0, 0.005, len(LANDMARK_NAMES) * 4)
            ni = 0

            for name in LANDMARK_NAMES:
                if f"{name}_x" in base:
                    row[f"{name}_x"] = round(base[f"{name}_x"] + drift + noise[ni], 6)
                    row[f"{name}_y"] = round(base[f"{name}_y"] + noise[ni + 1], 6)
                else:
                    row[f"{name}_x"] = round(0.5 + drift + noise[ni], 6)
                    row[f"{name}_y"] = round(0.5 + noise[ni + 1], 6)
                row[f"{name}_z"] = round(noise[ni + 2] * 0.1, 6)
                row[f"{name}_vis"] = round(min(0.95, 0.7 + rng.random() * 0.3), 4)
                ni += 4

            # Computed angles
            # Elbow angle (simplified)
            angle_noise_l = rng.normal(0, 8.0)
            angle_noise_r = rng.normal(0, 8.0)

            # Simulate periodic guard drops (vulnerability)
            guard_drop = 20.0 if (i % 90) < 10 else 0.0  # drops every ~3s for 0.3s

            row["left_elbow_angle"] = round(p["elbow_angle_l"] + angle_noise_l + guard_drop, 2)
            row["right_elbow_angle"] = round(p["elbow_angle_r"] + angle_noise_r, 2)

            # Shoulder tilt
            ls_x = row.get("left_shoulder_x", 0.42)
            rs_x = row.get("right_shoulder_x", 0.58)
            ls_y = row.get("left_shoulder_y", 0.38)
            rs_y = row.get("right_shoulder_y", 0.38)
            row["shoulder_tilt_deg"] = round(
                np.degrees(np.arctan2(ls_y - rs_y, ls_x - rs_x)), 2
            )

            # Hip width
            lh_x = row.get("left_hip_x", 0.44)
            rh_x = row.get("right_hip_x", 0.56)
            row["hip_width"] = round(abs(lh_x - rh_x), 4)

            # Guard height (wrist above shoulder)
            row["left_guard_height_mean"] = round(
                base["left_shoulder_y"] - base["left_wrist_y"] + rng.normal(0, 0.01), 4
            )
            row["right_guard_height_mean"] = round(
                base["right_shoulder_y"] - base["right_wrist_y"] + rng.normal(0, 0.01), 4
            )

            # Chin exposure
            shoulder_avg_y = (ls_y + rs_y) / 2
            nose_y = row.get("nose_y", 0.25)
            row["chin_exposure_index"] = round(shoulder_avg_y - nose_y + rng.normal(0, 0.01), 4)

        else:
            for name in LANDMARK_NAMES:
                row[f"{name}_x"] = None
                row[f"{name}_y"] = None
                row[f"{name}_z"] = None
                row[f"{name}_vis"] = None

        records.append(row)

    df = pd.DataFrame(records)
    out_dir = DATA_PROCESSED / fighter_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{entry_id}_pose.parquet"
    df.to_parquet(out_path, index=False, compression="snappy")
    print(f"  [SIM] {fighter_slug}: {len(df)} frames → {out_path}")
    return str(out_path)


def inject_manifest(fighter: str, fighter_slug: str, role: str, entry_id: str, parquet_path: str):
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)
    else:
        manifest = {"version": "1.0", "entries": []}

    # Remove old entry if exists
    manifest["entries"] = [e for e in manifest["entries"] if e["id"] != entry_id]

    manifest["entries"].append({
        "id": entry_id,
        "fighter": fighter,
        "fighter_slug": fighter_slug,
        "role": role,
        "url": "",
        "title": f"{fighter} — Fight Footage (simulated)",
        "duration_seconds": 60,
        "filename": "",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "processed": True,
        "parquet_path": parquet_path,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    })

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  [MANIFEST] updated for {fighter}")


if __name__ == "__main__":
    print("[SIM] Generating telemetry for Fighter1 (subject)...")
    path1 = gen_fighter_telemetry(
        fighter_slug="fighter1",
        entry_id="sim0001",
        fps=30.0,
        duration_s=60.0,
        profile={
            "guard_height": 0.08,      # mid guard
            "chin_tuck": 0.12,
            "elbow_angle_l": 88.0,     # tight guard
            "elbow_angle_r": 105.0,    # slightly open rear hand
            "stance_width": 0.30,
            "lateral_bias": -0.002,    # moves left
            "pressure": 0.55,
            "detection_rate": 0.88,
        },
    )
    inject_manifest("Fighter1", "fighter1", "subject", "sim0001", path1)

    print("\n[SIM] Generating telemetry for Adversario (opponent)...")
    path2 = gen_fighter_telemetry(
        fighter_slug="adversario",
        entry_id="sim0002",
        fps=30.0,
        duration_s=60.0,
        profile={
            "guard_height": 0.18,      # high guard
            "chin_tuck": 0.06,         # chin somewhat exposed
            "elbow_angle_l": 112.0,    # looser lead arm
            "elbow_angle_r": 95.0,
            "stance_width": 0.24,      # narrower stance
            "lateral_bias": 0.001,     # moves right
            "pressure": 0.72,          # high pressure fighter
            "detection_rate": 0.82,
        },
    )
    inject_manifest("Adversario", "adversario", "opponent", "sim0002", path2)

    print("\n[SIM] Done. Ready for brain/pattern_recognition.py")
