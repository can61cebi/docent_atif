import { defineEventHandler, getCookie } from 'h3'
import { existsSync, readFileSync } from 'fs'
import { getUserIdFromEvent, getUserSessionPath, getBaseOutputDir } from '../utils/user-utils'
import { join } from 'path'

export default defineEventHandler((event) => {
    const userId = getUserIdFromEvent(event)

    // If no userId, return empty data
    if (!userId) {
        return {
            success: true,
            candidate: null,
            source_article: null,
            citing_articles: []
        }
    }

    // Get user-specific session path
    const sessionPath = getUserSessionPath(userId)

    if (existsSync(sessionPath)) {
        try {
            const data = readFileSync(sessionPath, 'utf-8')
            const parsed = JSON.parse(data)
            return {
                success: true,
                candidate: parsed.candidate || null,
                source_article: parsed.source_article || null,
                citing_articles: parsed.citing_articles || [],
                uploaded_files: parsed.uploaded_files || []
            }
        } catch (e) {
            return { success: false, error: "Failed to read session data" }
        }
    }

    return {
        success: true,
        candidate: null,
        source_article: null,
        citing_articles: []
    }
})
