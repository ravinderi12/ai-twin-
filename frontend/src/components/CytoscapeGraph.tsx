import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Filter, Layers } from 'lucide-react';

interface CytoscapeGraphProps {
  graphData: {
    nodes: any[];
    edges: any[];
  };
  onSelectNode?: (nodeData: any) => void;
  selectedNodeId?: string | null;
  highlightPathNodes?: string[];
}

export const CytoscapeGraph: React.FC<CytoscapeGraphProps> = ({
  graphData,
  onSelectNode,
  selectedNodeId,
  highlightPathNodes
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [layoutName, setLayoutName] = useState<'cose' | 'concentric' | 'circle' | 'breadthfirst'>('cose');
  const [filterSubnet, setFilterSubnet] = useState<string>('ALL');

  // Collect available subnets
  const subnets = Array.from(
    new Set(
      (graphData?.nodes || [])
        .map((n) => n.data?.subnet)
        .filter((s) => Boolean(s) && s !== 'Unknown')
    )
  );

  useEffect(() => {
    if (!containerRef.current || !graphData || !graphData.nodes) return;

    // Filter nodes by subnet if selected
    let filteredNodes = graphData.nodes;
    if (filterSubnet !== 'ALL') {
      filteredNodes = graphData.nodes.filter(
        (n) => n.data?.subnet === filterSubnet || n.data?.is_perimeter
      );
    }
    const nodeIds = new Set(filteredNodes.map((n) => n.data.id));
    const filteredEdges = (graphData.edges || []).filter(
      (e) => nodeIds.has(e.data.source) && nodeIds.has(e.data.target)
    );

    const cy = cytoscape({
      container: containerRef.current,
      elements: [...filteredNodes, ...filteredEdges],
      style: ([
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#f8fafc',
            'font-size': '11px',
            'font-family': 'Inter, sans-serif',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'background-color': '#1e293b',
            'border-width': 2,
            'border-color': '#06b6d4',
            'width': 44,
            'height': 44,
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': 0.2
          }
        },
        // Coloration by risk score
        {
          selector: 'node[risk_score >= 80]',
          style: {
            'border-color': '#ef4444',
            'background-color': '#7f1d1d',
            'border-width': 3
          }
        },
        {
          selector: 'node[risk_score >= 50][risk_score < 80]',
          style: {
            'border-color': '#f59e0b',
            'background-color': '#78350f',
            'border-width': 2.5
          }
        },
        {
          selector: 'node[risk_score < 50]',
          style: {
            'border-color': '#06b6d4',
            'background-color': '#083344',
            'border-width': 2
          }
        },
        // Node Shapes by Asset Type
        {
          selector: 'node[asset_type = "gateway"]',
          style: {
            'shape': 'diamond',
            'width': 52,
            'height': 52,
            'border-color': '#38bdf8'
          }
        },
        {
          selector: 'node[asset_type = "database"]',
          style: {
            'shape': 'octagon',
            'width': 48,
            'height': 48,
            'border-color': '#ef4444'
          }
        },
        {
          selector: 'node[asset_type = "workstation"]',
          style: {
            'shape': 'round-rectangle',
            'width': 44,
            'height': 38,
            'border-color': '#10b981'
          }
        },
        // Choke point bottleneck nodes
        {
          selector: 'node[?is_choke_point]',
          style: {
            'border-style': 'double',
            'border-width': 5,
            'border-color': '#ec4899'
          }
        },
        // Selected node highlight
        {
          selector: 'node:selected',
          style: {
            'border-color': '#ffffff',
            'border-width': 4,
            'shadow-blur': 15,
            'shadow-color': '#38bdf8',
            'shadow-opacity': 0.8
          }
        },
        // Node in simulated attack path
        {
          selector: 'node[?is_in_attack_path]',
          style: {
            'border-color': '#f43f5e',
            'border-width': 4,
            'shadow-blur': 12,
            'shadow-color': '#f43f5e',
            'shadow-opacity': 0.9
          }
        },
        // Default Edge Styling
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#334155',
            'target-arrow-color': '#334155',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '9px',
            'color': '#94a3b8',
            'text-rotation': 'autorotate',
            'text-background-opacity': 0.8,
            'text-background-color': '#0b0f19',
            'text-background-padding': '2px',
            'text-background-shape': 'roundrectangle'
          }
        },
        // Inferred edge styling
        {
          selector: 'edge[?is_inferred]',
          style: {
            'line-style': 'dashed',
            'line-color': '#64748b'
          }
        },
        // Simulated Attack Path Edge
        {
          selector: 'edge[?is_attack_path]',
          style: {
            'width': 4,
            'line-color': '#ef4444',
            'target-arrow-color': '#ef4444',
            'target-arrow-shape': 'triangle',
            'line-style': 'dashed',
            'shadow-blur': 10,
            'shadow-color': '#ef4444',
            'shadow-opacity': 0.8,
            'z-index': 99
          }
        }
      ] as any),
      layout: {
        name: layoutName,
        animate: true,
        animationDuration: 500,
        padding: 50
      }
    });

    // Handle node selection
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      if (onSelectNode) {
        onSelectNode(node.data());
      }
    });

    // Handle canvas background tap
    cy.on('tap', (evt) => {
      if (evt.target === cy && onSelectNode) {
        onSelectNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [graphData, layoutName, filterSubnet]);

  // Apply layout change
  const handleLayoutChange = (name: any) => {
    setLayoutName(name);
    if (cyRef.current) {
      cyRef.current.layout({ name, animate: true, animationDuration: 400 }).run();
    }
  };

  const handleZoomIn = () => {
    if (cyRef.current) cyRef.current.zoom(cyRef.current.zoom() * 1.25);
  };

  const handleZoomOut = () => {
    if (cyRef.current) cyRef.current.zoom(cyRef.current.zoom() * 0.8);
  };

  const handleFit = () => {
    if (cyRef.current) cyRef.current.fit(undefined, 50);
  };

  const handleReset = () => {
    if (cyRef.current) {
      cyRef.current.reset();
      cyRef.current.fit(undefined, 50);
    }
  };

  return (
    <div className="relative w-full h-full bg-[#070b14] rounded-xl border border-soc-border overflow-hidden">
      {/* Top Floating Controls Bar */}
      <div className="absolute top-3 left-3 z-10 flex flex-wrap items-center gap-2 bg-slate-900/90 backdrop-blur-md p-1.5 rounded-lg border border-slate-800 shadow-lg text-xs">
        {/* Layout Selector */}
        <div className="flex items-center space-x-1 border-r border-slate-700 pr-2">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <select
            value={layoutName}
            onChange={(e) => handleLayoutChange(e.target.value)}
            className="bg-slate-800 text-slate-200 border-none rounded px-2 py-1 text-xs focus:ring-1 focus:ring-cyan-500 outline-none"
          >
            <option value="cose">Force-Directed (COSE)</option>
            <option value="concentric">Concentric Rings</option>
            <option value="circle">Circular Topology</option>
            <option value="breadthfirst">Breadth-First Hierarchy</option>
          </select>
        </div>

        {/* Subnet Filter */}
        <div className="flex items-center space-x-1 border-r border-slate-700 pr-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={filterSubnet}
            onChange={(e) => setFilterSubnet(e.target.value)}
            className="bg-slate-800 text-slate-200 border-none rounded px-2 py-1 text-xs focus:ring-1 focus:ring-cyan-500 outline-none"
          >
            <option value="ALL">All Subnets ({graphData?.nodes?.length || 0})</option>
            {subnets.map((sub: any) => (
              <option key={sub} value={sub}>
                Subnet {sub}
              </option>
            ))}
          </select>
        </div>

        {/* Zoom & Fit Actions */}
        <div className="flex items-center space-x-1">
          <button
            onClick={handleZoomIn}
            className="p-1 hover:bg-slate-800 text-slate-300 rounded"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-1 hover:bg-slate-800 text-slate-300 rounded"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleFit}
            className="p-1 hover:bg-slate-800 text-slate-300 rounded"
            title="Fit to Screen"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="p-1 hover:bg-slate-800 text-slate-300 rounded"
            title="Reset View"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Legend Card Bottom Left */}
      <div className="absolute bottom-3 left-3 z-10 bg-slate-900/90 backdrop-blur-md p-2.5 rounded-lg border border-slate-800 shadow-md text-[11px] space-y-1.5">
        <div className="font-semibold text-slate-300">Topology Legend</div>
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
            <span className="text-slate-400">Risk &ge; 80</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span className="text-slate-400">Risk &ge; 50</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>
            <span className="text-slate-400">Low Risk</span>
          </span>
        </div>
        <div className="flex items-center space-x-3 text-[10px] text-slate-400">
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 border-2 border-pink-500 rounded-sm"></span>
            <span>Choke Point</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-3 border-b-2 border-red-500 border-dashed"></span>
            <span>Attack Path</span>
          </span>
        </div>
      </div>

      {/* Cytoscape Canvas Container */}
      <div ref={containerRef} className="w-full h-full" />
    </div>
  );
};
