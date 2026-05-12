"use client";

interface HeaderProps {
  fighter: string;
  opponent?: string;
  status?: string;
}

export default function Header({ fighter, opponent, status = "LIVE" }: HeaderProps) {
  return (
    <header className="border-b-2 border-white px-6 py-3 flex items-center justify-between bg-asphalt sticky top-0 z-50">
      <div className="flex items-center gap-6">
        <div>
          <span className="text-neon font-mono font-bold text-xs tracking-widest uppercase">
            TELEMETRY FIGHT LAB
          </span>
          <span className="text-dim font-mono text-xs ml-3">// MMA ANALYZER</span>
        </div>
        <div className="hidden md:flex items-center gap-2 border-l border-dim pl-6">
          <span className="text-ghost text-2xs uppercase tracking-wider">SUBJECT</span>
          <span className="text-white font-bold text-sm uppercase tracking-wide">{fighter}</span>
          {opponent && (
            <>
              <span className="text-dim mx-2">VS</span>
              <span className="text-ghost text-2xs uppercase tracking-wider">OPP</span>
              <span className="text-white font-bold text-sm uppercase tracking-wide">{opponent}</span>
            </>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-neon rounded-full animate-pulse" />
          <span className="text-neon text-2xs uppercase tracking-widest font-mono">{status}</span>
        </div>
        <span className="text-dim text-2xs font-mono">v1.0.0</span>
      </div>
    </header>
  );
}
