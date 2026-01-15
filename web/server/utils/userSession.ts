import { join } from 'path'
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs'
import type { H3Event } from 'h3'
import { getCookie } from 'h3'

/**
 * Get the session file path for a specific user
 * Falls back to global session if no user is identified
 */
export function getSessionPath(event?: H3Event): string {
    // Try to get user ID from cookie or header
    let userId = ''

    if (event) {
        // Try cookie first
        userId = getCookie(event, 'userId') || ''

        // Try header as fallback
        if (!userId) {
            userId = event.node.req.headers['x-user-id'] as string || ''
        }
    }

    // Determine output directory
    let outputDir = join(process.cwd(), '..', 'output')
    if (!existsSync(outputDir)) {
        outputDir = join(process.cwd(), 'output')
    }
    if (!existsSync(outputDir)) {
        mkdirSync(outputDir, { recursive: true })
    }

    // Create user-specific or global session path
    const filename = userId ? `session_data_${userId}.json` : 'session_data.json'
    return join(outputDir, filename)
}

/**
 * Get the downloads directory path for a specific user
 */
export function getDownloadsPath(event?: H3Event): string {
    let userId = ''

    if (event) {
        userId = getCookie(event, 'userId') || ''
        if (!userId) {
            userId = event.node.req.headers['x-user-id'] as string || ''
        }
    }

    let downloadDir = join(process.cwd(), '..', 'downloads')
    if (!existsSync(downloadDir)) {
        if (existsSync(join(process.cwd(), 'downloads'))) {
            downloadDir = join(process.cwd(), 'downloads')
        } else {
            mkdirSync(downloadDir, { recursive: true })
        }
    }

    // Create user-specific subdirectory if user is identified
    if (userId) {
        const userDir = join(downloadDir, userId)
        if (!existsSync(userDir)) {
            mkdirSync(userDir, { recursive: true })
        }
        return userDir
    }

    return downloadDir
}

/**
 * Read session data for a user
 */
export function readSessionData(event?: H3Event): any {
    const sessionPath = getSessionPath(event)

    if (existsSync(sessionPath)) {
        try {
            return JSON.parse(readFileSync(sessionPath, 'utf-8'))
        } catch (e) {
            return {}
        }
    }

    return {}
}

/**
 * Write session data for a user
 */
export function writeSessionData(data: any, event?: H3Event): void {
    const sessionPath = getSessionPath(event)
    writeFileSync(sessionPath, JSON.stringify(data, null, 2))
}
