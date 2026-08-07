import React, { useMemo, useCallback, useRef, useState, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { useKnowledgeGraph } from '../../hooks/useKnowledgeGraph';
import type { GraphNodeDTO, GraphEdgeDTO } from '../../types/graph';
import { Loader2, AlertCircle } from 'lucide-react';

interface KnowledgeGraphProps {
  customerId: string;
  riskScore?: number;
}

export const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ customerId, riskScore }) => {
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set(['customer', 'company', 'ip', 'device', 'wallet', 'email', 'phone', 'merchant', 'country']));
  
  // Convert selectedTypes set to comma-separated string for API
  const entityTypesStr = Array.from(selectedTypes).join(',');
  
  const { data, isLoading, isError, error } = useKnowledgeGraph(customerId, 2, entityTypesStr);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  // Measure container dimensions on mount and resize
  useEffect(() => {
    const measure = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };
    measure();
    const resizeObserver = new ResizeObserver(measure);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    return () => resizeObserver.disconnect();
  }, []);

  // Map backend DTOs to ForceGraph expected node/link format
  const graphData = useMemo(() => {
    if (!data) return { nodes: [], links: [] };

    return {
      nodes: data.nodes.map((n: GraphNodeDTO) => ({
        id: n.id,
        name: n.label,
        type: n.type,
        val: n.type === 'CUSTOMER' ? 2 : 1,
        color: n.id === customerId && riskScore !== undefined ? getNodeColor(n.type, riskScore) : getNodeColor(n.type, n.metadata?.risk_score),
        ...n.metadata
      })),
      links: data.edges.map((e: GraphEdgeDTO) => ({
        source: e.source,
        target: e.target,
        label: e.relationship,
        value: e.weight || 1
      }))
    };
  }, [data]);

  const handleNodeClick = useCallback((node: any) => {
    console.log('Node clicked:', node);
    // Dynamic click-to-expand hop logic would go here
  }, []);

  const toggleType = (type: string) => {
    const newTypes = new Set(selectedTypes);
    if (newTypes.has(type)) {
      newTypes.delete(type);
    } else {
      newTypes.add(type);
    }
    setSelectedTypes(newTypes);
  };

  const filterOptions = ['customer', 'company', 'ip', 'device', 'wallet', 'email', 'phone', 'merchant', 'country'];

  return (
    <div className="flex flex-col gap-2">
      {/* A6: Filter Panel */}
      <div className="flex flex-wrap gap-1.5 p-1.5 bg-white rounded-lg border border-[#E4E7EC] shadow-sm items-center">
        <span className="text-brand-black text-[9px] font-bold tracking-wider mr-1 uppercase">Filters:</span>
        {filterOptions.map(type => (
          <button
            key={type}
            onClick={() => toggleType(type)}
            className={`px-1.5 py-0.5 text-[9px] font-bold tracking-wider uppercase rounded-full transition-colors ${
              selectedTypes.has(type) 
                ? 'bg-brand-red text-white border border-brand-red shadow-sm' 
                : 'bg-white text-[#6B7280] border border-[#E4E7EC] hover:bg-[#F9FAFB] hover:text-brand-black'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      <div
        ref={containerRef}
        className="relative w-full bg-white rounded-lg border border-[#E4E7EC] overflow-hidden shadow-sm"
        style={{ height: 300 }}
      >
        <div className="absolute top-2 left-2 z-10 bg-white/90 backdrop-blur-sm p-2 rounded-md border border-[#E4E7EC] shadow-sm">
          <h3 className="text-brand-black text-[10px] font-bold mb-1 uppercase tracking-wider">Risk Legend</h3>
          <div className="flex flex-col gap-1 text-[10px] text-[#6B7280]">
            <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#10b981]"></div> Low Risk (&lt;30)</div>
            <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]"></div> Medium Risk (30-70)</div>
            <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#ef4444]"></div> High Risk (&gt;70)</div>
            <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#94a3b8]"></div> Unknown</div>
          </div>
        </div>
        
        {isLoading && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-white/50 backdrop-blur-sm">
            <Loader2 className="w-8 h-8 text-brand-red animate-spin mb-4" />
            <span className="text-brand-black font-medium font-mono text-sm tracking-wider">MAPPING KNOWLEDGE GRAPH...</span>
          </div>
        )}

        {isError && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-white/90 border border-brand-red/20">
            <AlertCircle className="w-8 h-8 text-brand-red mb-4" />
            <span className="text-brand-black text-sm">{error instanceof Error ? error.message : 'Failed to load graph data'}</span>
          </div>
        )}

        {!isLoading && !isError && graphData.nodes.length === 0 && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-white/90">
            <span className="text-[#6B7280] text-sm">No graph connections found for these filters.</span>
          </div>
        )}

        {dimensions.width > 0 && dimensions.height > 0 && graphData.nodes.length > 0 && (
          <ForceGraph2D
            graphData={graphData}
            width={dimensions.width}
            height={dimensions.height}
            nodeLabel="name"
            nodeColor="color"
            nodeRelSize={6}
            linkColor={() => 'rgba(107, 114, 128, 0.4)'}
            linkWidth={1.5}
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            onNodeClick={handleNodeClick}
            backgroundColor="#FFFFFF"
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              const label = node.name;
              const fontSize = 12 / globalScale;
              ctx.font = `${fontSize}px Sans-Serif`;

              ctx.fillStyle = node.color;
              ctx.beginPath();
              ctx.arc(node.x, node.y, node.val * 2, 0, 2 * Math.PI, false);
              ctx.fill();

              if (node.color === '#ef4444') {
                 ctx.shadowColor = '#ef4444';
                 ctx.shadowBlur = 10;
              } else {
                 ctx.shadowBlur = 0;
              }

              // Only show labels when zoomed in or for high risk nodes to prevent clutter
              if (globalScale >= 1.5 || node.color === '#ef4444') {
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                
                // Add text background for readability over edges
                const textWidth = ctx.measureText(label).width;
                const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.4); 
                
                ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
                ctx.fillRect(
                  node.x - bckgDimensions[0] / 2, 
                  node.y + (node.val * 2) + fontSize - bckgDimensions[1] / 2, 
                  bckgDimensions[0], 
                  bckgDimensions[1]
                );

                ctx.fillStyle = '#111827';
                ctx.fillText(label, node.x, node.y + (node.val * 2) + fontSize);
              }
            }}
          />
        )}
      </div>
    </div>
  );
};

// Helper to determine node color based on type and risk score
function getNodeColor(_type: string, riskScore?: number): string {
  // A6: Risk-based coloring
  if (riskScore !== undefined) {
    if (riskScore >= 70) return '#ef4444'; // Red
    if (riskScore >= 30) return '#f59e0b'; // Yellow
    return '#10b981'; // Green
  }
  
  // Fallback if no risk score
  return '#94a3b8'; // Slate
}

