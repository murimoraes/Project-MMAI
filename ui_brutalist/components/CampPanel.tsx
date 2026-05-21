"use client";

interface CampPanelProps {
  recommendations: string[];
  fighter: string;
}

export default function CampPanel({ recommendations, fighter }: CampPanelProps) {
  return (
    <div className="card p-5">
      <div className="mb-4">
        <p className="section-title mb-0.5">Camp Directives</p>
        <p className="text-xs text-cb-muted">{fighter}</p>
      </div>

      <div className="space-y-0">
        {recommendations.map((rec, i) => (
          <div key={i} className="flex items-start gap-3 py-2.5 border-b border-cb-border last:border-0">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-cb-blue-muted border border-cb-blue/30 flex items-center justify-center">
              <span className="text-cb-blue font-mono font-bold" style={{ fontSize: "0.6rem" }}>
                {i + 1}
              </span>
            </span>
            <span className="text-sm text-cb-text leading-relaxed">{rec}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
