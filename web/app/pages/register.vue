<template>
  <div class="max-w-md mx-auto mt-10">
    <div class="x-panel">
      <div class="x-title">
        <h2>Hesap Oluştur</h2>
      </div>
      <div class="x-content">
        <form @submit.prevent="handleRegister">
          <div class="mb-4">
            <label class="block text-xs font-medium text-[#30302f] mb-1">
              Ad Soyad <span class="text-[#bc5f68]">*</span>
            </label>
            <input 
              v-model="form.name" 
              type="text" 
              class="form-control"
              placeholder="Dr. Öğr. Üyesi Ahmet Yılmaz"
              required
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-xs font-medium text-[#30302f] mb-1">
              E-posta <span class="text-[#bc5f68]">*</span>
            </label>
            <input 
              v-model="form.email" 
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
              v-model="form.password" 
              type="password" 
              class="form-control"
              placeholder="En az 6 karakter"
              minlength="6"
              required
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-xs font-medium text-[#30302f] mb-1">
              Kurum <span class="text-[#bc5f68]">*</span>
            </label>
            <input 
              v-model="form.institution" 
              type="text" 
              class="form-control"
              placeholder="İstanbul Üniversitesi"
              required
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-xs font-medium text-[#30302f] mb-1">
              Bölüm / Anabilim Dalı
            </label>
            <input 
              v-model="form.department" 
              type="text" 
              class="form-control"
              placeholder="Diş Hekimliği Fakültesi"
            />
          </div>
          
          <div v-if="error" class="mb-4 p-2 bg-[#fde8e8] border border-[#bc5f68] text-[#bc5f68] text-xs">
            {{ error }}
          </div>
          
          <div class="flex items-center justify-between">
            <NuxtLink to="/login" class="text-xs text-[#ae5961] hover:underline">
              Zaten hesabım var
            </NuxtLink>
            <button type="submit" class="btn-green" :disabled="isLoading">
              {{ isLoading ? 'Kaydediliyor...' : 'Kayıt Ol' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Info -->
    <div class="alert-info mt-4">
      <p class="text-sm">
        <strong>Neden kayıt?</strong> Bilgilerinizi bir kez girmeniz yeterli. Her yeni doküman oluşturduğunuzda bilgileriniz otomatik olarak yüklenecektir.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const form = ref({
  name: '',
  email: '',
  password: '',
  institution: '',
  department: ''
})
const error = ref('')
const isLoading = ref(false)

const { register, isLoggedIn } = useAuth()

// Redirect if already logged in (client-side only)
onMounted(() => {
  if (isLoggedIn.value) {
    navigateTo('/panel')
  }
})

const handleRegister = async () => {
  error.value = ''
  isLoading.value = true
  
  try {
    const result = await register(form.value)
    if (result.success) {
      navigateTo('/panel')
    } else {
      error.value = result.message || 'Kayıt başarısız'
    }
  } catch (e: any) {
    error.value = e?.message || 'Kayıt sırasında hata oluştu'
  } finally {
    isLoading.value = false
  }
}

definePageMeta({
  layout: 'auth'
})
</script>
