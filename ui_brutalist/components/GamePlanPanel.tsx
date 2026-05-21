"use client";

import { GamePlan } from "@/lib/types";

interface GamePlanPanelProps {
  data: GamePlan;
}

function EdgeBadge({ edge, fighters }: { edge: string; fighters: [string, string] }) {
  const isSubject = fighters.some(
    (f) => edge.toLowerCase().includes(f.toLowerCase().split(" ")[0])
  );
  if (edge === "even") return <span className="badge-neutral">Even</span>;
  return (
    <span className={isSubject ? "badge-success" : "badge-danger"}>
      {edge}
    </span>
  );
}

const EDGE_LABELS: Record<string, string> = {
  striking_edge: "Striking",
  grappling_edge: "Grappling",
  footwork_edge: "Footwork",
  overall_edge: "Overall",
};

export default function GamePlanPanel({ data }: GamePlanPanelProps) {
  const fighters = data.matchup.split(" vs ") as [string, string];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="card p-5">
        <p className="section-title mb-1">Tactical Game Plan</p>
        <p className="text-xl font-bold text-cb-text">{data.matchup}</p>
        <p className="text-xs text-cb-muted mt-1">
          Generated {new Date(data.generated_at).toLocaleString()}
        </p>
      </div>

      {/* Advantage analysis */}
      <div className="card p-5">
        <p className="section-title mb-3">Advantage Analysis</p>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(data.advantage_analysis).map(([key, val]) => (
            <div key={key} className="rounded-cb-sm bg-cb-elevated border border-cb-border p-3">
              <p className="data-label mb-1.5">{EDGE_LABELS[key] ?? key.replace(/_/g, " ")}</p>
              <EdgeBadge edge={val} fighters={fighters} />
            </div>
          ))}
        </div>
      </div>

      {/* Round strategy */}
      <div className="card p-5">
        <p className="section-title mb-3">Round Strategy</p>
        <div className="space-y-3">
          {Object.entries(data.round_strategy).map(([key, val]) => (
            <div key={key} className="flex gap-3">
              <span className="badge-blue flex-shrink-0 self-start mt-0.5">
                {key.replace(/_/g, " ").replace("rounds", "Rds").replace("round", "Rd")}
              </span>
              <p className="text-sm text-cb-text leading-relaxed">{val}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Exploitation plan */}
      <div className="card p-5">
        <p className="section-title mb-3">Exploitation Vectors</p>
        <div className="space-y-3">
          {data.exploitation_plan.map((item, i) => (
            <div key={i} className="rounded-cb-sm border border-cb-border bg-cb-elevated p-4">
              <div className="flex items-center justify-between mb-2.5">
                <span className="font-mono text-2xs text-cb-dim uppercase tracking-widest">
                  Exploit-{String(i + 1).padStart(2, "0")}
                </span>
                <span className="badge-neutral">{item.timing}</span>
              </div>
              <p className="text-sm text-cb-danger mb-1.5">↑ {item.opponent_weakness}</p>
              <p className="text-sm text-cb-blue mb-3">→ {item.our_tool}</p>
              <div className="pt-2.5 border-t border-cb-border">
                <p className="data-label mb-1">Camp drill</p>
                <p className="text-xs text-cb-muted">{item.drill}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* KPIs */}
      <div className="card p-5">
        <p className="section-title mb-3">Key Performance Indicators</p>
        <div className="space-y-2">
          {data.key_performance_indicators.map((kpi, i) => (
            <div key={i} className="flex items-start gap-2.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cb-blue flex-shrink-0 mt-2" />
              <span className="text-sm text-cb-text leading-relaxed">{kpi}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Priority camp drills */}
      <div className="card p-5">
        <p className="section-title mb-3">Priority Camp Drills</p>
        <div className="space-y-3">
          {data.camp_priority_drills.map((drill, i) => (
            <div key={i} className="rounded-cb-sm border-l-2 border-cb-blue pl-4 py-2">
              <p className="text-sm font-semibold text-cb-text mb-0.5">{drill.drill}</p>
              <p className="text-xs text-cb-muted mb-1">{drill.purpose}</p>
              <span className="badge-blue">{drill.volume}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
