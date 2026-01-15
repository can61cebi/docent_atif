export default defineNuxtRouteMiddleware((to, from) => {
    // Skip middleware on server-side (localStorage not available)
    if (import.meta.server) {
        return
    }

    // Skip middleware for public pages
    const publicPages = ['/', '/login', '/register']
    if (publicPages.includes(to.path)) {
        return
    }

    // Check if user is logged in
    const user = localStorage.getItem('currentUser')
    if (!user) {
        return navigateTo('/login')
    }
})
