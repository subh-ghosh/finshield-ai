import React, { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

export function KnowledgeGraph({ customerId }: { customerId: string }) {
  const fgRef = useRef<any>();
  const [data, setData] = useState({ nodes: [], links: [] });
  const [width, setWidth] = useState(800);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    
    fetch(`http://localhost:8000/api/v1/graph/${customerId}`)
      .then(res => {
        if (!res.ok) throw new Error('Graph data not available');
        return res.json();
      })
      .then(json => {
        if (isMounted) {
          setData(json);
          setLoading(false);
        }
      })
      .catch(err => {
        if (isMounted) {
          console.error(err);
          setError('Failed to load knowledge graph.');
          setLoading(false);
        }
      });
      
    return () => { isMounted = false; };
  }, [customerId]);

  useEffect(() => {
    if (containerRef.current) {
      setWidth(containerRef.current.clientWidth);
      const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
          setWidth(entry.contentRect.width);
        }
      });
      resizeObserver.observe(containerRef.current);
      return () => resizeObserver.disconnect();
    }
  }, []);

  useEffect(() => {
    // Force graph to center after data load
    if (!loading && data.nodes.length > 0) {
      setTimeout(() => {
        if (fgRef.current) {
          fgRef.current.d3Force('charge').strength(-400);
          fgRef.current.zoomToFit(400, 50);
        }
      }, 500);
    }
  }, [data, loading]);

  return (
    <div className="w-full h-full flex flex-col bg-white border border-[#E4E7EC] shadow-sm mt-6">
      <div className="px-4 py-3 border-b border-[#E4E7EC] flex items-center justify-between bg-[#F9FAFB]">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
          <h3 className="text-[13px] font-bold text-brand-black uppercase tracking-wider">Living Knowledge Graph</h3>
        </div>
        <div className="text-[11px] text-[#6B7280]">
          Showing 2-hop network for {customerId}
        </div>
      </div>
      <div className="flex-1 relative" style={{ height: '400px' }} ref={containerRef}>
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/50 z-10 text-[11px] font-bold text-brand-gray tracking-wider uppercase">
            Loading Knowledge Graph...
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/50 z-10 text-[11px] font-bold text-brand-red tracking-wider uppercase">
            {error}
          </div>
        )}
        {!loading && !error && data.nodes.length > 0 && (
          <ForceGraph2D
          ref={fgRef}
          width={width}
          height={400}
          graphData={data}
          nodeLabel="name"
          nodeColor={(node: any) => {
            switch(node.group) {
              case 'customer': return '#E1000F'; // Red
              case 'company': return '#1F2937'; // Dark Gray
              case 'person': return '#3B82F6'; // Blue
              case 'ip': return '#10B981'; // Green
              case 'phone': return '#F59E0B'; // Yellow
              default: return '#9CA3AF';
            }
          }}
          nodeRelSize={6}
          linkColor={() => '#E4E7EC'}
          linkWidth={2}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          onNodeClick={(node: any) => {
            // Center on clicked node
            if (fgRef.current) {
              fgRef.current.centerAt(node.x, node.y, 1000);
              fgRef.current.zoom(2, 2000);
            }
          }}
        />
        )}
        
        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur p-3 border border-[#E4E7EC] shadow-sm text-[10px] uppercase font-bold tracking-wider space-y-2 pointer-events-none">
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#E1000F]" /> Target Customer</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#1F2937]" /> Connected Entity</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#3B82F6]" /> Director / UBO</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#10B981]" /> Digital Fingerprint</div>
        </div>
      </div>
    </div>
  );
}
