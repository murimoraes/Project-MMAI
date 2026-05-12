"""
ingestion/downloader.py
Download fight footage from YouTube and populate data_raw/ + manifest.json
"""

import argparse
import json
import os
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("[ERROR] yt-dlp not found. Run: pip install yt-dlp")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data_raw"
MANIFEST_PATH = DATA_RAW / "manifest.json"


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r") as f:
            return json.load(f)
    return {"version": "1.0", "entries": []}


def _save_manifest(manifest: dict) -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[MANIFEST] Saved → {MANIFEST_PATH}")


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:8]


def _already_downloaded(manifest: dict, url: str) -> bool:
    uid = _url_hash(url)
    return any(e["id"] == uid for e in manifest["entries"])


def download(url: str, fighter: str, role: str = "subject") -> dict | None:
    """
    Download a YouTube video for a given fighter.

    role: 'subject' (our fighter) | 'opponent'
    Returns the manifest entry dict or None if skipped.
    """
    manifest = _load_manifest()

    if _already_downloaded(manifest, url):
        print(f"[SKIP] Already in manifest: {url}")
        return None

    uid = _url_hash(url)
    fighter_slug = fighter.lower().replace(" ", "_")
    output_dir = DATA_RAW / fighter_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / f"{uid}_%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_template,
        "writeinfojson": True,
        "writethumbnail": False,
        "quiet": False,
        "no_warnings": False,
        "progress_hooks": [_progress_hook],
    }

    print(f"\n[DOWNLOAD] Fighter: {fighter} | Role: {role}")
    print(f"[DOWNLOAD] URL: {url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    entry = {
        "id": uid,
        "fighter": fighter,
        "fighter_slug": fighter_slug,
        "role": role,
        "url": url,
        "title": info.get("title", ""),
        "duration_seconds": info.get("duration", 0),
        "filename": filename,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "processed": False,
    }

    manifest["entries"].append(entry)
    _save_manifest(manifest)

    print(f"[OK] Downloaded → {filename}")
    return entry


def _progress_hook(d: dict) -> None:
    if d["status"] == "downloading":
        pct = d.get("_percent_str", "?%").strip()
        speed = d.get("_speed_str", "?").strip()
        eta = d.get("_eta_str", "?").strip()
        print(f"\r  {pct} @ {speed} ETA {eta}   ", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\n  [DONE] {d['filename']}")


def list_manifest() -> None:
    manifest = _load_manifest()
    entries = manifest.get("entries", [])
    if not entries:
        print("[MANIFEST] Empty — no downloads yet.")
        return
    print(f"\n[MANIFEST] {len(entries)} entries:\n")
    for e in entries:
        status = "✓" if e.get("processed") else "○"
        print(f"  {status} [{e['role']:8}] {e['fighter']:20} | {e['title'][:50]}")
        print(f"           {e['filename']}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TELEMETRY FIGHT LAB — Ingestion Module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingestion/downloader.py --url https://youtu.be/xxx --fighter "Jon Jones"
  python ingestion/downloader.py --url https://youtu.be/yyy --fighter "Stipe Miocic" --role opponent
  python ingestion/downloader.py --list
        """,
    )
    parser.add_argument("--url", help="YouTube URL to download")
    parser.add_argument("--fighter", help="Fighter name (e.g. 'Jon Jones')")
    parser.add_argument(
        "--role",
        choices=["subject", "opponent"],
        default="subject",
        help="Fighter role in the analysis (default: subject)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List all downloaded entries in manifest"
    )

    args = parser.parse_args()

    if args.list:
        list_manifest()
        return

    if not args.url or not args.fighter:
        parser.print_help()
        sys.exit(1)

    download(url=args.url, fighter=args.fighter, role=args.role)


if __name__ == "__main__":
    main()
