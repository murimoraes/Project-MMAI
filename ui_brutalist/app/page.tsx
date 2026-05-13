"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import GuardPanel from "@/components/GuardPanel";
import MovementPanel from "@/components/MovementPanel";
import StrikingPanel from "@/components/StrikingPanel";
import VulnerabilityPanel from "@/components/VulnerabilityPanel";
import ThreatPanel from "@/components/ThreatPanel";
import GamePlanPanel from "@/components/GamePlanPanel";
import DataQualityBar from "@/components/DataQualityBar";
import CampPanel from "@/components/CampPanel";
import { MOCK_SUBJECT, MOCK_OPPONENT, MOCK_GAMEPLAN } from "@/lib/mock-data";
import { FightSignature, GamePlan } from "@/lib/types";

type Tab = "subject" | "opponent" | "gameplan";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<Tab>("subject");
  const [subject, setSubject] = useState<FightSignature>(MOCK_SUBJECT);
  const [opponent, setOpponent] = useState<FightSignature>(MOCK_OPPONENT);
  const [gamePlan, setGamePlan] = useState<GamePlan>(MOCK_GAMEPLAN);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetch("/api/reports")
      .then((r) => r.json())
      .then((data: { reports: Record<string, FightSignature | GamePlan> }) => {
        const reports = data.reports;
        const keys = Object.keys(reports);

        const subjectKey = keys.find((k) => k.includes("fighter1") || k.includes("subject"));
        const opponentKey = keys.find((k) => k.includes("adversario") || k.includes("opponent"));
        const gamePlanKey = keys.find((k) => k.startsWith("gameplan"));

        if (subjectKey) setSubject(reports[subjectKey] as FightSignature);
        if (opponentKey) setOpponent(reports[opponentKey] as FightSignature);
        if (gamePlanKey) setGamePlan(reports[gamePlanKey] as GamePlan);
        setLoaded(true);
      })
      .catch(() => setLoaded(true));
  }, []);

  return (
    <div className="min-h-screen bg-asphalt">
      <Header
        fighter={subject.fighter}
        opponent={opponent.fighter}
        status={loaded ? "ANÁLISE PRONTA" : "CARREGANDO..."}
      />

      {/* Tab bar */}
      <div className="border-b border-dim flex">
        {(["subject", "opponent", "gameplan"] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 font-mono text-xs uppercase tracking-widest border-r border-dim transition-colors
              ${
                activeTab === tab
                  ? "bg-neon text-black font-bold"
                  : "text-ghost hover:text-white hover:bg-steel"
              }`}
          >
            {tab === "subject"
              ? `◆ ${subject.fighter}`
              : tab === "opponent"
              ? `▲ ${opponent.fighter}`
              : "⚡ GAME PLAN"}
          </button>
        ))}

        <div className="flex-1 flex items-center justify-end px-6">
          <span className="text-dim font-mono text-2xs">
            {new Date().toISOString().replace("T", " ").slice(0, 19)} UTC
          </span>
        </div>
      </div>

      {/* Subject view */}
      {activeTab === "subject" && (
        <div className="p-4 space-y-4">
          <DataQualityBar
            detectionRate={subject.data_quality.detection_rate_pct}
            totalFrames={subject.data_quality.total_frames_analyzed}
            durationSeconds={subject.data_quality.duration_seconds}
            fighter={subject.fighter}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <GuardPanel data={subject.guard_signature} fighter={subject.fighter} />
            <MovementPanel data={subject.movement_patterns} />
            <StrikingPanel data={subject.striking_tendencies} />
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <VulnerabilityPanel
              data={subject.exploitable_vulnerabilities}
              fighter={subject.fighter}
            />
            <div className="space-y-4">
              <ThreatPanel data={subject.threat_assessment} fighter={subject.fighter} />
              <CampPanel
                recommendations={subject.camp_recommendations}
                fighter={subject.fighter}
              />
            </div>
          </div>
        </div>
      )}

      {/* Opponent view */}
      {activeTab === "opponent" && (
        <div className="p-4 space-y-4">
          <DataQualityBar
            detectionRate={opponent.data_quality.detection_rate_pct}
            totalFrames={opponent.data_quality.total_frames_analyzed}
            durationSeconds={opponent.data_quality.duration_seconds}
            fighter={opponent.fighter}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <GuardPanel data={opponent.guard_signature} fighter={opponent.fighter} />
            <MovementPanel data={opponent.movement_patterns} />
            <StrikingPanel data={opponent.striking_tendencies} />
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <VulnerabilityPanel
              data={opponent.exploitable_vulnerabilities}
              fighter={opponent.fighter}
            />
            <div className="space-y-4">
              <ThreatPanel data={opponent.threat_assessment} fighter={opponent.fighter} />
              <CampPanel
                recommendations={opponent.camp_recommendations}
                fighter={opponent.fighter}
              />
            </div>
          </div>
        </div>
      )}

      {/* Game Plan view */}
      {activeTab === "gameplan" && (
        <div className="p-4">
          <div className="max-w-4xl mx-auto">
            <GamePlanPanel data={gamePlan} />
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-dim px-6 py-3 mt-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <span className="text-dim font-mono text-2xs">
            TELEMETRY FIGHT LAB // MMA ANALYZER // v1.0.0
          </span>
          <div className="flex items-center gap-6">
            <span className="badge">MediaPipe</span>
            <span className="badge">Claude AI</span>
            <span className="badge">Apache Parquet</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
