<template>
  <NuxtLayout name="panel">
    <div>
      <!-- Page Title -->
      <div class="mb-4">
        <h1 class="text-base font-medium text-[#30302f]">Doküman Oluştur</h1>
      </div>

      <!-- Summary Panel -->
      <div class="x-panel">
        <div class="x-title">
          <h2>Özet Bilgiler</h2>
        </div>
        <div class="x-content">
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-[#7c7c7c] text-xs mb-1">Aday</p>
              <p class="text-[#30302f] font-medium">{{ candidateInfo.name || '-' }}</p>
            </div>
            <div>
              <p class="text-[#7c7c7c] text-xs mb-1">Kurum</p>
              <p class="text-[#30302f]">{{ candidateInfo.institution || '-' }}</p>
            </div>
            <div>
              <p class="text-[#7c7c7c] text-xs mb-1">Kaynak Makale</p>
              <p class="text-[#30302f]">{{ candidateInfo.articleTitle || '-' }}</p>
            </div>
            <div>
              <p class="text-[#7c7c7c] text-xs mb-1">Toplam Atıf</p>
              <p class="text-[#30302f] font-medium">{{ articles.length }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Options Panel -->
      <div class="x-panel">
        <div class="x-title">
          <h2>Çıktı Seçenekleri</h2>
        </div>
        <div class="x-content">
          <div class="space-y-3">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="options.generatePdf" class="w-4 h-4">
              <span class="text-sm text-[#30302f]">PDF Dokümanı Oluştur</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="options.generateExcel" class="w-4 h-4">
              <span class="text-sm text-[#30302f]">Excel Raporu Oluştur</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="options.highlightCitations" class="w-4 h-4">
              <span class="text-sm text-[#30302f]">Atıf Cümlelerini İşaretle (Sarı)</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="options.highlightBibliography" class="w-4 h-4">
              <span class="text-sm text-[#30302f]">Kaynakça Referansını İşaretle (Sarı)</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Generate Button -->
      <div class="flex items-center justify-between">
        <NuxtLink to="/panel/pdfs" class="btn-gray">← Geri</NuxtLink>
        <button 
          @click="generateDocument"
          :disabled="isGenerating"
          class="btn-green flex items-center gap-1"
          :class="{ 'opacity-50 cursor-not-allowed': isGenerating }"
        >
          {{ isGenerating ? 'Oluşturuluyor...' : 'Dokümanları Oluştur' }}
        </button>
      </div>

      <!-- Result Panel -->
      <div v-if="result" class="x-panel mt-4">
        <div class="x-title">
          <h2>{{ result.success ? 'Oluşturuldu' : 'Hata' }}</h2>
        </div>
        <div class="x-content">
          <div v-if="result.success" class="space-y-2">
            <p class="text-sm text-[#5eab8c]">Dokümanlar başarıyla oluşturuldu.</p>
            <NuxtLink to="/panel/documents" class="btn-green inline-block">
              Arşive Git →
            </NuxtLink>
          </div>
          <div v-else class="text-sm text-[#bc5f68]">
            {{ result.error || 'Bilinmeyen hata' }}
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const { getSavedCandidateInfo, saveToArchive } = useAuth()

const candidateInfo = ref<any>({})
const articles = ref<any[]>([])
const options = ref({
  generatePdf: true,
  generateExcel: true,
  highlightCitations: true,
  highlightBibliography: true
})
const isGenerating = ref(false)
const result = ref<any>(null)

onMounted(async () => {
  // Load from server session (single source of truth)
  try {
    const sessionData = await $fetch('/api/session-get')
    if (sessionData.success) {
      // Merge candidate info from both sources
      candidateInfo.value = {
        name: sessionData.candidate?.name || '',
        institution: sessionData.candidate?.institution || '',
        department: sessionData.candidate?.department || '',
        applicationPeriod: sessionData.candidate?.applicationPeriod || '',
        articleTitle: sessionData.source_article?.title || '',
        doi: sessionData.source_article?.doi || '',
        firstAuthorSurname: sessionData.source_article?.authors?.[0] || '',
        year: sessionData.source_article?.year || ''
      }
      articles.value = sessionData.citing_articles || []
    }
  } catch (e) {
    console.error('Failed to load session:', e)
  }
})

const generateDocument = async () => {
  isGenerating.value = true
  result.value = null
  
  try {
    const response = await $fetch('/api/generate', {
      method: 'POST',
      body: {
        candidateInfo: candidateInfo.value,
        sourceArticle: candidateInfo.value,
        citingArticles: articles.value,
        options: options.value
      }
    })
    
    result.value = response
    
    if (response.success) {
      saveToArchive({
        id: Date.now(),
        createdAt: new Date().toISOString(),
        candidateName: candidateInfo.value.name,
        articleTitle: candidateInfo.value.articleTitle,
        citationCount: articles.value.length,
        files: response.files
      })
    }
  } catch (error: any) {
    result.value = { 
      success: false, 
      error: error.data?.message || error.message || 'Oluşturma hatası' 
    }
  } finally {
    isGenerating.value = false
  }
}
</script>
