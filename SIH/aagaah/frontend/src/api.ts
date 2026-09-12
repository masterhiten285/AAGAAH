export async function get<T>(path: string): Promise<T> {
  const response = await fetch('/api' + path, { signal: AbortSignal.timeout(20000) })
  if (!response.ok) throw new Error(`Request failed (${response.status}). Check the backend connection.`)
  return response.json()
}

export async function post<T>(path: string, body: unknown, token?: string): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['X-Control-Token'] = token
  const response = await fetch('/api' + path, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(30000)
  })
  if (!response.ok) throw new Error(`POST ${path} failed (${response.status})`)
  return response.json()
}

export async function patch<T>(path: string, body: unknown, token?: string): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['X-Control-Token'] = token
  const response = await fetch('/api' + path, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(30000)
  })
  if (!response.ok) throw new Error(`PATCH ${path} failed (${response.status})`)
  return response.json()
}

export async function control(action: string, token: string, step?: number) {
  const response = await fetch('/api/replay/control', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Control-Token': token },
    body: JSON.stringify({ action, ...(step === undefined ? {} : { step }) }),
    signal: AbortSignal.timeout(30000)
  })
  if (!response.ok) throw new Error(response.status === 401 ? 'Control token rejected. Update the token in Connection settings.' : `Replay request failed (${response.status}).`)
  return response.json()
}
