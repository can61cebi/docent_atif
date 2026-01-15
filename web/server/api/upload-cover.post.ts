import { defineEventHandler, readMultipartFormData } from 'h3'
import { join } from 'path'
import { writeFileSync, existsSync, readFileSync } from 'fs'
import { getUserIdFromEvent, getUserCoversDir, getUserSessionPath } from '../utils/user-utils'

export default defineEventHandler(async (event) => {
    try {
        const userId = getUserIdFromEvent(event)

        if (!userId) {
            return { success: false, message: "User not authenticated" }
        }

        const body = await readMultipartFormData(event)
        if (!body) {
            return { success: false, message: "No multipart data" }
        }

        const filePart = body.find(p => p.name === 'file')
        const doiPart = body.find(p => p.name === 'doi')
        const indexPart = body.find(p => p.name === 'index')
        const coverIndexPart = body.find(p => p.name === 'coverIndex')

        if (!filePart) {
            return { success: false, message: "Missing file" }
        }

        const doi = doiPart?.data.toString() || 'unknown'
        const articleIndex = indexPart?.data.toString() || '0'
        const coverIndex = coverIndexPart?.data.toString() || '0'
        const originalFilename = filePart.filename || 'cover.pdf'
        const fileExt = originalFilename.split('.').pop() || 'pdf'

        // Use user-specific covers directory
        const coversDir = getUserCoversDir(userId)

        // Sanitize DOI for filename
        const sanitizedDoi = doi.replace(/[\/\\:*?"<>|]/g, '_')
        const coverFilename = `cover_${sanitizedDoi}_${articleIndex}_${coverIndex}.${fileExt}`
        const coverPath = join(coversDir, coverFilename)

        // Save the file
        writeFileSync(coverPath, filePart.data)

        // Update user-specific session data
        const sessionPath = getUserSessionPath(userId)
        let sessionData: any = {}

        if (existsSync(sessionPath)) {
            try {
                sessionData = JSON.parse(readFileSync(sessionPath, 'utf-8'))
            } catch (e) { }
        }

        // Update citing_articles with cover info
        const artIdx = parseInt(articleIndex)
        if (sessionData.citing_articles && sessionData.citing_articles[artIdx]) {
            if (!sessionData.citing_articles[artIdx].cover_pages) {
                sessionData.citing_articles[artIdx].cover_pages = []
            }
            sessionData.citing_articles[artIdx].cover_pages.push({
                name: originalFilename,
                path: coverPath
            })

            // Write updated session
            writeFileSync(sessionPath, JSON.stringify(sessionData, null, 2))
        }

        return {
            success: true,
            message: 'Cover uploaded',
            path: coverPath,
            filename: coverFilename
        }
    } catch (error: any) {
        console.error('Cover upload error:', error)
        return { success: false, message: error?.toString?.() || String(error) }
    }
})
