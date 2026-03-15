import { useMemo } from 'react'
import type { Relationship } from '../../types/dashboard'
import type { DashboardData } from '../../types/agents'
import { forceLayout } from '../../layout/forceLayout'
import { loadConfig } from '../../config/loader'

interface Props {
  relationships: Relationship[]
  data?: DashboardData
}

const edgeTypeColors: Record<string, string> = {
  data: '#3b82f6',
  trigger: '#f59e0b',
  publish: '#10b981',
  extends: '#8b5cf6',
}

const defaultNodeColors = [
  '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444',
  '#ec4899', '#14b8a6', '#6366f1', '#f97316', '#64748b',
]

export function RelationshipMap({ relationships, data }: Props) {
  const config = loadConfig()

  const nodes = useMemo(() => {
    const nodeSet = new Set<string>()
    for (const r of relationships) {
      nodeSet.add(r.from)
      nodeSet.add(r.to)
    }
    const nodeIds = Array.from(nodeSet)

    const labels: Record<string, string> = {}
    const colors: Record<string, string> = {}

    const projectNames = new Map(data?.projects.map((p) => [p.id, p.name]) || [])

    nodeIds.forEach((id, i) => {
      labels[id] = projectNames.get(id) || id.split('-').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ')
      colors[id] = defaultNodeColors[i % defaultNodeColors.length]
    })

    return forceLayout(
      nodeIds,
      relationships.map((r) => ({ from: r.from, to: r.to })),
      labels,
      colors,
      config.centerNode
    )
  }, [relationships, data?.projects, config.centerNode])

  const nodeMap = new Map(nodes.map((n) => [n.id, n]))

  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900 p-4 overflow-x-auto">
      <svg
        viewBox="0 0 950 480"
        className="w-full min-w-[600px]"
        style={{ maxHeight: 420 }}
      >
        {relationships.map((rel, i) => {
          const from = nodeMap.get(rel.from)
          const to = nodeMap.get(rel.to)
          if (!from || !to) return null
          const color = edgeTypeColors[rel.type] || '#6b7280'
          const midX = (from.x + to.x) / 2
          const midY = (from.y + to.y) / 2
          return (
            <g key={i}>
              <line
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke={color}
                strokeWidth={1.5}
                strokeOpacity={0.5}
              />
              <text
                x={midX}
                y={midY - 6}
                fill={color}
                fontSize={9}
                textAnchor="middle"
                fontFamily="monospace"
              >
                {rel.label}
              </text>
            </g>
          )
        })}

        {nodes.map((node) => {
          const isCenter = node.isCenter
          const w = isCenter ? 140 : 110
          const h = isCenter ? 44 : 36
          return (
            <g key={node.id}>
              {isCenter && (
                <rect
                  x={node.x - w / 2 - 3}
                  y={node.y - h / 2 - 3}
                  width={w + 6}
                  height={h + 6}
                  rx={12}
                  fill="none"
                  stroke={node.color}
                  strokeWidth={1}
                  strokeOpacity={0.3}
                />
              )}
              <rect
                x={node.x - w / 2}
                y={node.y - h / 2}
                width={w}
                height={h}
                rx={8}
                fill="#111827"
                stroke={node.color}
                strokeWidth={isCenter ? 2.5 : 1.5}
              />
              <text
                x={node.x}
                y={node.y + 4}
                fill="white"
                fontSize={isCenter ? 12 : 10}
                textAnchor="middle"
                fontFamily="sans-serif"
                fontWeight={isCenter ? 700 : 600}
              >
                {node.label}
              </text>
            </g>
          )
        })}

        <g transform="translate(10, 460)">
          {Object.entries(edgeTypeColors).map(([type, color], i) => (
            <g key={type} transform={`translate(${i * 110}, 0)`}>
              <line x1={0} y1={6} x2={20} y2={6} stroke={color} strokeWidth={2} />
              <text x={25} y={10} fill="#9ca3af" fontSize={10}>
                {type}
              </text>
            </g>
          ))}
        </g>
      </svg>
    </div>
  )
}
