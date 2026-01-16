<template>
  <NuxtLayout name="panel">
    <div>
      <!-- Page Title -->
      <div class="mb-4">
        <h1 class="text-base font-medium text-[#30302f]">WoS İçe Aktar</h1>
      </div>

      <!-- Upload Panel -->
      <div class="x-panel">
        <div class="x-title flex items-center justify-between">
          <h2>Web of Science Export Dosyası</h2>
        </div>
        <div class="x-content">
          <!-- Help Box -->
          <div class="alert-info mb-4">
            <p class="text-sm">
              <strong>Nasıl export alınır?</strong><br>
              1. Web of Science'ta makalenizi arayın<br>
              2. "Cited References" bölümüne gidin<br>
              3. Tüm atıfları seçin ve "Export" → "Plain Text" seçin<br>
              4. savedrecs.txt dosyasını buraya yükleyin
            </p>
          </div>

          <!-- File Upload Area -->
          <div 
            :class="[
              'border-2 border-dashed p-8 text-center cursor-pointer transition-all',
              isDragging 
                ? 'border-blue-500 bg-blue-50 scale-[1.02] shadow-lg' 
                : 'border-[#d0d0d0] hover:border-[#ae5961]'
            ]"
            @drop.prevent="handleDrop"
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            @click="$refs.fileInput.click()"
          >
            <input 
              ref="fileInput"
              type="file" 
              accept=".txt"
              class="hidden"
              @change="handleFileSelect"
            />
            
            <!-- Drag Active State -->
            <template v-if="isDragging">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-blue-500 mb-3 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
              <p class="text-sm text-blue-700 font-medium">
                Dosyayı buraya bırakın!
              </p>
            </template>
            
            <!-- Default State -->
            <template v-else>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-[#7c7c7c] mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="text-sm text-[#30302f] mb-1">
                <strong>savedrecs.txt</strong> dosyasını sürükleyin veya tıklayın
              </p>
            </template>
          </div>

          <!-- Selected File Info -->
          <div v-if="selectedFile" class="mt-4 p-3 bg-[#f5f5f5] border border-[#d0d0d0] flex items-center justify-between">
            <div class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[#5eab8c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-sm text-[#30302f]">{{ selectedFile.name }}</span>
            </div>
            <button @click="clearFile" class="text-[#bc5f68] hover:text-[#a85058]">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Parse Button -->
          <div class="mt-4 flex justify-end">
            <button 
              @click="parseFile"
              :disabled="!selectedFile || isProcessing"
              class="btn-green"
              :class="{ 'opacity-50 cursor-not-allowed': !selectedFile || isProcessing }"
            >
              {{ isProcessing ? 'İşleniyor...' : 'Dosyayı İşle' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Parsed Articles -->
      <div v-if="articles.length > 0" class="x-panel">
        <div class="x-title flex items-center justify-between">
          <h2>Bulunan Atıflar ({{ articles.length }})</h2>
          <button @click="saveAndContinue" class="btn-green text-xs">
            Kaydet ve Devam Et →
          </button>
        </div>
        <div class="x-content p-0">
          <table class="data-table">
            <thead>
              <tr>
                <th class="w-12">#</th>
                <th>Yayın Adı</th>
                <th class="w-48">Yazarlar</th>
                <th class="w-16">Yıl</th>
                <th class="w-32">Dergi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(article, index) in articles" :key="index">
                <td class="text-center">{{ index + 1 }}</td>
                <td class="text-xs">{{ article.title }}</td>
                <td class="text-xs text-gray-600">{{ formatAuthors(article.authors) }}</td>
                <td class="text-center">{{ article.year }}</td>
                <td class="text-xs">{{ article.journal }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const isProcessing = ref(false)
const articles = ref<any[]>([])

// Format authors for display
const formatAuthors = (authors: string[] | undefined): string => {
  if (!authors || authors.length === 0) return '-'
  if (authors.length <= 2) return authors.join(', ')
  return `${authors.slice(0, 2).join(', ')} et al.`
}

onMounted(async () => {
  // Load from server session only (user-specific)
  try {
    const sessionData = await $fetch('/api/session-get')
    if (sessionData.success && sessionData.citing_articles?.length > 0) {
      articles.value = sessionData.citing_articles
    }
  } catch (e) {
    console.error('Failed to load session:', e)
  }
})

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) selectedFile.value = files[0]
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) selectedFile.value = target.files[0]
}

const clearFile = () => { selectedFile.value = null; articles.value = [] }

const parseFile = async () => {
  if (!selectedFile.value) return
  isProcessing.value = true
  try {
    const text = await selectedFile.value.text()
    const parsed = parseWoSFile(text)
    articles.value = parsed
  } finally { isProcessing.value = false }
}

const parseWoSFile = (content: string): any[] => {
  const records: any[] = []
  const lines = content.split('\n')
  let currentRecord: Record<string, any> = {}
  let currentTag = ''
  
  // List fields that can have multiple entries
  const listFields = ['AU', 'AF', 'CR', 'C1']
  
  for (const line of lines) {
    const lineStripped = line.trimEnd()
    if (!lineStripped) continue
    
    let isTagLine = false
    let tag = ''
    let value = ''
    
    // Check for special end markers
    if (lineStripped === 'ER') {
      tag = 'ER'
      isTagLine = true
    } else if (lineStripped === 'EF') {
      tag = 'EF'
      isTagLine = true
    } else if (line.length >= 3 && /^[A-Z]{2}$/.test(line.substring(0, 2)) && line[2] === ' ') {
      // Standard tag line: "TI Title text..."
      tag = line.substring(0, 2)
      value = line.substring(3).trim()
      isTagLine = true
    }
    
    if (isTagLine) {
      currentTag = tag
      
      if (tag === 'ER') {
        // End of record - convert and save
        if (currentRecord.TI) {
          const article = convertWoSToArticle(currentRecord)
          if (article) records.push(article)
        }
        currentRecord = {}
        currentTag = ''
      } else if (tag === 'EF') {
        // End of file
        break
      } else if (['FN', 'VR'].includes(tag)) {
        // Skip file headers
      } else if (listFields.includes(tag)) {
        // List fields - create array and add first value
        if (!currentRecord[tag]) currentRecord[tag] = []
        if (value) currentRecord[tag].push(value)
      } else {
        // Regular field
        currentRecord[tag] = value
      }
    } else if (currentTag) {
      // Continuation line (no tag, follows previous line)
      value = line.trim()
      if (!value) continue
      
      if (listFields.includes(currentTag)) {
        currentRecord[currentTag].push(value)
      } else {
        // Append to existing text field
        currentRecord[currentTag] = (currentRecord[currentTag] || '') + ' ' + value
      }
    }
  }
  
  return records
}

// Convert WoS record to article object
const convertWoSToArticle = (data: Record<string, any>): any | null => {
  if (!data.TI) return null
  
  // Prefer AF (Author Full Name) over AU (Authors short)
  const authors = data.AF || data.AU || []
  
  // Parse year
  let year = 0
  if (data.PY) {
    const parsed = parseInt(data.PY)
    if (!isNaN(parsed)) year = parsed
  }
  
  // Build pages string
  let pages = ''
  if (data.BP && data.EP) {
    pages = `${data.BP}-${data.EP}`
  } else if (data.AR) {
    pages = data.AR
  }
  
  return {
    title: data.TI,
    authors: authors,
    journal: data.SO || data.SE || '',
    year: year,
    volume: data.VL || '',
    issue: data.IS || '',
    pages: pages,
    doi: data.DI || '',
    wos_id: (data.UT || '').replace('WOS:', ''),
    cover_pages: []
  }
}

const saveAndContinue = async () => {
  // Save to server session only (user-specific)
  try {
    await $fetch('/api/session-save', {
      method: 'POST',
      body: { citing_articles: articles.value }
    })
  } catch (e) {
    console.error('Failed to save to server:', e)
  }
  
  navigateTo('/panel/pdfs')
}
</script>
