"use client";

import { GamePlan } from "@/lib/types";

interface GamePlanPanelProps {
  data: GamePlan;
}

function EdgeBadge({ edge, fighters }: { edge: string; fighters: [string, string] }) {
  const isSubject = fighters.some(
    (f) => edge.toLowerCase().includes(f.toLowerCase().split(" ")[0])
  );
  const color = edge === "even" ? "#888888" : isSubject ? "#ccff00" : "#ff4444";
  return (
    <span className="font-mono font-bold text-xs uppercase" style={{ color }}>
      {edge.toUpperCase()}
    </span>
  );
}

export default function GamePlanPanel({ data }: GamePlanPanelProps) {
  const fighters = data.matchup.split(" vs ") as [string, string];

  return (
    <div className="panel-neon p-4 space-y-6">
      <div>
        <div className="section-header">TACTICAL GAME PLAN</div>
        <p className="text-ghost font-mono text-2xs">{data.matchup.toUpperCase()}</p>
      </div>

      {/* Advantage grid */}
      <div>
        <span className="label block mb-2">advantage analysis</span>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(data.advantage_analysis).map(([key, val]) => (
            <div key={key} className="border border-dim p-2">
              <span className="label block">{key.replace(/_/g, " ")}</span>
              <EdgeBadge edge={val} fighters={fighters} />
            </div>
          ))}
        </div>
      </div>

      {/* Round strategy */}
      <div>
        <span className="label block mb-2">round strategy</span>
        <div className="space-y-2">
          {Object.entries(data.round_strategy).map(([key, val]) => (
            <div key={key} className="flex gap-3">
              <span className="text-neon font-mono text-2xs uppercase whitespace-nowrap pt-0.5">
                {key.replace(/_/g, " ")}:
              </span>
              <span className="text-white font-mono text-xs leading-relaxed">{val}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Exploitation plan */}
      <div>
        <span className="label block mb-2">exploitation vectors</span>
        <div className="space-y-3">
          {data.exploitation_plan.map((item, i) => (
            <div key={i} className="border border-dim p-3">
              <div className="flex justify-between mb-2">
                <span className="text-2xs text-ghost uppercase font-mono">EXPLOIT-{String(i + 1).padStart(2, "0")}</span>
                <span className="text-2xs text-dim font-mono">{item.timing}</span>
              </div>
              <p className="text-red-300 font-mono text-xs mb-1">▲ {item.opponent_weakness}</p>
              <p className="text-neon font-mono text-xs mb-2">→ {item.our_tool}</p>
              <p className="text-ghost font-mono text-2xs">DRILL: {item.drill}</p>
            </div>
          ))}
        </div>
      </div>

      {/* KPIs */}
      <div>
        <span className="label block mb-2">key performance indicators</span>
        <div className="space-y-1">
          {data.key_performance_indicators.map((kpi, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="text-neon font-mono text-2xs mt-0.5">◆</span>
              <span className="text-white font-mono text-xs">{kpi}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Camp drills */}
      <div>
        <span className="label block mb-2">priority camp drills</span>
        <div className="space-y-2">
          {data.camp_priority_drills.map((drill, i) => (
            <div key={i} className="border-l-2 border-neon pl-3">
              <p className="text-neon font-mono text-xs font-bold">{drill.drill}</p>
              <p className="text-ghost font-mono text-2xs">{drill.purpose}</p>
              <p className="text-white font-mono text-2xs">{drill.volume}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
