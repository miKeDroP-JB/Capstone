"use client";

/**
 * Demigod Selector Component
 * Allows users to select from the 7 demigods
 */

import { use3iStore } from "@/lib/stores/use-3i-store";
import { DEMIGODS } from "@/lib/constants";
import { cn, getPillarColor } from "@/lib/utils";
import type { DemigodId, Pillar } from "@/types";

export function DemigodSelector() {
  const { demigod, setDemigod } = use3iStore();

  const demigodsByPillar: Record<Pillar, typeof DEMIGODS[DemigodId][]> = {
    nous: [DEMIGODS.athena, DEMIGODS.mercury, DEMIGODS.hephaestus],
    anima: [DEMIGODS.apollo, DEMIGODS.artemis],
    holos: [DEMIGODS.hermes, DEMIGODS.ares],
  };

  const pillarLabels: Record<Pillar, string> = {
    nous: "☿ NOUS — The Mind",
    anima: "🜍 ANIMA — The Soul",
    holos: "🜔 HOLOS — The Whole",
  };

  return (
    <div className="bg-subtle rounded-xl border border-white/5 p-4">
      <h3 className="text-sm font-medium text-white/70 mb-4">Demigod</h3>

      <div className="space-y-4">
        {(Object.keys(demigodsByPillar) as Pillar[]).map((pillar) => (
          <div key={pillar}>
            <div
              className="text-xs font-medium mb-2"
              style={{ color: getPillarColor(pillar) }}
            >
              {pillarLabels[pillar]}
            </div>

            <div className="flex flex-wrap gap-2">
              {demigodsByPillar[pillar].map((d) => (
                <button
                  key={d.id}
                  onClick={() =>
                    setDemigod(demigod === d.id ? null : (d.id as DemigodId))
                  }
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-sm",
                    demigod === d.id
                      ? "bg-white/10 border border-white/20"
                      : "bg-white/5 border border-transparent hover:bg-white/10"
                  )}
                  title={d.specialty}
                  style={{
                    borderColor:
                      demigod === d.id ? getPillarColor(d.pillar) : undefined,
                  }}
                >
                  <span>{d.symbol}</span>
                  <span
                    className={cn(
                      demigod === d.id ? "text-white" : "text-white/60"
                    )}
                  >
                    {d.name}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {demigod && (
        <div className="mt-4 p-3 bg-white/5 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">{DEMIGODS[demigod].symbol}</span>
            <div>
              <div className="font-medium text-sm">{DEMIGODS[demigod].name}</div>
              <div className="text-xs text-white/40">
                {DEMIGODS[demigod].domain}
              </div>
            </div>
          </div>
          <p className="text-xs text-white/60">{DEMIGODS[demigod].specialty}</p>
        </div>
      )}
    </div>
  );
}
