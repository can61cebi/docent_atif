import { defineEventHandler, getQuery, getCookie } from 'h3'
import { join } from 'path'
import { existsSync, createReadStream } from 'fs'
import { stat } from 'fs/promises'

export default defineEventHandler(async (event) => {
    const query = getQuery(event)
    const filePath = query.path as string

    if (!filePath) {
        throw createError({
            statusCode: 400,
            message: 'Path is required'
        })
    }

    // Get userId from cookie
    const userId = getCookie(event, 'userId')

    if (!userId) {
        throw createError({
            statusCode: 401,
            message: 'User not authenticated'
        })
    }

    // Security: Only allow files from user's own output directory
    const projectRoot = join(process.cwd(), '..')
    const userOutputDir = join(projectRoot, 'output', `user_${userId}`)

    const absolutePath = filePath.startsWith('C:') || filePath.startsWith('/')
        ? filePath
        : join(projectRoot, filePath)

    // Verify path is within user's directory
    if (!absolutePath.includes(`user_${userId}`)) {
        throw createError({
            statusCode: 403,
            message: 'Access denied: Cannot access files outside your directory'
        })
    }

    if (!existsSync(absolutePath)) {
        throw createError({
            statusCode: 404,
            message: 'File not found'
        })
    }

    const fileStat = await stat(absolutePath)
    const fileName = absolutePath.split(/[\\/]/).pop()

    // Set headers for download
    setHeaders(event, {
        'Content-Type': absolutePath.endsWith('.pdf') ? 'application/pdf' : 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${fileName}"`,
        'Content-Length': fileStat.size.toString()
    })

    return sendStream(event, createReadStream(absolutePath))
})