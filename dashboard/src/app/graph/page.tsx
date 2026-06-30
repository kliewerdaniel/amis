"use client";

import { useEffect, useRef, useState } from "react";
import { getKnowledgeGraph } from "@/lib/data";
import * as d3 from "d3";

const TYPE_COLORS: Record<string, string> = {
  article: "#3B82F6",
  topic: "#10B981",
  entity: "#8B5CF6",
};

export default function GraphPage() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const data = getKnowledgeGraph();

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const width = svgRef.current.clientWidth;
    const height = Math.max(600, window.innerHeight - 200);

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("viewBox", [0, 0, width, height]);

    const links = data.links.map((l) => ({
      ...l,
      source: l.source,
      target: l.target,
    }));

    const nodes: any[] = data.nodes.map((n) => ({ ...n }));

    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance(60)
      )
      .force("charge", d3.forceManyBody().strength(-120))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide(20));

    const link = svg
      .append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#D1D5DB")
      .attr("stroke-width", (d) => Math.max(0.5, (d.weight || 1) * 1.5))
      .attr("stroke-opacity", 0.3);

    const node = svg
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", (d) => (d.type === "article" ? 6 : 4))
      .attr("fill", (d) => TYPE_COLORS[d.type] || "#9CA3AF")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .style("cursor", "pointer")
      .on("mouseenter", function (event: any, d: any) {
        setHovered(d.id);
        d3.select(this).attr("r", (d: any) => (d.type === "article" ? 10 : 7));
      })
      .on("mouseleave", function () {
        setHovered(null);
        d3.select(this).attr("r", (d: any) => (d.type === "article" ? 6 : 4));
      })
      .call(
        d3
          .drag<SVGCircleElement, any>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }) as any
      );

    const label = svg
      .append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text((d) => d.label)
      .attr("font-size", 8)
      .attr("dx", 8)
      .attr("dy", 3)
      .attr("fill", "#6B7280")
      .style("pointer-events", "none")
      .style("opacity", 0);

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);

      label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });

    // Show labels on center node or hover
    const showLabels = (ids: Set<string>) => {
      label.style("opacity", (d: any) => (ids.has(d.id) ? 1 : 0));
    };

    node.on("mouseenter", function (event: any, d: any) {
      const connected = new Set<string>();
      connected.add(d.id);
      links.forEach((l) => {
        const sid = typeof l.source === "object" ? (l.source as any).id : l.source;
        const tid = typeof l.target === "object" ? (l.target as any).id : l.target;
        if (sid === d.id) connected.add(tid);
        if (tid === d.id) connected.add(sid);
      });
      showLabels(connected);
    });

    node.on("mouseleave", () => {
      label.style("opacity", 0);
    });

    return () => {
      simulation.stop();
    };
  }, []);

  const hoveredNode = hovered ? data.nodes.find((n) => n.id === hovered) : null;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Knowledge Graph</h1>
      <p className="text-sm text-gray-500 mb-4">
        {data.nodes.length} nodes · {data.links.length} relationships
        {hoveredNode && (
          <span className="ml-4 text-blue-600 font-medium">
            Selected: {hoveredNode.label} ({hoveredNode.type})
          </span>
        )}
      </p>

      <div className="flex gap-4 mb-4 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-blue-500 inline-block" /> Article
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-green-500 inline-block" /> Topic
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-purple-500 inline-block" /> Entity
        </span>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-2">
        <svg ref={svgRef} className="w-full" style={{ height: "70vh", minHeight: 600 }} />
      </div>
    </div>
  );
}
