"use client";

interface CampPanelProps {
  recommendations: string[];
  fighter: string;
}

export default function CampPanel({ recommendations, fighter }: CampPanelProps) {
  return (
    <div className="panel p-4">
      <div className="section-header">CAMP DIRECTIVES // {fighter.toUpperCase()}</div>

      <div className="space-y-2">
        {recommendations.map((rec, i) => (
          <div key={i} className="flex items-start gap-3 border-b border-dim pb-2 last:border-0">
            <span className="text-neon font-mono font-bold text-xs shrink-0">
              {String(i + 1).padStart(2, "0")}.
            </span>
            <span className="text-white font-mono text-xs leading-relaxed">{rec}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
