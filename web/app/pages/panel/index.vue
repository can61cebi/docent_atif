<template>
  <NuxtLayout name="panel">
    <div>
      <!-- Page Title -->
      <div class="mb-4">
        <h1 class="text-base font-medium text-[#30302f]">Aday Bilgileri</h1>
      </div>

      <!-- Form Panel -->
      <div class="x-panel">
        <div class="x-title flex items-center justify-between">
          <h2>Kişisel Bilgiler</h2>
          <span class="text-xs text-[#7c7c7c]">(*) Zorunlu alanlar</span>
        </div>
        <div class="x-content">
          <form @submit.prevent="saveAndContinue">
            <!-- Candidate Info Section -->
            <div class="grid md:grid-cols-2 gap-4 mb-6">
              <div>
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
              <div>
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
              <div>
                <label class="block text-xs font-medium text-[#30302f] mb-1">
                  Bölüm / Anabilim Dalı <span class="text-[#bc5f68]">*</span>
                </label>
                <input 
                  v-model="form.department" 
                  type="text" 
                  class="form-control"
                  placeholder="Diş Hekimliği Fakültesi"
                  required
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-[#30302f] mb-1">
                  Başvuru Dönemi <span class="text-[#bc5f68]">*</span>
                </label>
                <select v-model="form.applicationPeriod" class="form-control" required>
                  <option value="">Seçiniz...</option>
                  <option v-for="period in applicationPeriods" :key="period" :value="period">{{ period }}</option>
                </select>
              </div>
            </div>

            <!-- Source Article Section -->
            <div class="border-t border-[#d0d0d0] pt-4">
              <h3 class="text-sm font-medium text-[#30302f] mb-3">Kaynak Makale Bilgileri</h3>
              
              <div class="grid md:grid-cols-2 gap-4">
                <div class="md:col-span-2">
                  <label class="block text-xs font-medium text-[#30302f] mb-1">
                    Makale Başlığı <span class="text-[#bc5f68]">*</span>
                  </label>
                  <input 
                    v-model="form.articleTitle" 
                    type="text" 
                    class="form-control"
                    placeholder="Makalenin tam başlığı"
                    required
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium text-[#30302f] mb-1">
                    DOI <span class="text-[#bc5f68]">*</span>
                  </label>
                  <input 
                    v-model="form.doi" 
                    type="text" 
                    class="form-control"
                    placeholder="10.1016/j.jdent.2024.001"
                    required
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium text-[#30302f] mb-1">
                    Yayın Yılı <span class="text-[#bc5f68]">*</span>
                  </label>
                  <input 
                    v-model="form.year" 
                    type="number" 
                    min="1990" 
                    max="2030"
                    class="form-control"
                    placeholder="2024"
                    required
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium text-[#30302f] mb-1">
                    İlk Yazarın Soyadı <span class="text-[#bc5f68]">*</span>
                  </label>
                  <input 
                    v-model="form.firstAuthorSurname" 
                    type="text" 
                    class="form-control"
                    placeholder="Atıf aramasında kullanılır"
                    required
                  />
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center justify-end gap-2 pt-4 mt-4 border-t border-[#d0d0d0]">
              <button type="button" class="btn-gray" @click="openClearModal">
                Temizle
              </button>
              <button type="submit" class="btn-green flex items-center gap-1">
                <span>Kaydet ve Devam Et</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      </div>

      
      <!-- Clear Confirmation Modal -->
      <ConfirmModal
        :show="showClearModal"
        type="warning"
        title="Oturumu Temizle"
        message="Aday bilgileri, yüklenen dosyalar ve geçici veriler temizlenecektir. Oluşturulan dokümanlar silinmeyecektir."
        confirm-text="Temizle"
        @confirm="confirmClear"
        @cancel="showClearModal = false"
      />
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

const { user, saveCandidateInfo, getSavedCandidateInfo } = useAuth()

// Helper to calculate upcoming application periods
const getApplicationPeriods = () => {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth() + 1 // 1-12
  
  const periods: string[] = []
  
  // Determine next upcoming period and one after
  // Mart = March, Ekim = October
  if (currentMonth <= 3) {
    // Jan-Mar: Next is Mart of current year
    periods.push(`${currentYear} Mart`)
    periods.push(`${currentYear} Ekim`)
  } else if (currentMonth <= 10) {
    // Apr-Oct: Next is Ekim of current year
    periods.push(`${currentYear} Ekim`)
    periods.push(`${currentYear + 1} Mart`)
  } else {
    // Nov-Dec: Next is Mart of next year
    periods.push(`${currentYear + 1} Mart`)
    periods.push(`${currentYear + 1} Ekim`)
  }
  
  return periods
}

const applicationPeriods = computed(() => getApplicationPeriods())
const defaultPeriod = computed(() => applicationPeriods.value[0] || '2026 Mart')

const form = ref({
  name: '',
  institution: '',
  department: '',
  applicationPeriod: defaultPeriod.value,
  articleTitle: '',
  doi: '',
  year: 2025,
  firstAuthorSurname: ''
})

onMounted(() => {
  // Load user info first
  if (user.value) {
    form.value.name = user.value.name || ''
    form.value.institution = user.value.institution || ''
    form.value.department = user.value.department || ''
  }
  
  // Then load saved candidate info
  const saved = getSavedCandidateInfo()
  if (saved) {
    Object.assign(form.value, saved)
  }
})

const saveAndContinue = async () => {
  // Save to localStorage (for backward compatibility)
  saveCandidateInfo(form.value)
  
  // Also save to server session
  try {
    await $fetch('/api/session-save', {
      method: 'POST',
      body: { candidate_info: form.value }
    })
  } catch (e) {
    console.error('Failed to save to server:', e)
  }
  
  navigateTo('/panel/import')
}

const { clearSessionData } = useAuth()

const showClearModal = ref(false)

const openClearModal = () => {
  showClearModal.value = true
}

const confirmClear = async () => {
  showClearModal.value = false
  
  try {
    // 1. Clear Server Files
    await $fetch('/api/clear', { method: 'POST' })

    // 2. Clear Local Storage
    clearSessionData()
    
    // Reset Form (Keep User Info)
    if (user.value) {
      form.value = {
        name: user.value.name || '',
        institution: user.value.institution || '',
        department: user.value.department || '',
        applicationPeriod: defaultPeriod.value,
        articleTitle: '',
        doi: '',
        year: 2025,
        firstAuthorSurname: ''
      }
    } else {
       // Reset completely
       form.value = {
        name: '',
        institution: '',
        department: '',
        applicationPeriod: defaultPeriod.value,
        articleTitle: '',
        doi: '',
        year: 2025,
        firstAuthorSurname: ''
      }
    }
    
    // Success feedback via UI if needed, for now modal closes implies success
  } catch (e) {
    alert('Temizleme sırasında hata oluştu.')
    console.error(e)
  }
}
</script>
