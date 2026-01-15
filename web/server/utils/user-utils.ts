import { H3Event, getCookie } from 'h3'
import { join } from 'path'
import { existsSync, mkdirSync } from 'fs'

/**
 * Get userId from cookie
 */
export const getUserIdFromEvent = (event: H3Event): string | null => {
    const userId = getCookie(event, 'userId')
    return userId || null
}

/**
 * Get project root directory (one level up from web/)
 */
export const getProjectRoot = (): string => {
    return join(process.cwd(), '..')
}

/**
 * Get base output directory
 */
export const getBaseOutputDir = (): string => {
    const projectRoot = getProjectRoot()
    let outputDir = join(projectRoot, 'output')
    if (!existsSync(outputDir)) {
        outputDir = join(process.cwd(), 'output')
    }
    return outputDir
}

/**
 * Get user-specific output directory
 * Creates the directory if it doesn't exist
 */
export const getUserOutputDir = (userId: string): string => {
    const baseOutput = getBaseOutputDir()
    const userDir = join(baseOutput, `user_${userId}`)

    if (!existsSync(userDir)) {
        mkdirSync(userDir, { recursive: true })
    }

    return userDir
}

/**
 * Get user-specific downloads directory
 * Creates the directory if it doesn't exist
 */
export const getUserDownloadsDir = (userId: string): string => {
    const userOutput = getUserOutputDir(userId)
    const downloadsDir = join(userOutput, 'downloads')

    if (!existsSync(downloadsDir)) {
        mkdirSync(downloadsDir, { recursive: true })
    }

    return downloadsDir
}

/**
 * Get user-specific covers directory
 * Creates the directory if it doesn't exist
 */
export const getUserCoversDir = (userId: string): string => {
    const downloadsDir = getUserDownloadsDir(userId)
    const coversDir = join(downloadsDir, 'covers')

    if (!existsSync(coversDir)) {
        mkdirSync(coversDir, { recursive: true })
    }

    return coversDir
}

/**
 * Get user-specific generated documents directory
 * Creates the directory if it doesn't exist
 */
export const getUserGeneratedDir = (userId: string): string => {
    const userOutput = getUserOutputDir(userId)
    const generatedDir = join(userOutput, 'generated')

    if (!existsSync(generatedDir)) {
        mkdirSync(generatedDir, { recursive: true })
    }

    return generatedDir
}

/**
 * Get user-specific session file path
 */
export const getUserSessionPath = (userId: string): string => {
    const userOutput = getUserOutputDir(userId)
    return join(userOutput, 'session_data.json')
}
