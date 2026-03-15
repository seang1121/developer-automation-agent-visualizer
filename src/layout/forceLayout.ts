interface Node {
  id: string
  x: number
  y: number
  label: string
  color: string
  isCenter?: boolean
}

interface Edge {
  from: string
  to: string
}

export function forceLayout(
  nodeIds: string[],
  edges: Edge[],
  labels: Record<string, string>,
  colors: Record<string, string>,
  centerId?: string,
  width = 950,
  height = 480
): Node[] {
  if (nodeIds.length === 0) return []

  const cx = width / 2
  const cy = height / 2

  if (nodeIds.length <= 2) {
    return nodeIds.map((id, i) => ({
      id,
      x: cx + (i - (nodeIds.length - 1) / 2) * 200,
      y: cy,
      label: labels[id] || id,
      color: colors[id] || '#6b7280',
      isCenter: id === centerId,
    }))
  }

  const center =
    centerId && nodeIds.includes(centerId)
      ? centerId
      : findMostConnected(nodeIds, edges)

  const nodes: Node[] = nodeIds.map((id) => {
    if (id === center) {
      return { id, x: cx, y: cy, label: labels[id] || id, color: colors[id] || '#f97316', isCenter: true }
    }
    const others = nodeIds.filter((n) => n !== center)
    const idx = others.indexOf(id)
    const angle = (2 * Math.PI * idx) / others.length - Math.PI / 2
    const radius = Math.min(width, height) * 0.35
    return {
      id,
      x: cx + radius * Math.cos(angle) + (Math.random() - 0.5) * 20,
      y: cy + radius * Math.sin(angle) + (Math.random() - 0.5) * 20,
      label: labels[id] || id,
      color: colors[id] || '#6b7280',
      isCenter: false,
    }
  })

  const padding = 70
  for (let iter = 0; iter < 100; iter++) {
    const forces = nodes.map(() => ({ fx: 0, fy: 0 }))

    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x
        const dy = nodes[j].y - nodes[i].y
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1)
        const repulsion = 8000 / (dist * dist)
        const fx = (dx / dist) * repulsion
        const fy = (dy / dist) * repulsion
        forces[i].fx -= fx
        forces[i].fy -= fy
        forces[j].fx += fx
        forces[j].fy += fy
      }
    }

    const nodeMap = new Map(nodes.map((n, i) => [n.id, i]))
    for (const edge of edges) {
      const iA = nodeMap.get(edge.from)
      const iB = nodeMap.get(edge.to)
      if (iA == null || iB == null) continue
      const dx = nodes[iB].x - nodes[iA].x
      const dy = nodes[iB].y - nodes[iA].y
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1)
      const spring = (dist - 180) * 0.01
      const fx = (dx / dist) * spring
      const fy = (dy / dist) * spring
      forces[iA].fx += fx
      forces[iA].fy += fy
      forces[iB].fx -= fx
      forces[iB].fy -= fy
    }

    const damping = 0.85 - iter * 0.005
    for (let i = 0; i < nodes.length; i++) {
      if (nodes[i].isCenter) continue
      nodes[i].x += forces[i].fx * damping
      nodes[i].y += forces[i].fy * damping
      nodes[i].x = Math.max(padding, Math.min(width - padding, nodes[i].x))
      nodes[i].y = Math.max(padding, Math.min(height - padding, nodes[i].y))
    }
  }

  return nodes
}

function findMostConnected(nodeIds: string[], edges: Edge[]): string {
  const counts = new Map<string, number>()
  for (const id of nodeIds) counts.set(id, 0)
  for (const e of edges) {
    if (counts.has(e.from)) counts.set(e.from, (counts.get(e.from) || 0) + 1)
    if (counts.has(e.to)) counts.set(e.to, (counts.get(e.to) || 0) + 1)
  }
  let best = nodeIds[0]
  let max = 0
  for (const [id, c] of counts) {
    if (c > max) { max = c; best = id }
  }
  return best
}
