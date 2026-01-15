import { defineEventHandler, readBody } from 'h3'
import { join } from 'path'
import { existsSync, readFileSync } from 'fs'
import { createHash } from 'crypto'

interface User {
    id: string
    name: string
    email: string
    institution: string
    department: string
    passwordHash: string
    salt: string
    createdAt: string
}

// Hash password with salt
const hashPassword = (password: string, salt: string): string => {
    return createHash('sha256').update(password + salt).digest('hex')
}

// Get users file path
const getUsersFilePath = (): string => {
    let outputDir = join(process.cwd(), '..', 'output')
    if (!existsSync(outputDir)) {
        outputDir = join(process.cwd(), 'output')
    }
    return join(outputDir, 'users.json')
}

// Load users from file
const loadUsers = (): User[] => {
    const filePath = getUsersFilePath()
    if (existsSync(filePath)) {
        try {
            return JSON.parse(readFileSync(filePath, 'utf-8'))
        } catch (e) {
            return []
        }
    }
    return []
}

export default defineEventHandler(async (event) => {
    try {
        const body = await readBody(event)

        const { email, password } = body

        // Validation
        if (!email || !password) {
            return { success: false, message: 'E-posta ve şifre zorunludur' }
        }

        // Load users
        const users = loadUsers()

        // Find user by email
        const user = users.find(u => u.email.toLowerCase() === email.toLowerCase())

        if (!user) {
            return { success: false, message: 'E-posta veya şifre hatalı' }
        }

        // Verify password
        const inputHash = hashPassword(password, user.salt)

        if (inputHash !== user.passwordHash) {
            return { success: false, message: 'E-posta veya şifre hatalı' }
        }

        // Return user without sensitive data
        const { passwordHash: _, salt: __, ...safeUser } = user

        return {
            success: true,
            message: 'Giriş başarılı',
            user: safeUser
        }
    } catch (error: any) {
        return { success: false, message: error?.message || 'Giriş sırasında hata oluştu' }
    }
})
