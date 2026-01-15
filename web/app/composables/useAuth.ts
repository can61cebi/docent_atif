import { ref, computed } from 'vue'

interface User {
    id: string
    name: string
    email: string
    institution: string
    department: string
    createdAt: string
}

const currentUser = ref<User | null>(null)

export const useAuth = () => {
    // Initialize from localStorage on first use
    if (!currentUser.value && import.meta.client) {
        const saved = localStorage.getItem('currentUser')
        if (saved) {
            try {
                currentUser.value = JSON.parse(saved)
            } catch (e) { }
        }
    }

    const isLoggedIn = computed(() => !!currentUser.value)

    const register = async (userData: { name: string, email: string, password: string, institution?: string, department?: string }) => {
        try {
            const response = await $fetch('/api/auth-register', {
                method: 'POST',
                body: userData
            })

            if (response.success && response.user) {
                currentUser.value = response.user as User
                localStorage.setItem('currentUser', JSON.stringify(response.user))
                return { success: true, user: response.user }
            }

            return { success: false, message: response.message || 'Kayıt başarısız' }
        } catch (e: any) {
            return { success: false, message: e?.message || 'Kayıt sırasında hata oluştu' }
        }
    }

    const login = async (email: string, password: string) => {
        try {
            const response = await $fetch('/api/auth-login', {
                method: 'POST',
                body: { email, password }
            })

            if (response.success && response.user) {
                currentUser.value = response.user as User
                localStorage.setItem('currentUser', JSON.stringify(response.user))
                return { success: true, user: response.user }
            }

            return { success: false, message: response.message || 'Giriş başarısız' }
        } catch (e: any) {
            return { success: false, message: e?.message || 'Giriş sırasında hata oluştu' }
        }
    }

    const logout = () => {
        currentUser.value = null
        localStorage.removeItem('currentUser')
    }

    const updateUser = (updates: Partial<User>) => {
        if (!currentUser.value) return

        currentUser.value = { ...currentUser.value, ...updates }
        localStorage.setItem('currentUser', JSON.stringify(currentUser.value))

        // Update in users list
        const users = JSON.parse(localStorage.getItem('users') || '[]')
        const index = users.findIndex((u: User) => u.id === currentUser.value?.id)
        if (index >= 0) {
            users[index] = currentUser.value
            localStorage.setItem('users', JSON.stringify(users))
        }
    }

    // Get user's saved candidate info
    const getSavedCandidateInfo = () => {
        if (!currentUser.value) return null
        const key = `candidateInfo_${currentUser.value.id}`
        const saved = localStorage.getItem(key)
        return saved ? JSON.parse(saved) : null
    }

    // Save candidate info for user
    const saveCandidateInfo = (info: any) => {
        if (!currentUser.value) {
            localStorage.setItem('candidateInfo', JSON.stringify(info))
            return
        }
        const key = `candidateInfo_${currentUser.value.id}`
        localStorage.setItem(key, JSON.stringify(info))
    }

    // Get user's document archive
    const getDocumentArchive = () => {
        if (!currentUser.value) {
            return JSON.parse(localStorage.getItem('documentArchive') || '[]')
        }
        const key = `documentArchive_${currentUser.value.id}`
        return JSON.parse(localStorage.getItem(key) || '[]')
    }

    // Save to document archive
    const saveToArchive = (doc: any) => {
        const archives = getDocumentArchive()
        archives.push(doc)

        if (currentUser.value) {
            const key = `documentArchive_${currentUser.value.id}`
            localStorage.setItem(key, JSON.stringify(archives))
        } else {
            localStorage.setItem('documentArchive', JSON.stringify(archives))
        }
    }

    // Clear all session data
    const clearSessionData = () => {
        if (!currentUser.value) return

        // Clear local storage keys except user/users
        const userId = currentUser.value.id
        localStorage.removeItem(`candidateInfo_${userId}`)
        // DO NOT CLEAR ARCHIVE: localStorage.removeItem(`documentArchive_${userId}`)

        // Also clear legacy keys
        localStorage.removeItem('candidateInfo')
        localStorage.removeItem('citingArticles')
        // DO NOT CLEAR ARCHIVE: localStorage.removeItem('documentArchive')
    }

    return {
        user: currentUser,
        isLoggedIn,
        register,
        login,
        logout,
        updateUser,
        getSavedCandidateInfo,
        saveCandidateInfo,
        getDocumentArchive,
        saveToArchive,
        clearSessionData
    }
}
