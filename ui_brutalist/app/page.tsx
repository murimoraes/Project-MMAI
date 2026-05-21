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

const TABS: { id: Tab; label: string }[] = [
  { id: "subject", label: "Subject" },
  { id: "opponent", label: "Opponent" },
  { id: "gameplan", label: "Game Plan" },
];

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

  const activeFighter = activeTab === "opponent" ? opponent : subject;

  return (
    <div className="min-h-screen bg-cb-bg">
      <Header
        fighter={subject.fighter}
        opponent={opponent.fighter}
        status={loaded ? "ANÁLISE PRONTA" : "CARREGANDO..."}
      />

      {/* Tab navigation */}
      <div className="border-b border-cb-border bg-cb-surface/60 backdrop-blur-sm px-6">
        <div className="flex items-center gap-1">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            const label =
              tab.id === "subject"
                ? subject.fighter
                : tab.id === "opponent"
                ? opponent.fighter
                : tab.label;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors duration-150 -mb-px ${
                  isActive
                    ? "border-cb-blue text-cb-text"
                    : "border-transparent text-cb-muted hover:text-cb-text hover:border-cb-border-strong"
                }`}
              >
                {label}
              </button>
            );
          })}

          <div className="flex-1 flex items-center justify-end pb-px">
            <span className="font-mono text-2xs text-cb-dim" suppressHydrationWarning>
              {new Date().toISOString().replace("T", " ").slice(0, 19)} UTC
            </span>
          </div>
        </div>
      </div>

      {/* Fighter views */}
      {(activeTab === "subject" || activeTab === "opponent") && (
        <div className="p-6 space-y-4 max-w-[1400px] mx-auto">
          <DataQualityBar
            detectionRate={activeFighter.data_quality.detection_rate_pct}
            totalFrames={activeFighter.data_quality.total_frames_analyzed}
            durationSeconds={activeFighter.data_quality.duration_seconds}
            fighter={activeFighter.fighter}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <GuardPanel data={activeFighter.guard_signature} fighter={activeFighter.fighter} />
            <MovementPanel data={activeFighter.movement_patterns} />
            <StrikingPanel data={activeFighter.striking_tendencies} />
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <VulnerabilityPanel
              data={activeFighter.exploitable_vulnerabilities}
              fighter={activeFighter.fighter}
            />
            <div className="space-y-4">
              <ThreatPanel data={activeFighter.threat_assessment} fighter={activeFighter.fighter} />
              <CampPanel
                recommendations={activeFighter.camp_recommendations}
                fighter={activeFighter.fighter}
              />
            </div>
          </div>
        </div>
      )}

      {/* Game plan view */}
      {activeTab === "gameplan" && (
        <div className="p-6 max-w-[900px] mx-auto">
          <GamePlanPanel data={gamePlan} />
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-cb-border px-6 py-4 mt-8">
        <div className="flex flex-wrap items-center justify-between gap-4 max-w-[1400px] mx-auto">
          <span className="text-cb-dim text-xs">
            Telemetry Fight Lab · MMA Analyzer · v1.0.0
          </span>
          <div className="flex items-center gap-3">
            {["MediaPipe", "Claude AI", "Apache Parquet"].map((tag) => (
              <span key={tag} className="badge-neutral">{tag}</span>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
