import { spawn } from 'child_process'
import { join } from 'path'
import { writeFile, mkdir } from 'fs/promises'
import { existsSync } from 'fs'
import { getUserIdFromEvent, getUserGeneratedDir, getUserSessionPath, getUserDownloadsDir, getProjectRoot } from '../utils/user-utils'

export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const userId = getUserIdFromEvent(event)

    if (!userId) {
        throw createError({
            statusCode: 401,
            message: 'User not authenticated'
        })
    }

    // Get session data
    const { candidateInfo, sourceArticle, citingArticles } = body

    if (!candidateInfo || !citingArticles || citingArticles.length === 0) {
        throw createError({
            statusCode: 400,
            message: 'Missing required data: candidateInfo or citingArticles'
        })
    }

    try {
        // Use user-specific directories
        const projectRoot = getProjectRoot()
        const userGeneratedDir = getUserGeneratedDir(userId)
        const userDownloadsDir = getUserDownloadsDir(userId)
        const sessionFile = getUserSessionPath(userId)

        // Create session data for Python
        const sessionData = {
            candidate: {
                name: candidateInfo.name,
                institution: candidateInfo.institution,
                department: candidateInfo.department,
                application_period: candidateInfo.applicationPeriod
            },
            source_article: {
                title: sourceArticle?.articleTitle || candidateInfo.articleTitle,
                doi: sourceArticle?.doi || candidateInfo.doi,
                authors: [candidateInfo.firstAuthorSurname],
                year: parseInt(sourceArticle?.year || candidateInfo.year) || 2025
            },
            citing_articles: citingArticles.map((a: any, i: number) => {
                // Handle pdf_path - check if already absolute or just filename
                let pdfPath = null
                if (a.pdf_path) {
                    // Check if already absolute path (contains drive letter or starts with /)
                    if (a.pdf_path.includes(':') || a.pdf_path.startsWith('/')) {
                        pdfPath = a.pdf_path
                    } else {
                        // Use user-specific downloads directory
                        pdfPath = join(userDownloadsDir, a.pdf_path)
                    }
                }

                // Extract cover paths - handle both object format {name, path} and string format
                const coverPaths = (a.cover_pages || [])
                    .map((cp: any) => typeof cp === 'string' ? cp : cp.path)
                    .filter(Boolean)

                return {
                    title: a.title,
                    authors: a.authors || [],
                    journal: a.journal || '',
                    year: a.year || 0,
                    volume: a.volume || '',
                    issue: a.issue || '',
                    pages: a.pages || '',
                    doi: a.doi || '',
                    pdf_path: pdfPath,
                    title_page: 1,
                    citation_pages: a.citation_pages || [],
                    citation_bboxes: a.citation_bboxes || [],
                    reference_page: a.reference_page || null,
                    reference_number: a.reference_number || null,
                    reference_bbox: a.reference_bbox || null,
                    cover_page_path: coverPaths[0] || a.coverPath || null,
                    cover_pages_all: coverPaths
                }
            }),
            saved_at: new Date().toISOString()
        }

        // Write session file
        await writeFile(sessionFile, JSON.stringify(sessionData, null, 2), 'utf-8')

        // Run Python script to generate documents
        // Note: OUTPUT_DIR in Python is overridden via command line
        const pythonScript = `
import sys
import json
sys.path.insert(0, '${projectRoot.replace(/\\/g, '\\\\')}')

from config import CandidateInfo, SourceArticle, CitingArticle
from document_builder import CitationDocumentBuilder, FinalDocumentAssembler
from datetime import datetime
from pathlib import Path

# User-specific output directory
USER_OUTPUT_DIR = Path('${userGeneratedDir.replace(/\\/g, '\\\\')}')

# Load session data
with open('${sessionFile.replace(/\\/g, '\\\\')}', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create objects
candidate = CandidateInfo(
    name=data['candidate']['name'],
    institution=data['candidate']['institution'],
    department=data['candidate']['department'],
    application_period=data['candidate']['application_period']
)

source = SourceArticle(
    title=data['source_article']['title'],
    doi=data['source_article']['doi'],
    authors=data['source_article']['authors'],
    year=data['source_article']['year']
)

for a in data['citing_articles']:
    article = CitingArticle(
        title=a['title'],
        authors=a['authors'],
        journal=a['journal'],
        year=a['year'],
        volume=a['volume'],
        issue=a['issue'],
        pages=a['pages'],
        doi=a['doi'],
        pdf_path=a['pdf_path'],
        title_page=a['title_page'],
        citation_pages=a['citation_pages'],
        citation_bboxes=a.get('citation_bboxes', []),
        reference_page=a['reference_page'],
        reference_number=a['reference_number'],
        reference_bbox=a.get('reference_bbox'),
        cover_page_path=a.get('cover_page_path'),
        cover_pages_all=a.get('cover_pages_all', [])
    )
    source.citing_articles.append(article)

# Generate documents to user-specific directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

builder = CitationDocumentBuilder(candidate, source)
list_pdf = str(USER_OUTPUT_DIR / f"atif_listesi_{timestamp}.pdf")
builder.build_pdf(list_pdf)

excel_path = str(USER_OUTPUT_DIR / f"atif_raporu_{timestamp}.xlsx")
builder.build_excel(excel_path)

final_pdf = str(USER_OUTPUT_DIR / f"docentlik_atif_dosyasi_{timestamp}.pdf")
assembler = FinalDocumentAssembler(source)
assembler.assemble(list_pdf, final_pdf)

print(json.dumps({
    "success": True,
    "files": {
        "list_pdf": list_pdf,
        "excel": excel_path,
        "final_pdf": final_pdf
    }
}))
`

        // Execute Python
        return new Promise((resolve, reject) => {
            const python = spawn('python', ['-c', pythonScript], {
                cwd: projectRoot,
                env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
            })

            let stdout = ''
            let stderr = ''

            python.stdout.on('data', (data) => {
                stdout += data.toString()
            })

            python.stderr.on('data', (data) => {
                stderr += data.toString()
            })

            python.on('close', (code) => {
                if (code === 0) {
                    try {
                        // Find JSON in output
                        const jsonMatch = stdout.match(/\{[\s\S]*"success"[\s\S]*\}/)
                        if (jsonMatch) {
                            resolve(JSON.parse(jsonMatch[0]))
                        } else {
                            resolve({ success: true, message: 'Generated', stdout })
                        }
                    } catch (e) {
                        resolve({ success: true, stdout })
                    }
                } else {
                    reject(createError({
                        statusCode: 500,
                        message: `Python error: ${stderr || stdout}`
                    }))
                }
            })
        })

    } catch (error: any) {
        throw createError({
            statusCode: 500,
            message: error.message || 'Generation failed'
        })
    }
})
