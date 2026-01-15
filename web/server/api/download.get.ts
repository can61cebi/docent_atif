import { defineEventHandler, getQuery } from 'h3'
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

    // Security: Only allow files from output or downloads directory
    const projectRoot = join(process.cwd(), '..')
    const outputDir = join(projectRoot, 'output')
    const downloadsDir = join(projectRoot, 'downloads')

    const absolutePath = filePath.startsWith('C:') || filePath.startsWith('/') 
        ? filePath 
        : join(projectRoot, filePath)

    if (!absolutePath.startsWith(outputDir) && !absolutePath.startsWith(downloadsDir)) {
        throw createError({
            statusCode: 403,
            message: 'Access denied'
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