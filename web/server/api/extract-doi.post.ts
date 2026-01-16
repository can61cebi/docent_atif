import { defineEventHandler, readMultipartFormData } from 'h3'
import { join } from 'path'
import { writeFileSync, unlinkSync, existsSync, mkdirSync } from 'fs'
import { exec } from 'child_process'
import { promisify } from 'util'
import { getUserIdFromEvent, getUserDownloadsDir, getProjectRoot } from '../utils/user-utils'

const execAsync = promisify(exec)

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

        if (!filePart) {
            return { success: false, message: "Missing file" }
        }

        const filename = filePart.filename || 'unknown.pdf'

        // Use user-specific downloads directory
        const downloadDir = getUserDownloadsDir(userId)
        const filePath = join(downloadDir, filename)
        writeFileSync(filePath, filePart.data)

        // Call Python script to extract DOI
        const projectRoot = getProjectRoot()
        const scriptPath = join(projectRoot, 'extract_doi.py')

        try {
            const { stdout, stderr } = await execAsync(`python "${scriptPath}" "${filePath}"`)

            // Parse result
            try {
                const output = stdout.trim()
                const lines = output.split('\n')
                const lastLine = lines[lines.length - 1]

                const result = JSON.parse(lastLine)
                return { success: true, filename, ...result }
            } catch (e) {
                console.error("Python parsing error:", e)
                return { success: false, message: "Invalid JSON from Python", stdout, stderr }
            }

        } catch (e: any) {
            console.error("Python execution error:", e)
            return { success: false, message: "Python Execution Failed", error: e?.toString?.() || String(e) }
        }
    } catch (error: any) {
        return { success: false, message: error?.toString?.() || String(error) }
    }
})
