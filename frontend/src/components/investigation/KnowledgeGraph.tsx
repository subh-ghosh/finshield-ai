import React, { useMemo, useCallback, useRef, useState, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { useKnowledgeGraph } from '../../hooks/useKnowledgeGraph';
import type { GraphNodeDTO, GraphEdgeDTO } from '../../types/graph';
import { Loader2, AlertCircle } from 'lucide-react';

interface KnowledgeGraphProps {
  customerId: string;
}

export const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ customerId }) => {
  const { data, isLoading, isError, error } = useKnowledgeGraph(customerId, 2);
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
        color: getNodeColor(n.type, n.metadata?.risk_score),
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
  }, []);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center w-full bg-slate-900 rounded-lg border border-slate-700/50" style={{ height: 400 }}>
        <Loader2 className="w-8 h-8 text-brand-blue animate-spin mb-4" />
        <span className="text-slate-300 font-medium font-mono text-sm tracking-wider">MAPPING KNOWLEDGE GRAPH...</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center w-full bg-slate-900 rounded-lg border border-brand-red/20" style={{ height: 400 }}>
        <AlertCircle className="w-8 h-8 text-brand-red mb-4" />
        <span className="text-slate-300 text-sm">{error instanceof Error ? error.message : 'Failed to load graph data'}</span>
      </div>
    );
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center w-full bg-slate-900 rounded-lg border border-slate-700/50" style={{ height: 400 }}>
        <span className="text-slate-400 text-sm">No graph connections found for this entity.</span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="relative w-full bg-[#0a0f18] rounded-lg border border-slate-800 overflow-hidden shadow-2xl"
      style={{ height: 400 }}
    >
      <div className="absolute top-4 left-4 z-10 bg-slate-900/80 backdrop-blur-sm p-3 rounded-md border border-slate-700/50">
        <h3 className="text-slate-200 text-xs font-bold mb-2 uppercase tracking-wider">Network Legend</h3>
        <div className="flex flex-col gap-1.5 text-xs text-slate-400">
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#3b82f6]"></div> Customer</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#10b981]"></div> Account</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#8b5cf6]"></div> Device / IP</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#ef4444]"></div> High Risk Node</div>
        </div>
      </div>
      
      {dimensions.width > 0 && dimensions.height > 0 && (
        <ForceGraph2D
          graphData={graphData}
          width={dimensions.width}
          height={dimensions.height}
          nodeLabel="name"
          nodeColor="color"
          nodeRelSize={6}
          linkColor={() => 'rgba(148, 163, 184, 0.2)'}
          linkWidth={1.5}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          onNodeClick={handleNodeClick}
          backgroundColor="#0a0f18"
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

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fillText(label, node.x, node.y + (node.val * 2) + fontSize);
          }}
        />
      )}
    </div>
  );
};

// Helper to determine node color based on type and risk score
function getNodeColor(type: string, riskScore?: number): string {
  if (riskScore && riskScore >= 75) return '#ef4444'; // Red for high risk
  
  switch (type.toUpperCase()) {
    case 'CUSTOMER': return '#3b82f6'; // Blue
    case 'ACCOUNT': return '#10b981'; // Green
    case 'DEVICE':
    case 'IP': return '#8b5cf6'; // Purple
    case 'COMPANY': return '#f59e0b'; // Amber
    default: return '#94a3b8'; // Slate gray
  }
}

