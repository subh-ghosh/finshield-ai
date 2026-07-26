export function TableSkeleton() {
  return (
    <div className="animate-pulse">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="flex border-b border-[#F0F1F3] py-4 px-6 gap-6">
          <div className="h-4 bg-gray-200 w-24"></div>
          <div className="h-4 bg-gray-200 w-48"></div>
          <div className="h-4 bg-gray-200 w-16"></div>
          <div className="h-4 bg-gray-200 w-20"></div>
          <div className="h-4 bg-gray-200 w-24"></div>
          <div className="h-4 bg-gray-200 w-full"></div>
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="fs-stat-card animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="h-3 bg-gray-200 w-24"></div>
        <div className="w-8 h-8 rounded-full bg-gray-100"></div>
      </div>
      <div className="h-8 bg-gray-200 w-16 mb-3"></div>
      <div className="pt-3 border-t border-[#F0F1F3]">
        <div className="h-2 bg-gray-200 w-32"></div>
      </div>
    </div>
  );
}

