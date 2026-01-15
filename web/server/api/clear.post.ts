import { defineEventHandler, createError } from 'h3'
import { join } from 'path'
import { readdir, unlink, rm, stat } from 'fs/promises'
import { existsSync } from 'fs'
import { getUserIdFromEvent, getUserOutputDir, getUserDownloadsDir, getUserSessionPath } from '../utils/user-utils'

export default defineEventHandler(async (event) => {
    try {
        const userId = getUserIdFromEvent(event)

        if (!userId) {
            throw createError({
                statusCode: 401,
                message: 'User not authenticated'
            })
        }

        const deletedFiles: string[] = []

        // 1. Clear user-specific session data
        const sessionFile = getUserSessionPath(userId)
        if (existsSync(sessionFile)) {
            await unlink(sessionFile)
            deletedFiles.push('session_data.json')
        }

        // 2. Clear user-specific downloads directory
        const downloadsDir = getUserDownloadsDir(userId)
        if (existsSync(downloadsDir)) {
            const files = await readdir(downloadsDir)
            for (const file of files) {
                if (file !== '.gitkeep') {
                    const filePath = join(downloadsDir, file)
                    try {
                        const stats = await stat(filePath)
                        if (stats.isDirectory()) {
                            await rm(filePath, { recursive: true, force: true })
                        } else {
                            await unlink(filePath)
                        }
                        deletedFiles.push(file)
                    } catch (e) {
                        console.error(`Failed to delete ${filePath}:`, e)
                    }
                }
            }
        }

        return {
            success: true,
            message: 'User data cleared successfully',
            deletedFiles
        }

    } catch (error: any) {
        throw createError({
            statusCode: 500,
            message: `Clear failed: ${error.message}`
        })
    }
})
