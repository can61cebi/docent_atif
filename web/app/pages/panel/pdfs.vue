<template>
  <NuxtLayout name="panel">
    <div>
      <!-- Page Title -->
      <div class="mb-4">
        <h1 class="text-base font-medium text-[#30302f]">PDF Dosyaları</h1>
      </div>

      <!-- No Articles Warning -->
      <div v-if="articles.length === 0" class="alert-warning">
        <p class="text-sm">
          <strong>Dikkat:</strong> Henüz atıf yüklenmemiş. Önce 
          <NuxtLink to="/panel/import" class="underline">WoS dosyası yükleyin</NuxtLink>.
        </p>
      </div>

      <div v-else>
        <!-- Bulk Upload Area -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div class="lg:col-span-2">
             <div 
              :class="[
                'h-[220px] p-6 border-2 border-dashed rounded-lg text-center transition-all cursor-pointer flex flex-col items-center justify-center',
                isDragging 
                  ? 'border-blue-500 bg-blue-50 scale-[1.02] shadow-lg' 
                  : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
              ]"
              @dragover.prevent 
              @dragenter.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleBulkDrop"
              @click="$refs.bulkInput.click()"
            >
              <!-- Uploading Files Indicator -->
              <div v-if="uploadingFiles.length > 0" class="flex flex-col items-center gap-3">
                <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                  <svg class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-base font-medium text-blue-700">{{ uploadingFiles.length }} dosya yükleniyor...</p>
                  <p class="text-xs text-blue-500 mt-1">{{ uploadingFiles[0] }}</p>
                </div>
              </div>
              
              <!-- Drag Active State -->
              <div v-else-if="isDragging" class="flex flex-col items-center gap-3">
                <div class="w-12 h-12 rounded-full bg-blue-200 flex items-center justify-center text-blue-600 animate-pulse">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
                <div>
                  <p class="text-base font-medium text-blue-700">Dosyaları buraya bırakın!</p>
                </div>
              </div>
              
              <!-- Default State -->
              <div v-else class="flex flex-col items-center gap-3">
                <div class="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-500">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <p class="text-base font-medium text-gray-700">Tüm Makale PDF'lerini Buraya Yükleyin</p>
                  <p class="text-xs text-gray-500 mt-1">Sürükleyip bırakın veya seçmek için tıklayın</p>
                </div>
                <input 
                  ref="bulkInput"
                  type="file" 
                  multiple 
                  accept=".pdf" 
                  class="hidden" 
                  @change="handleBulkUpload" 
                />
              </div>
            </div>
          </div>

          <!-- Uploaded Files Stats/List -->
          <div class="bg-white border border-gray-200 rounded-lg shadow-sm flex flex-col h-[220px]">
            <div class="px-4 py-3 border-b border-gray-100 bg-gray-50 rounded-t-lg">
              <h3 class="text-sm font-medium text-gray-700">Yüklenen Dosyalar</h3>
            </div>
            <div class="p-0 flex-1 overflow-y-scroll">
              <ul v-if="uploadedFiles.length > 0" class="divide-y divide-gray-100">
                <li v-for="(file, i) in uploadedFiles" :key="i" class="px-4 py-2 flex items-center justify-between hover:bg-gray-50 text-xs">
                  <div class="flex items-center gap-2 overflow-hidden">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <span class="truncate text-gray-600" :title="file.name">{{ getFilename(file.name) }}</span>
                  </div>
                  <button @click="removeUploadedFile(file.name)" class="text-gray-400 hover:text-red-500 p-1 cursor-pointer">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </li>
              </ul>
              <div v-else class="h-full flex flex-col items-center justify-center p-4 text-center">
                <p class="text-xs text-gray-400">Henüz dosya yüklenmedi.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Articles List -->
        <div class="x-panel">
          <div class="x-title flex items-center justify-between">
            <h2>Makale Listesi & Eşleşme Durumu</h2>
            <div class="flex items-center gap-3">
              <span class="text-xs px-2 py-1 rounded bg-green-50 text-green-700 border border-green-100">
                {{ completedCount }} Tamamlandı
              </span>
              <span class="text-xs px-2 py-1 rounded bg-red-50 text-red-700 border border-red-100">
                {{ articles.length - completedCount }} Bekliyor
              </span>
            </div>
          </div>
          <div class="x-content p-0">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="w-12">#</th>
                  <th>Yayın Bilgileri</th>
                  <th class="w-48">Eşleşen Dosya</th>
                  <th class="w-32">Kapak Sayfaları <span class="text-[#bc5f68]">*</span></th>
                  <th class="w-64">Atıf Kontrolü</th>
                  <th class="w-16">Durum</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(article, index) in articles" :key="index">
                  <td class="text-center">{{ index + 1 }}</td>
                  <td class="text-xs">
                    <div class="text-gray-500 text-[10px] mb-0.5" v-if="article.authors && article.authors.length > 0">
                      {{ formatAuthors(article.authors) }}
                    </div>
                    <div class="font-medium text-[#30302f] mb-1">{{ article.title }}</div>
                    <div class="flex items-center gap-2 flex-wrap">
                      <span v-if="article.journal" class="text-gray-500 text-[10px]">{{ article.journal }} ({{ article.year || '-' }})</span>
                      <a v-if="article.doi" :href="`https://doi.org/${article.doi}`" target="_blank" class="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-100 text-[10px] hover:underline flex items-center gap-1" @click.stop>
                        <span>{{ article.doi }}</span>
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                      </a>
                    </div>
                  </td>
                  <td>
                    <div v-if="article.pdf_path" class="group relative">
                      <div class="flex items-center gap-2 p-1.5 rounded bg-green-50 border border-green-100 text-[#5eab8c] text-xs">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span class="truncate max-w-[140px]" :title="article.pdf_path">{{ getFilename(article.pdf_path) }}</span>
                      </div>
                      <button @click="unlinkPdf(index)" class="cursor-pointer absolute -right-2 -top-2 bg-white rounded-full p-0.5 shadow border border-gray-200 text-gray-400 hover:text-red-600 hidden group-hover:block" title="Eşleşmeyi Kaldır">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                      </button>
                    </div>
                    <div v-else class="text-xs text-gray-400 italic flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                      Eşleşme bekleniyor...
                    </div>
                  </td>
                  <td>
                    <div class="flex flex-col gap-1">
                      <!-- Existing covers -->
                      <div class="flex flex-wrap gap-1">
                        <span 
                          v-for="(cover, ci) in (article.cover_pages || [])" 
                          :key="ci"
                          class="inline-flex items-center gap-1 bg-white border border-gray-300 rounded px-1.5 py-0.5 text-[10px] text-gray-600"
                        >
                          Kapak {{ ci + 1 }}
                          <button @click="removeCover(index, ci)" class="cursor-pointer text-gray-400 hover:text-red-500 ml-0.5">×</button>
                        </span>
                      </div>
                      
                      <!-- Add cover button -->
                      <div>
                        <label class="text-[10px] text-blue-600 hover:text-blue-800 cursor-pointer inline-flex items-center gap-0.5 hover:underline">
                          <span>+ Kapak Ekle</span>
                          <input type="file" accept=".pdf,.jpg,.png" class="hidden" @change="e => handleCoverUpload(e, index)" />
                        </label>
                      </div>
                    </div>
                  </td>
                  <td class="text-xs">
                    <div v-if="!article.pdf_path" class="text-gray-300">-</div>
                    <div v-else>
                      <!-- Found State - Detailed Card -->
                      <div v-if="article.citation_status === 'found'" class="space-y-2">
                        <div class="inline-flex items-center gap-1 text-green-600 bg-green-50 px-2 py-0.5 rounded-full text-[10px] font-medium">
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                          Atıf Bulundu
                        </div>
                        
                        <!-- Citation & Reference Info Cards -->
                        <div class="flex gap-2 mt-1">
                          <!-- Citation Card -->
                          <div class="flex-1 bg-blue-50 border border-blue-100 rounded px-2 py-1.5">
                            <div class="text-[10px] text-blue-600 font-medium mb-0.5 flex items-center gap-1">
                              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                              Atıf
                            </div>
                            <div class="text-xs text-gray-700">
                              <span class="font-semibold">Sayfa:</span> 
                              {{ article.citation_pages?.join(', ') || article.citation_page || '-' }}
                            </div>
                            <div class="text-[10px] text-gray-500">
                              {{ article.citation_pages?.length || 1 }} adet
                            </div>
                          </div>
                          
                          <!-- Reference Card -->
                          <div class="flex-1 bg-purple-50 border border-purple-100 rounded px-2 py-1.5">
                            <div class="text-[10px] text-purple-600 font-medium mb-0.5 flex items-center gap-1">
                              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                              Referans
                            </div>
                            <div class="text-xs text-gray-700">
                              <span class="font-semibold">Sayfa:</span> {{ article.reference_page || '-' }}
                            </div>
                            <div class="text-[10px] text-gray-500">
                              <span class="font-semibold">#</span>{{ article.reference_number || '-' }}
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <!-- Not Found State -->
                      <div v-else-if="article.citation_status === 'not_found'" class="inline-flex items-center gap-1 text-red-600 bg-red-50 px-2 py-0.5 rounded-full">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                        <span class="font-medium">Bulunamadı</span>
                      </div>
                      
                      <!-- Checking State -->
                      <div v-else class="text-orange-500 flex items-center gap-1">
                        <svg class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Aranıyor...
                      </div>
                    </div>
                  </td>
                  <td class="text-center">
                    <!-- Fully Complete (PDF + Cover) -->
                    <span v-if="isArticleComplete(article)" 
                          class="inline-flex items-center gap-1 text-green-700 bg-green-50 px-1.5 py-0.5 rounded text-[9px]" 
                          title="Tamamlandı">
                      ✓ Tamam
                    </span>
                    <!-- PDF Missing -->
                    <span v-else-if="!article.pdf_path" 
                          class="inline-flex items-center gap-1 text-red-600 bg-red-50 px-1.5 py-0.5 rounded text-[9px]" 
                          title="PDF eşleşmesi yapılmadı">
                      PDF Eksik
                    </span>
                    <!-- PDF Found but Cover Missing -->
                    <span v-else-if="!article.cover_pages || article.cover_pages.length === 0" 
                          class="inline-flex items-center gap-1 text-orange-600 bg-orange-50 px-1.5 py-0.5 rounded text-[9px]" 
                          title="Ünvan sayfası yükleyin">
                      Kapak Eksik
                    </span>
                    <!-- Other states (shouldn't happen) -->
                    <span v-else 
                          class="inline-block w-3 h-3 bg-[#bc5f68] rounded-full ring-2 ring-red-100" 
                          title="Eksik"></span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Action Buttons -->
        <div v-if="articles.length > 0" class="flex items-center justify-between mt-4">
          <NuxtLink to="/panel/import" class="btn-gray flex items-center gap-1">
            ← Geri
          </NuxtLink>
          <button 
            @click="saveAndContinue" 
            :disabled="!canContinue"
            class="btn-green flex items-center gap-1"
            :class="{ 'opacity-50 cursor-not-allowed': !canContinue }"
          >
            <span>Devam Et →</span>
          </button>
        </div>

        <!-- Warning if incomplete -->
        <div v-if="articles.length > 0 && !canContinue" class="alert-warning mt-4">
          <p class="text-sm">
            <strong>Dikkat:</strong> Devam etmek için tüm makalelerin PDF ve en az 1 kapak sayfası yüklenmesi zorunludur.
          </p>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface UploadedFile {
  name: string;
  file: File;
}

const articles = ref<any[]>([])
const uploadedFiles = ref<UploadedFile[]>([])
const bulkInput = ref<HTMLInputElement | null>(null)
const sourceArticle = ref<any>(null)
const isDragging = ref(false)
const uploadingFiles = ref<string[]>([])

const completedCount = computed(() => articles.value.filter(a => isArticleComplete(a)).length)
const canContinue = computed(() => articles.value.length > 0 && articles.value.every(a => isArticleComplete(a)))

const isArticleComplete = (article: any) => {
  return article.pdf_path && article.cover_pages?.length > 0
}

// Format authors for display
const formatAuthors = (authors: string[] | undefined): string => {
  if (!authors || authors.length === 0) return ''
  if (authors.length <= 2) return authors.join(', ')
  return `${authors.slice(0, 2).join(', ')} et al.`
}

// Extract just the filename from a path
const getFilename = (path: string): string => {
  if (!path) return ''
  // Handle both Windows and Unix paths
  const parts = path.replace(/\\/g, '/').split('/')
  return parts[parts.length - 1] || path
}

onMounted(async () => {
  // Try loading from server session first (single source of truth)
  try {
    const sessionData = await $fetch('/api/session-get')
    
    if (sessionData.success && sessionData.citing_articles?.length > 0) {
      articles.value = sessionData.citing_articles.map((a: any) => {
        // Auto-detect status based on existing citation data
        let status = a.citation_status || 'pending'
        if (a.citation_pages?.length > 0) {
          status = 'found'
        } else if (a.pdf_path && status === 'pending') {
          status = 'not_found'
        }
        
        // Convert cover_pages_all (server format) to cover_pages (UI format)
        let coverPages = a.cover_pages || []
        if ((!coverPages || coverPages.length === 0) && a.cover_pages_all?.length > 0) {
          coverPages = a.cover_pages_all.map((path: string, idx: number) => ({
            name: `Kapak ${idx + 1}`,
            path: path
          }))
        }
        
        return {
          ...a,
          cover_pages: coverPages,
          citation_status: status
        }
      })
      console.log("Loaded articles from server session:", articles.value.length)
    }
    
    // Get source article from session
    if (sessionData.success && sessionData.source_article) {
      sourceArticle.value = sessionData.source_article
      console.log("Loaded Source Article:", sourceArticle.value)
    } else {
      console.warn("No source article found in session data")
    }
  } catch (e) {
    console.error("Failed to fetch session data:", e)
  }

  // Restore file list display
  const usedPaths = articles.value.map(a => a.pdf_path).filter(Boolean)
  uploadedFiles.value = usedPaths.map(path => ({ name: path, file: null as any }))
})

// Bulk Upload Logic
const handleBulkDrop = (e: DragEvent) => {
  isDragging.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  processFiles(files)
}

const handleBulkUpload = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = Array.from(target.files || [])
  processFiles(files)
  if (target) target.value = ''
}

const processFiles = async (files: File[]) => {
  let matchedCount = 0
  
  for (const file of files) {
    // Add to uploaded list if not exists
    if (!uploadedFiles.value.some(f => f.name === file.name)) {
      uploadedFiles.value.push({ name: file.name, file: file })
    }

    // Matching Logic
    const filename = file.name.toLowerCase()
    
    // 1. Try matching by DOI (Robust)
    let matchedArticle = articles.value.find(a => {
      if (!a.doi) return false
      const cleanDoi = a.doi.toLowerCase()
      const doiSlug = cleanDoi.replace(/\//g, '_')
      const doiSlug2 = cleanDoi.replace(/\//g, '-')
      
      // Check full DOI variations
      if (filename.includes(doiSlug) || filename.includes(doiSlug2)) return true
      
      // Check DOI Suffix only (after last slash)
      if (cleanDoi.includes('/')) {
          const suffix = cleanDoi.split('/').pop()
          if (suffix && filename.includes(suffix)) return true
      }
      return false
    })

    // 2. Try matching by Title (Fuzzy)
    if (!matchedArticle) {
      matchedArticle = articles.value.find(a => {
        const titleWords = a.title.toLowerCase().replace(/[^a-z0-9]/g, ' ').split(' ').filter((w: string) => w.length > 3)
        if (titleWords.length < 2) return false
        
        // Count how many significant title words appear in the filename
        const matchCount = titleWords.reduce((acc: number, word: string) => acc + (filename.includes(word) ? 1 : 0), 0)
        // Require at least 3 words match or 50% of words if title is short
        return matchCount >= Math.min(3, Math.ceil(titleWords.length * 0.5))
      })
    }

    if (matchedArticle) {
      matchedArticle.pdf_path = file.name
      // Reset ALL old citation data to force fresh check
      matchedArticle.citation_status = 'checking'
      matchedArticle.citation_pages = []
      matchedArticle.citation_page = null
      matchedArticle.reference_page = null
      matchedArticle.reference_number = null
      matchedCount++
      saveArticles()

      // Perform Real Upload & Check
      await checkCitation(file, matchedArticle)
    }
  }
}

const checkCitation = async (file: File, article: any) => {
    if (!file) return // Can't check if we just restored state without file object

    // Prepare form data
    const formData = new FormData()
    formData.append('file', file)
    
    // Get source article from multiple sources (API, localStorage, or defaults)
    let srcDoi = sourceArticle.value?.doi || ""
    let srcAuthors = sourceArticle.value?.authors || []
    let srcYear = sourceArticle.value?.year || 2024
    let srcTitle = sourceArticle.value?.title || ""
    
    // Fallback to localStorage if session-data not available
    if (!srcDoi) {
        const candidateInfo = localStorage.getItem('candidateInfo')
        if (candidateInfo) {
            try {
                const info = JSON.parse(candidateInfo)
                srcDoi = info.doi || ""
                srcAuthors = info.firstAuthorSurname ? [info.firstAuthorSurname] : []
                srcYear = info.year || 2024
                srcTitle = info.articleTitle || ""
            } catch (e) {}
        }
    }
    
    // Combine Source Article (Candidate) and Citing Article info
    const checkData = {
        title: article.title,
        doi: article.doi,
        source_title: srcTitle,
        source_doi: srcDoi,
        source_authors: srcAuthors.length > 0 ? srcAuthors : ["Gul"],
        source_year: srcYear
    }
    formData.append('data', JSON.stringify(checkData))

    try {
        const { data } = await useFetch('/api/check-pdf', {
            method: 'POST',
            body: formData
        })
        
        if (data.value && data.value.success) {
            if (data.value.found) {
                article.citation_status = 'found'
                article.citation_pages = data.value.citation_pages || []
                article.citation_bboxes = data.value.citation_bboxes || []
                article.reference_page = data.value.reference_page
                article.reference_number = data.value.reference_number
                article.reference_bbox = data.value.reference_bbox || null
            } else {
                article.citation_status = 'not_found'
            }
        } else {
            console.error("Check failed:", data.value?.message)
            article.citation_status = 'error'
        }
    } catch (e) {
        console.error("API Error:", e)
        article.citation_status = 'error'
    }
    saveArticles()
}

const removeUploadedFile = (filename: string) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.name !== filename)
  
  articles.value.forEach(article => {
    if (article.pdf_path === filename) {
      article.pdf_path = null
      article.citation_status = null
    }
  })
  saveArticles()
}

const unlinkPdf = (index: number) => {
  articles.value[index].pdf_path = null
  articles.value[index].citation_status = null
  saveArticles()
}

const handleCoverUpload = async (e: Event, index: number) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]!
    const article = articles.value[index]
    
    if (!article.cover_pages) {
      article.cover_pages = []
    }
    
    const coverIndex = article.cover_pages.length
    
    // Upload to server
    const formData = new FormData()
    formData.append('file', file)
    formData.append('doi', article.doi || '')
    formData.append('index', String(index))
    formData.append('coverIndex', String(coverIndex))
    
    try {
      const response = await $fetch<{ success: boolean; path?: string; message?: string }>('/api/upload-cover', {
        method: 'POST',
        body: formData
      })
      
      if (response.success && response.path) {
        article.cover_pages.push({
          name: file.name,
          path: response.path
        })
        saveArticles()
      } else {
        console.error('Cover upload failed:', response.message || 'Unknown error')
      }
    } catch (err) {
      console.error('Cover upload error:', err)
      // Fallback - still add to UI even if upload fails
      article.cover_pages.push({
        name: file.name,
        file: file
      })
      saveArticles()
    }
  }
}

const removeCover = (articleIndex: number, coverIndex: number) => {
  articles.value[articleIndex].cover_pages.splice(coverIndex, 1)
  saveArticles()
}

const saveArticles = async () => {
  const toSave = articles.value.map(a => {
    // Exclude large objects or temporary states if needed
    const { pdf_file, ...rest } = a
    return rest
  })
  
  // Sync to server session only (user-specific)
  try {
    await $fetch('/api/session-save', {
      method: 'POST',
      body: { citing_articles: toSave }
    })
  } catch (e) {
    console.error('Failed to sync articles to server:', e)
  }
}

const saveAndContinue = () => {
  if (!canContinue.value) return
  saveArticles()
  navigateTo('/panel/generate')
}
</script>
