import { defineEventHandler } from 'h3'
import { existsSync, readFileSync } from 'fs'
import { getUserIdFromEvent, getUserSessionPath } from '../utils/user-utils'

export default defineEventHandler((event) => {
  const userId = getUserIdFromEvent(event)

  // If no userId, return empty data
  if (!userId) {
    return { error: "User not authenticated" }
  }

  // Get user-specific session path
  const sessionPath = getUserSessionPath(userId)

  if (existsSync(sessionPath)) {
    try {
      const data = readFileSync(sessionPath, 'utf-8')
      return JSON.parse(data)
    } catch (e) {
      return { error: "Failed to read session data" }
    }
  }

  // Return empty object for new users
  return {}
})
