export function RiskBadge({ score }: { score: number }) {
  if (score >= 90) return <span className="fs-badge fs-badge-critical">CRITICAL ({score})</span>;
  if (score >= 75) return <span className="fs-badge fs-badge-high">HIGH ({score})</span>;
  if (score >= 50) return <span className="fs-badge fs-badge-medium">MEDIUM ({score})</span>;
  return <span className="fs-badge fs-badge-low">LOW ({score})</span>;
}

export function StatusBadge({ status }: { status: string }) {
  let style = 'bg-[#F9FAFB] text-[#6B7280] border-[#E5E7EB]';
  
  if (status === 'Open') style = 'bg-[#FEF2F2] text-brand-red border-[#FECACA]';
  else if (status === 'In Progress') style = 'bg-[#FEF9C3] text-[#92400E] border-[#FDE68A]';
  else if (status === 'Pending Review') style = 'bg-[#F0FDF4] text-[#166534] border-[#BBF7D0]';

  return (
    <span className={`inline-flex items-center text-[10px] font-semibold px-2 py-0.5 border ${style}`}>
      {status}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: string }) {
  let color = 'text-[#6B7280]';
  if (priority === 'Critical') color = 'text-brand-red';
  else if (priority === 'High') color = 'text-[#F59E0B]';

  return (
    <span className={`text-[10px] font-bold px-2 py-0.5 ${color}`}>
      {priority}
    </span>
  );
}



