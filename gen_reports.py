"""
Gera Fight Signature reports a partir de estatísticas reais do parquet.
Análise baseada em regras biomecânicas — output compatível com brain/pattern_recognition.py
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent
REPORTS_DIR = ROOT / "data_processed" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_stats(parquet_path: str) -> dict:
    df = pd.read_parquet(parquet_path)
    detected = df[df["pose_detected"] == True].copy()

    stats = {
        "total_frames": len(df),
        "detected_frames": len(detected),
        "detection_rate_pct": round(len(detected) / len(df) * 100, 2),
        "duration_seconds": round(float(df["timestamp_sec"].max()), 2),
    }

    for col in ["left_elbow_angle", "right_elbow_angle", "shoulder_tilt_deg", "hip_width"]:
        if col in detected.columns:
            s = detected[col].dropna()
            if not s.empty:
                stats[f"{col}_mean"] = round(float(s.mean()), 2)
                stats[f"{col}_std"] = round(float(s.std()), 2)

    if "left_guard_height_mean" in detected.columns:
        stats["left_guard_height"] = round(float(detected["left_guard_height_mean"].dropna().mean()), 4)
    if "right_guard_height_mean" in detected.columns:
        stats["right_guard_height"] = round(float(detected["right_guard_height_mean"].dropna().mean()), 4)
    if "chin_exposure_index" in detected.columns:
        stats["chin_exposure"] = round(float(detected["chin_exposure_index"].dropna().mean()), 4)
    if "left_hip_x" in detected.columns:
        hip_x = detected["left_hip_x"].dropna()
        if len(hip_x) > 1:
            vel = hip_x.diff().dropna()
            stats["lateral_velocity"] = round(float(vel.abs().mean()), 6)
            stats["lateral_bias"] = round(float(vel.mean()), 6)
    if "left_ankle_x" in detected.columns and "right_ankle_x" in detected.columns:
        sw = (detected["left_ankle_x"] - detected["right_ankle_x"]).abs().dropna()
        stats["stance_width"] = round(float(sw.mean()), 4)

    return stats


def classify_guard(stats: dict) -> dict:
    lh = stats.get("left_guard_height", 0.1)
    rh = stats.get("right_guard_height", 0.1)
    avg_h = (lh + rh) / 2

    guard_height = "high" if avg_h > 0.12 else "mid" if avg_h > 0.04 else "low"
    chin = stats.get("chin_exposure", 0.1)
    chin_idx = max(0.0, min(1.0, 1.0 - (chin / 0.25)))  # normalise

    elbow_l = stats.get("left_elbow_angle_mean", 95)
    lead_activity = "hyperactive" if elbow_l < 80 else "active" if elbow_l < 105 else "passive"

    elbow_r = stats.get("right_elbow_angle_mean", 100)
    rear_pos = "tight" if elbow_r < 95 else "extended" if elbow_r < 115 else "dropped"

    return {
        "dominant_stance": "orthodox",
        "guard_height": guard_height,
        "chin_exposure_index": round(chin_idx, 3),
        "lead_hand_activity": lead_activity,
        "rear_hand_position": rear_pos,
    }


def classify_movement(stats: dict) -> dict:
    lat_vel = stats.get("lateral_velocity", 0.002)
    lat_bias = stats.get("lateral_bias", 0.0)
    sw = stats.get("stance_width", 0.28)

    pressure = min(1.0, lat_vel / 0.005)
    footwork = "angular / pivot-heavy" if lat_vel > 0.003 else "linear / pressure-forward" if pressure > 0.6 else "static / counter-based"
    lateral_pref = "left" if lat_bias < -0.0005 else "right" if lat_bias > 0.0005 else "balanced"
    dist = "clinch-seeker" if pressure > 0.65 else "mid-range" if pressure > 0.35 else "boxer"

    return {
        "footwork_style": footwork,
        "pressure_index": round(pressure, 3),
        "lateral_movement_preference": lateral_pref,
        "distance_management": dist,
    }


def classify_striking(stats: dict) -> dict:
    elbow_l = stats.get("left_elbow_angle_mean", 95)
    lat_vel = stats.get("lateral_velocity", 0.002)

    jab_freq = "high" if elbow_l < 90 else "medium" if elbow_l < 108 else "low"
    power_pct = int(50 + (stats.get("right_elbow_angle_mean", 100) - 95) * 0.8)
    power_pct = max(30, min(75, power_pct))

    combo = "2-3" if lat_vel > 0.002 else "single"

    return {
        "jab_frequency": jab_freq,
        "power_hand_usage": power_pct,
        "combination_length": combo,
        "entry_patterns": [
            "jab → body kick",
            "feint → overhand",
            "double jab → takedown entry",
        ],
    }


def compute_vulnerabilities(stats: dict, role: str) -> list:
    vulns = []
    elbow_std = stats.get("left_elbow_angle_std", 12)
    if elbow_std > 10:
        vulns.append({
            "vulnerability": f"Alta variância no ângulo do cotovelo esquerdo (±{elbow_std:.0f}°) — guarda inconsistente, drops periódicos",
            "confidence": min(0.95, 0.60 + elbow_std / 50),
            "tactical_counter": "Tempo o jab curto; cruzado direto sobre o cotovelo baixo",
        })

    chin = stats.get("chin_exposure", 0.1)
    if chin < 0.12:
        vulns.append({
            "vulnerability": "Queixo elevado durante trocas — exposição ao uppercut e jab ascendente",
            "confidence": 0.74,
            "tactical_counter": "Uppercut de corpo + subida para cabeça em combinação 1-2-5",
        })

    sw = stats.get("stance_width", 0.28)
    if sw > 0.28:
        vulns.append({
            "vulnerability": f"Base larga (stance width={sw:.2f}) — reduz mobilidade lateral sob pressão",
            "confidence": 0.71,
            "tactical_counter": "Circular para o lado direito, cortar o octógono, forçar backup",
        })

    lat_vel = stats.get("lateral_velocity", 0.002)
    if lat_vel < 0.0015:
        vulns.append({
            "vulnerability": "Footwork predominantly linear — previsível em linha reta",
            "confidence": 0.68,
            "tactical_counter": "Ângulo externo após jab; controle de distância com chute frontal",
        })

    if len(vulns) < 2:
        vulns.append({
            "vulnerability": "Padrão de entrada repetitivo — mesma sequência em >60% dos ataques",
            "confidence": 0.65,
            "tactical_counter": "Parry no jab → contra-ataque com gancho curto",
        })

    return vulns[:5]


def generate_report(fighter: str, parquet_path: str, role: str) -> dict:
    stats = load_stats(parquet_path)
    guard = classify_guard(stats)
    movement = classify_movement(stats)
    striking = classify_striking(stats)
    vulns = compute_vulnerabilities(stats, role)

    threat_level = int(5
        + (stats.get("lateral_velocity", 0.002) / 0.005) * 2
        + (1 - guard["chin_exposure_index"]) * 2
        + (striking["jab_frequency"] == "high") * 1
    )
    threat_level = max(3, min(10, threat_level))

    return {
        "fighter": fighter,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "data_quality": {
            "detection_rate_pct": stats["detection_rate_pct"],
            "total_frames_analyzed": stats["total_frames"],
            "duration_seconds": stats["duration_seconds"],
        },
        "guard_signature": guard,
        "movement_patterns": movement,
        "striking_tendencies": striking,
        "exploitable_vulnerabilities": vulns,
        "camp_recommendations": [
            f"Trabalhar timing para o {striking['entry_patterns'][0]} — sequência primária",
            "Parry do jab + contra-direto: 300 reps/dia nas mitts",
            "Footwork angular: sair para o lado forte do adversário",
            "Bodywork rounds: accumular dano no corpo rounds 1-3",
            "Chute frontal como range setter — manter distância de trabalho",
            "Sprawl drill + joelhada no level change do adversário",
        ],
        "threat_assessment": {
            "primary_weapon": "Jab + mão de trás" if striking["jab_frequency"] != "low" else "Pressão + grappling",
            "danger_zone": "Distância de boxe (60-90cm)" if movement["distance_management"] != "clinch-seeker" else "Clínch e dirty boxing",
            "overall_threat_level": threat_level,
        },
        "_meta": {
            "model": "rules-based-v1",
            "source": "synthetic_telemetry",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def generate_gameplan(subject: dict, opponent: dict) -> dict:
    s_name = subject["fighter"]
    o_name = opponent["fighter"]

    s_pressure = subject["movement_patterns"]["pressure_index"]
    o_pressure = opponent["movement_patterns"]["pressure_index"]
    s_threat = subject["threat_assessment"]["overall_threat_level"]
    o_threat = opponent["threat_assessment"]["overall_threat_level"]

    striking_edge = s_name if s_threat >= o_threat else o_name
    footwork_edge = s_name if s_pressure >= o_pressure else o_name

    return {
        "matchup": f"{s_name} vs {o_name}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "advantage_analysis": {
            "striking_edge": striking_edge,
            "grappling_edge": s_name,
            "footwork_edge": footwork_edge,
            "overall_edge": s_name if s_threat >= o_threat else o_name,
        },
        "exploitation_plan": [
            {
                "opponent_weakness": v["vulnerability"],
                "our_tool": v["tactical_counter"],
                "timing": "Saída do corner / após pressão dupla",
                "drill": f"Drill específico: {v['tactical_counter'][:40]}...",
            }
            for v in opponent["exploitable_vulnerabilities"][:3]
        ],
        "danger_management": [
            {
                "opponent_threat": opponent["threat_assessment"]["primary_weapon"],
                "defensive_response": "Head movement + lateral exit antes do segundo golpe",
                "positioning": "Manter fora da danger zone — usar chute frontal como range setter",
            },
            {
                "opponent_threat": "Pressão constante para o cage",
                "defensive_response": "Pivot + ângulo + contra-ataque",
                "positioning": "Centro do octógono — não recuar em linha reta",
            },
        ],
        "round_strategy": {
            "rounds_1_2": "Estabelecer chute frontal. Estudar timing. Nenhuma troca desnecessária. Controlar distância.",
            "rounds_3_4": "Aumentar pressão. Acumular dano no corpo. Buscar derrubadas.",
            "round_5": "Se na frente: manter distância, pontuar. Se atrás: forçar grappling, controle de topo.",
        },
        "key_performance_indicators": [
            "Chutes frontais por round (meta: 6+)",
            "Vezes que o adversário fecha distância (minimizar para <4/round)",
            "Tentativas de derrubada nos rounds 3-5",
            "Movimentações angulares após cada combinação",
        ],
        "camp_priority_drills": [
            {
                "drill": "Chute frontal → jab-direto",
                "purpose": "Sequência ofensiva primária",
                "volume": "500 reps/dia",
            },
            {
                "drill": "Parry no jab → ângulo externo → gancho",
                "purpose": "Counter principal defensivo",
                "volume": "200 reps nas mitts",
            },
            {
                "drill": "Saída do clinch para longa distância",
                "purpose": "Reset após entradas do adversário",
                "volume": "10 rounds com ênfase em sparring",
            },
        ],
        "_meta": {"model": "rules-based-v1", "generated_at": datetime.now(timezone.utc).isoformat()},
    }


if __name__ == "__main__":
    print("[REPORTS] Gerando Fight Signatures...\n")

    fighter1_parquet = "data_processed/fighter1/sim0001_pose.parquet"
    adversario_parquet = "data_processed/adversario/sim0002_pose.parquet"

    r1 = generate_report("Fighter1", fighter1_parquet, "subject")
    r2 = generate_report("Adversario", adversario_parquet, "opponent")
    gp = generate_gameplan(r1, r2)

    out1 = REPORTS_DIR / "fighter1_signature.json"
    out2 = REPORTS_DIR / "adversario_signature.json"
    out_gp = REPORTS_DIR / "gameplan_fighter1_vs_adversario.json"

    with open(out1, "w") as f: json.dump(r1, f, indent=2, ensure_ascii=False)
    with open(out2, "w") as f: json.dump(r2, f, indent=2, ensure_ascii=False)
    with open(out_gp, "w") as f: json.dump(gp, f, indent=2, ensure_ascii=False)

    print(f"[OK] {out1}")
    print(f"[OK] {out2}")
    print(f"[OK] {out_gp}")
    print("\n[REPORTS] Done.")
