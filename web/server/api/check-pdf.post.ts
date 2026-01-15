import { defineEventHandler, readMultipartFormData } from 'h3'
import { join } from 'path'
import { writeFileSync, existsSync, readFileSync, unlinkSync } from 'fs'
import { exec } from 'child_process'
import { promisify } from 'util'
import { getUserIdFromEvent, getUserDownloadsDir, getUserSessionPath, getProjectRoot } from '../utils/user-utils'

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
    const dataPart = body.find(p => p.name === 'data')

    if (!filePart || !dataPart) {
      return { success: false, message: "Missing file or data" }
    }

    const articleData = JSON.parse(dataPart.data.toString())
    const filename = filePart.filename || 'unknown.pdf'

    // Use user-specific downloads directory
    const downloadDir = getUserDownloadsDir(userId)
    const filePath = join(downloadDir, filename)
    writeFileSync(filePath, filePart.data)

    // Read source_article from user-specific session_data.json
    let sourceArticle = {
      title: articleData.source_title || '',
      doi: articleData.source_doi || '',
      authors: articleData.source_authors || [],
      year: articleData.source_year || 2024
    }

    const sessionPath = getUserSessionPath(userId)
    if (existsSync(sessionPath)) {
      try {
        const sessionData = JSON.parse(readFileSync(sessionPath, 'utf-8'))
        if (sessionData.source_article) {
          sourceArticle = {
            title: sessionData.source_article.title || sourceArticle.title,
            doi: sessionData.source_article.doi || sourceArticle.doi,
            authors: sessionData.source_article.authors || sourceArticle.authors,
            year: sessionData.source_article.year || sourceArticle.year
          }
        }
      } catch (e) {
        console.log("Could not read session data, using client-provided data")
      }
    }

    // Merge session source_article into articleData
    const enrichedArticleData = {
      ...articleData,
      source_title: sourceArticle.title,
      source_doi: sourceArticle.doi,
      source_authors: sourceArticle.authors,
      source_year: sourceArticle.year
    }

    // Call Python script
    const projectRoot = getProjectRoot()
    const scriptPath = join(projectRoot, 'check_citation_cli.py')

    // Construct JSON payload for CLI
    const payload = JSON.stringify({
      pdf_path: filePath,
      article_data: enrichedArticleData
    })

    const tempJsonPath = join(downloadDir, `temp_req_${Date.now()}.json`)
    writeFileSync(tempJsonPath, payload)

    try {
      const { stdout, stderr } = await execAsync(`python "${scriptPath}" "${tempJsonPath}"`)

      // Cleanup temp file
      try { unlinkSync(tempJsonPath) } catch (e) { }

      // Parse result
      try {
        const output = stdout.trim()
        const lines = output.split('\n')
        const lastLine = lines[lines.length - 1]

        const result = JSON.parse(lastLine)
        return { success: true, ...result }
      } catch (e) {
        console.error("Python parsing error:", e)
        console.log("Full stdout:", stdout)
        console.log("Full stderr:", stderr)
        return { success: false, message: "Invalid JSON from Python", stdout, stderr }
      }

    } catch (e: any) {
      console.error("Python execution error:", e)
      try { unlinkSync(tempJsonPath) } catch (_) { }
      return { success: false, message: "Python Execution Failed", error: e?.toString?.() || String(e) }
    }
  } catch (error: any) {
    return { success: false, message: error?.toString?.() || String(error) }
  }
})
