import { defineEventHandler, readBody } from 'h3'
import { existsSync, writeFileSync, readFileSync } from 'fs'
import { getUserIdFromEvent, getUserSessionPath, getUserOutputDir } from '../utils/user-utils'

export default defineEventHandler(async (event) => {
    try {
        const body = await readBody(event)
        const userId = getUserIdFromEvent(event)

        // If no userId, cannot save session
        if (!userId) {
            return { success: false, message: 'User not authenticated' }
        }

        // Ensure user output directory exists
        getUserOutputDir(userId)

        const sessionPath = getUserSessionPath(userId)

        // Read existing session data or create new
        let sessionData: any = {}
        if (existsSync(sessionPath)) {
            try {
                sessionData = JSON.parse(readFileSync(sessionPath, 'utf-8'))
            } catch (e) { }
        }

        // Update with new data
        if (body.candidate_info) {
            sessionData.source_article = {
                title: body.candidate_info.articleTitle || '',
                doi: body.candidate_info.doi || '',
                authors: body.candidate_info.firstAuthorSurname
                    ? [body.candidate_info.firstAuthorSurname]
                    : [],
                year: body.candidate_info.year || 2024
            }
            sessionData.candidate = {
                name: body.candidate_info.name || '',
                institution: body.candidate_info.institution || '',
                department: body.candidate_info.department || '',
                applicationPeriod: body.candidate_info.applicationPeriod || ''
            }
        }

        if (body.citing_articles) {
            sessionData.citing_articles = body.citing_articles
        }

        // Save uploaded files list
        if (body.uploaded_files) {
            sessionData.uploaded_files = body.uploaded_files
        }

        // Merge article updates (for PDF matching results)
        if (body.update_article) {
            const { index, data } = body.update_article
            if (sessionData.citing_articles && sessionData.citing_articles[index]) {
                sessionData.citing_articles[index] = {
                    ...sessionData.citing_articles[index],
                    ...data
                }
            }
        }

        // Save to user-specific file
        writeFileSync(sessionPath, JSON.stringify(sessionData, null, 2))

        return { success: true, message: 'Session saved' }
    } catch (error: any) {
        return { success: false, message: error.message }
    }
})
