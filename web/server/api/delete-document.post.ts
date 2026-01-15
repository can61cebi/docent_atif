import { defineEventHandler, readBody, createError } from 'h3'
import { join } from 'path'
import { unlink } from 'fs/promises'
import { existsSync } from 'fs'
import { getUserIdFromEvent, getUserGeneratedDir } from '../utils/user-utils'

export default defineEventHandler(async (event) => {
    try {
        const userId = getUserIdFromEvent(event)

        if (!userId) {
            throw createError({
                statusCode: 401,
                message: 'User not authenticated'
            })
        }

        const body = await readBody(event)
        const { id, path } = body

        if (!id && !path) {
            throw createError({
                statusCode: 400,
                message: 'Document ID or path required'
            })
        }

        // Use user-specific generated directory
        const userGeneratedDir = getUserGeneratedDir(userId)

        // Define files to delete
        const filesToDelete = []

        if (path) {
            // Path provided directly - verify it's within user's directory
            if (path.includes(userGeneratedDir) || path.includes(`user_${userId}`)) {
                filesToDelete.push(path)

                // Try to deduce related excel and list files if it matches pattern
                if (path.includes('docentlik_atif_dosyasi_')) {
                    const timestamp = path.match(/(\d{8}_\d{6})/)?.[1]
                    if (timestamp) {
                        filesToDelete.push(join(userGeneratedDir, `atif_raporu_${timestamp}.xlsx`))
                        filesToDelete.push(join(userGeneratedDir, `atif_listesi_${timestamp}.pdf`))
                    }
                }
            } else {
                throw createError({
                    statusCode: 403,
                    message: 'Access denied: Cannot delete files outside your directory'
                })
            }
        } else if (id) {
            // ID provided (timestamp) - use user-specific directory
            filesToDelete.push(join(userGeneratedDir, `docentlik_atif_dosyasi_${id}.pdf`))
            filesToDelete.push(join(userGeneratedDir, `atif_raporu_${id}.xlsx`))
            filesToDelete.push(join(userGeneratedDir, `atif_listesi_${id}.pdf`))
        }

        const deleted = []
        for (const file of filesToDelete) {
            if (existsSync(file)) {
                await unlink(file)
                deleted.push(file)
            }
        }

        return {
            success: true,
            message: 'Document deleted successfully',
            deleted
        }

    } catch (error: any) {
        throw createError({
            statusCode: error.statusCode || 500,
            message: `Delete failed: ${error.message}`
        })
    }
})
