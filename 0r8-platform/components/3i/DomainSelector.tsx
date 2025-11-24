"use client";

/**
 * Domain Selector Component
 * Allows users to select from the 8 life domains
 */

import { use3iStore } from "@/lib/stores/use-3i-store";
import { DOMAINS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { DomainId } from "@/types";

export function DomainSelector() {
  const { domain, setDomain } = use3iStore();

  const domainList = Object.values(DOMAINS);

  return (
    <div className="bg-subtle rounded-xl border border-white/5 p-4">
      <h3 className="text-sm font-medium text-white/70 mb-3">Life Domain</h3>

      <div className="grid grid-cols-4 gap-2">
        {domainList.map((d) => (
          <button
            key={d.id}
            onClick={() => setDomain(domain === d.id ? null : (d.id as DomainId))}
            className={cn(
              "flex flex-col items-center justify-center p-3 rounded-lg transition-all",
              domain === d.id
                ? "bg-white/10 border border-white/20"
                : "bg-white/5 border border-transparent hover:bg-white/10"
            )}
            title={d.description}
          >
            <span className="text-xl mb-1">{d.icon}</span>
            <span
              className={cn(
                "text-xs",
                domain === d.id ? "text-white" : "text-white/50"
              )}
            >
              {d.name}
            </span>
          </button>
        ))}
      </div>

      {domain && (
        <p className="text-xs text-white/40 mt-3 text-center">
          {DOMAINS[domain].description}
        </p>
      )}
    </div>
  );
}
