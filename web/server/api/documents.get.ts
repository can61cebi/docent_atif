import { defineEventHandler } from 'h3'
import { join } from 'path'
import { readdir, stat, readFile } from 'fs/promises'
import { existsSync } from 'fs'
import { getUserIdFromEvent, getUserGeneratedDir, getUserSessionPath } from '../utils/user-utils'

export default defineEventHandler(async (event) => {
    try {
        const userId = getUserIdFromEvent(event)

        // If no userId, return empty list
        if (!userId) {
            return []
        }

        const generatedDir = getUserGeneratedDir(userId)

        if (!existsSync(generatedDir)) {
            return []
        }

        // Read user-specific session data for article title and citation count
        const sessionPath = getUserSessionPath(userId)
        let sessionData: any = null
        if (existsSync(sessionPath)) {
            try {
                const content = await readFile(sessionPath, 'utf-8')
                sessionData = JSON.parse(content)
            } catch (e) { }
        }

        const files = await readdir(generatedDir)
        const pdfPattern = /^docentlik_atif_dosyasi_(\d{8}_\d{6})\.pdf$/

        const documents = []

        for (const file of files) {
            const match = file.match(pdfPattern)
            if (match) {
                const timestamp = match[1] // e.g., 20250114_123000
                const fullPath = join(generatedDir, file)
                const fileStat = await stat(fullPath)

                // Related files
                const excelFile = `atif_raporu_${timestamp}.xlsx`
                const listPdf = `atif_listesi_${timestamp}.pdf`

                // Check if related files exist
                const hasExcel = existsSync(join(generatedDir, excelFile))

                // Parse timestamp for creation date
                // Format: YYYYMMDD_HHMMSS
                const year = timestamp.substring(0, 4)
                const month = timestamp.substring(4, 6)
                const day = timestamp.substring(6, 8)
                const hour = timestamp.substring(9, 11)
                const min = timestamp.substring(11, 13)
                const sec = timestamp.substring(13, 15)
                const date = new Date(`${year}-${month}-${day}T${hour}:${min}:${sec}`)

                // Get actual values from session data
                const articleTitle = sessionData?.source_article?.title || 'Doçentlik Atıf Dosyası'
                const citationCount = sessionData?.citing_articles?.length || '-'

                documents.push({
                    id: timestamp,
                    articleTitle,
                    createdAt: date.toISOString(),
                    citationCount,
                    files: {
                        final_pdf: join(generatedDir, file),
                        excel: hasExcel ? join(generatedDir, excelFile) : null
                    }
                })
            }
        }

        // Sort by date desc
        return documents.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())

    } catch (error: any) {
        return []
    }
})
