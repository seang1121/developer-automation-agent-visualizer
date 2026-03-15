import type { DaavConfig } from '../types/config'

let cachedConfig: DaavConfig | null = null

export function loadConfig(): DaavConfig {
  if (cachedConfig) return cachedConfig

  try {
    const modules = import.meta.glob('/daav.config.json', { eager: true })
    const mod = modules['/daav.config.json'] as { default: DaavConfig } | undefined
    if (mod?.default) {
      cachedConfig = mod.default
      return cachedConfig
    }
  } catch {
    // Config not found, use defaults
  }

  cachedConfig = {
    title: 'Developer Command Center',
    projectTabs: [],
  }
  return cachedConfig
}

export function getProjectConfig(projectId: string) {
  const config = loadConfig()
  return config.projects?.find((p) => p.projectId === projectId)
}
