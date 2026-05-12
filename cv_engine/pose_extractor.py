"""
cv_engine/pose_extractor.py
Extract MediaPipe pose keypoints from fight footage and export as .parquet
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data_raw"
DATA_PROCESSED = ROOT / "data_processed"
MANIFEST_PATH = DATA_RAW / "manifest.json"

# MediaPipe landmark indices (33 total)
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

# Key joints for combat analysis
COMBAT_JOINTS = {
    "left_shoulder": 11, "right_shoulder": 12,
    "left_elbow": 13, "right_elbow": 14,
    "left_wrist": 15, "right_wrist": 16,
    "left_hip": 23, "right_hip": 24,
    "left_knee": 25, "right_knee": 26,
    "left_ankle": 27, "right_ankle": 28,
    "nose": 0,
}


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print("[ERROR] manifest.json not found. Run ingestion/downloader.py first.")
        sys.exit(1)
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def _save_manifest(manifest: dict) -> None:
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def _compute_angles(row: dict) -> dict:
    """Compute key combat angles from landmark coordinates."""
    angles = {}

    def vec(a, b):
        return np.array([b[0] - a[0], b[1] - a[1]])

    def angle_deg(v1, v2):
        cos_a = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
        return float(np.degrees(np.arccos(np.clip(cos_a, -1, 1))))

    def pt(name):
        return [row.get(f"{name}_x", 0.0), row.get(f"{name}_y", 0.0)]

    # Elbow angles (guard posture)
    try:
        angles["left_elbow_angle"] = angle_deg(
            vec(pt("left_shoulder"), pt("left_elbow")),
            vec(pt("left_wrist"), pt("left_elbow")),
        )
        angles["right_elbow_angle"] = angle_deg(
            vec(pt("right_shoulder"), pt("right_elbow")),
            vec(pt("right_wrist"), pt("right_elbow")),
        )
    except Exception:
        angles["left_elbow_angle"] = None
        angles["right_elbow_angle"] = None

    # Hip width (stance measurement)
    try:
        lhip = pt("left_hip")
        rhip = pt("right_hip")
        angles["hip_width"] = float(abs(lhip[0] - rhip[0]))
    except Exception:
        angles["hip_width"] = None

    # Shoulder tilt
    try:
        ls = pt("left_shoulder")
        rs = pt("right_shoulder")
        angles["shoulder_tilt_deg"] = float(
            np.degrees(np.arctan2(ls[1] - rs[1], ls[0] - rs[0]))
        )
    except Exception:
        angles["shoulder_tilt_deg"] = None

    return angles


def extract_pose(video_path: str, fighter_slug: str, entry_id: str) -> Path | None:
    """Extract pose from video and save as parquet. Returns output path."""
    try:
        import mediapipe as mp
        import cv2
        import pandas as pd
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Run: pip install mediapipe opencv-python pandas pyarrow")
        sys.exit(1)

    mp_pose = mp.solutions.pose
    output_dir = DATA_PROCESSED / fighter_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{entry_id}_pose.parquet"

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"  Video: {Path(video_path).name}")
    print(f"  FPS: {fps:.1f} | Frames: {total_frames}")

    records = []
    frame_idx = 0

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            row = {
                "frame": frame_idx,
                "timestamp_sec": round(frame_idx / fps, 4),
                "pose_detected": results.pose_landmarks is not None,
            }

            if results.pose_landmarks:
                for idx, name in enumerate(LANDMARK_NAMES):
                    lm = results.pose_landmarks.landmark[idx]
                    row[f"{name}_x"] = round(lm.x, 6)
                    row[f"{name}_y"] = round(lm.y, 6)
                    row[f"{name}_z"] = round(lm.z, 6)
                    row[f"{name}_vis"] = round(lm.visibility, 4)

                angles = _compute_angles(row)
                row.update(angles)
            else:
                for name in LANDMARK_NAMES:
                    row[f"{name}_x"] = None
                    row[f"{name}_y"] = None
                    row[f"{name}_z"] = None
                    row[f"{name}_vis"] = None

            records.append(row)
            frame_idx += 1

            if frame_idx % 300 == 0:
                pct = (frame_idx / total_frames * 100) if total_frames > 0 else 0
                print(f"  Progress: {frame_idx}/{total_frames} ({pct:.1f}%)")

    cap.release()

    df = pd.DataFrame(records)
    df.to_parquet(output_path, index=False, compression="snappy")

    detection_rate = df["pose_detected"].mean() * 100
    print(f"  [OK] Saved → {output_path}")
    print(f"  Frames: {len(df)} | Pose detected: {detection_rate:.1f}%")

    return output_path


def process_manifest(manifest_path: Path | None = None) -> None:
    manifest = _load_manifest()
    entries = manifest.get("entries", [])
    pending = [e for e in entries if not e.get("processed")]

    if not pending:
        print("[INFO] All entries already processed.")
        return

    print(f"[CV ENGINE] Processing {len(pending)} pending entries...\n")

    for entry in pending:
        video_path = entry.get("filename", "")
        if not Path(video_path).exists():
            print(f"[WARN] File not found: {video_path} — skipping")
            continue

        print(f"[EXTRACT] {entry['fighter']} ({entry['role']})")
        output = extract_pose(
            video_path=video_path,
            fighter_slug=entry["fighter_slug"],
            entry_id=entry["id"],
        )

        if output:
            entry["processed"] = True
            entry["parquet_path"] = str(output)
            entry["processed_at"] = datetime.now(timezone.utc).isoformat()
            _save_manifest(manifest)
            print()

    print("[CV ENGINE] Done.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TELEMETRY FIGHT LAB — CV Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cv_engine/pose_extractor.py
  python cv_engine/pose_extractor.py --manifest data_raw/manifest.json
  python cv_engine/pose_extractor.py --video path/to/fight.mp4 --fighter jon_jones --id abc123
        """,
    )
    parser.add_argument("--manifest", help="Path to manifest.json (default: data_raw/manifest.json)")
    parser.add_argument("--video", help="Process a single video file directly")
    parser.add_argument("--fighter", help="Fighter slug (used with --video)")
    parser.add_argument("--id", help="Entry ID (used with --video)")

    args = parser.parse_args()

    if args.video:
        if not args.fighter or not args.id:
            print("[ERROR] --video requires --fighter and --id")
            sys.exit(1)
        extract_pose(args.video, args.fighter, args.id)
    else:
        process_manifest(Path(args.manifest) if args.manifest else None)


if __name__ == "__main__":
    main()
