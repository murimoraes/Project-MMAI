"use client";

interface HeaderProps {
  fighter: string;
  opponent?: string;
  status?: string;
}

export default function Header({ fighter, opponent, status = "LIVE" }: HeaderProps) {
  const isLive = status === "LIVE" || status === "ANÁLISE PRONTA";

  return (
    <header className="border-b border-cb-border bg-cb-surface/80 backdrop-blur-sm px-6 py-4 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-cb-blue flex items-center justify-center flex-shrink-0">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <circle cx="7" cy="7" r="6" stroke="white" strokeWidth="1.5" />
              <path d="M4 7h6M7 4v6" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <span className="text-cb-text font-semibold text-sm tracking-tight">
            Telemetry Fight Lab
          </span>
        </div>

        <div className="hidden md:flex items-center gap-3 border-l border-cb-border pl-6">
          <div className="flex items-center gap-1.5">
            <span className="text-cb-muted text-xs">Subject</span>
            <span className="text-cb-text font-semibold text-sm">{fighter}</span>
          </div>
          {opponent && (
            <>
              <span className="text-cb-dim text-xs">vs</span>
              <div className="flex items-center gap-1.5">
                <span className="text-cb-muted text-xs">Opponent</span>
                <span className="text-cb-text font-semibold text-sm">{opponent}</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${isLive ? "bg-cb-success animate-pulse" : "bg-cb-warning"}`}
          />
          <span className="text-cb-muted text-xs font-medium">{status}</span>
        </div>
        <span className="hidden sm:block text-cb-dim text-xs font-mono">v1.0.0</span>
      </div>
    </header>
  );
}
