import { defineEventHandler } from 'h3'
import { join } from 'path'
import { existsSync, readFileSync } from 'fs'

export default defineEventHandler((event) => {
  // Path to output/session_data.json
  // Assuming we are in web/server/api, go up to root
  const sessionPath = join(process.cwd(), '..', 'output', 'session_data.json')
  
  if (existsSync(sessionPath)) {
    try {
      const data = readFileSync(sessionPath, 'utf-8')
      return JSON.parse(data)
    } catch (e) {
      return { error: "Failed to read session data" }
    }
  } else {
    // Try current directory relative if process.cwd is different
    const sessionPathRel = join(process.cwd(), 'output', 'session_data.json')
    if (existsSync(sessionPathRel)) {
        try {
            const data = readFileSync(sessionPathRel, 'utf-8')
            return JSON.parse(data)
        } catch (e) {
            return { error: "Failed to read session data" }
        }
    }
    
    return { error: "Session file not found" }
  }
})
