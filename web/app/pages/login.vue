<template>
  <div class="max-w-md mx-auto mt-10">
    <div class="x-panel">
      <div class="x-title">
        <h2>Giriş Yap</h2>
      </div>
      <div class="x-content">
        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label class="block text-xs font-medium text-[#30302f] mb-1">
              E-posta <span class="text-[#bc5f68]">*</span>
            </label>
            <input 
              v-model="email" 
              type="email" 
              class="form-control"
              placeholder="ornek@universite.edu.tr"
              required
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-xs font-medium text-[#30302f] mb-1">
              Şifre <span class="text-[#bc5f68]">*</span>
            </label>
            <input 
              v-model="password" 
              type="password" 
              class="form-control"
              placeholder="••••••••"
              required
            />
          </div>
          
          <div v-if="error" class="mb-4 p-2 bg-[#fde8e8] border border-[#bc5f68] text-[#bc5f68] text-xs">
            {{ error }}
          </div>
          
          <div class="flex items-center justify-between">
            <NuxtLink to="/register" class="text-xs text-[#ae5961] hover:underline">
              Hesap oluştur
            </NuxtLink>
            <button type="submit" class="btn-green" :disabled="isLoading">
              {{ isLoading ? 'Giriş yapılıyor...' : 'Giriş Yap' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const { login, isLoggedIn } = useAuth()

// Redirect if already logged in (client-side only)
onMounted(() => {
  if (isLoggedIn.value) {
    navigateTo('/panel')
  }
})

const handleLogin = async () => {
  error.value = ''
  isLoading.value = true
  
  try {
    const result = await login(email.value, password.value)
    if (result.success) {
      navigateTo('/panel')
    } else {
      error.value = result.message || 'Giriş başarısız'
    }
  } catch (e: any) {
    error.value = e?.message || 'Giriş sırasında hata oluştu'
  } finally {
    isLoading.value = false
  }
}

definePageMeta({
  layout: 'auth'
})
</script>
