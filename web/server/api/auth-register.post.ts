import { defineEventHandler, readBody } from 'h3'
import { join } from 'path'
import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'fs'
import { createHash, randomBytes } from 'crypto'

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
    if (!existsSync(outputDir)) {
        mkdirSync(outputDir, { recursive: true })
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

// Save users to file
const saveUsers = (users: User[]): void => {
    const filePath = getUsersFilePath()
    writeFileSync(filePath, JSON.stringify(users, null, 2))
}

export default defineEventHandler(async (event) => {
    try {
        const body = await readBody(event)

        const { name, email, password, institution, department } = body

        // Validation
        if (!name || !email || !password) {
            return { success: false, message: 'Ad, e-posta ve şifre zorunludur' }
        }

        if (password.length < 6) {
            return { success: false, message: 'Şifre en az 6 karakter olmalıdır' }
        }

        // Load existing users
        const users = loadUsers()

        // Check if email already exists
        if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
            return { success: false, message: 'Bu e-posta adresi zaten kayıtlı' }
        }

        // Create new user with hashed password
        const salt = randomBytes(16).toString('hex')
        const passwordHash = hashPassword(password, salt)

        const newUser: User = {
            id: Date.now().toString(),
            name,
            email: email.toLowerCase(),
            institution: institution || '',
            department: department || '',
            passwordHash,
            salt,
            createdAt: new Date().toISOString()
        }

        // Save user
        users.push(newUser)
        saveUsers(users)

        // Return user without sensitive data
        const { passwordHash: _, salt: __, ...safeUser } = newUser

        return {
            success: true,
            message: 'Kayıt başarılı',
            user: safeUser
        }
    } catch (error: any) {
        return { success: false, message: error?.message || 'Kayıt sırasında hata oluştu' }
    }
})
