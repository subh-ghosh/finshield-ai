import { Network } from 'lucide-react';

export function ReasoningTimeline({ steps }: { steps: string[] }) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="border border-[#E4E7EC] p-5 bg-white">
      <h3 className="fs-section-label mb-5 flex items-center gap-2">
        <Network className="h-3.5 w-3.5" /> Reasoning Timeline
      </h3>
      <div className="relative pl-3 space-y-5 before:absolute before:inset-y-0 before:left-[11px] before:w-[2px] before:bg-[#F0F1F3]">
        {steps.map((step, i) => (
          <div key={i} className="relative">
            <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-white border-2 border-[#10B981] flex items-center justify-center text-[10px] font-bold text-[#10B981] z-10 shadow-sm">
              {i + 1}
            </div>
            <div className="text-[12px] text-brand-black leading-relaxed ml-3 pt-0.5">
              {step}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

