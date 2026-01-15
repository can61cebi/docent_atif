<template>
  <NuxtLayout name="panel">
    <div>
      <!-- Page Title -->
      <div class="mb-4">
        <h1 class="text-base font-medium text-[#30302f]">Doküman Arşivi</h1>
      </div>

      <!-- No Documents -->
      <div v-if="documents.length === 0" class="x-panel">
        <div class="x-content text-center py-8">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-[#d0d0d0] mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-sm text-[#7c7c7c] mb-4">Henüz oluşturulmuş doküman yok.</p>
          <NuxtLink to="/panel" class="btn-green">
            Yeni Doküman Oluştur
          </NuxtLink>
        </div>
      </div>

      <!-- Documents List -->
      <div v-else class="x-panel">
        <div class="x-title flex items-center justify-between">
          <h2>Oluşturulan Dokümanlar ({{ documents.length }})</h2>
          <NuxtLink to="/panel" class="btn-red text-xs">+ Yeni</NuxtLink>
        </div>
        <div class="x-content p-0">
          <table class="data-table">
            <thead>
              <tr>
                <th class="w-12">#</th>
                <th>Makale Başlığı</th>
                <th class="w-20">Atıf</th>
                <th class="w-32">Tarih</th>
                <th class="w-48 text-right">Dosyalar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(doc, index) in documents" :key="doc.id">
                <td class="text-center">{{ index + 1 }}</td>
                <td class="text-xs">
                  <div class="font-medium text-[#30302f]">{{ doc.articleTitle || 'İsimsiz' }}</div>
                </td>
                <td class="text-center">{{ doc.citationCount }}</td>
                <td class="text-xs">{{ formatDate(doc.createdAt) }}</td>
                <td class="text-right">
                  <div class="flex items-center justify-end gap-2">
                    <a 
                      v-if="doc.files?.final_pdf"
                      :href="`/api/download?path=${encodeURIComponent(doc.files.final_pdf)}`"
                      class="btn-gray text-[10px] py-1 px-2 flex items-center gap-1"
                      title="Final PDF İndir"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
                      PDF
                    </a>
                    <a 
                      v-if="doc.files?.excel"
                      :href="`/api/download?path=${encodeURIComponent(doc.files.excel)}`"
                      class="btn-gray text-[10px] py-1 px-2 flex items-center gap-1"
                      title="Excel Rapor İndir"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                      Excel
                    </a>
                    
                    <button 
                         @click="openDeleteModal(doc)"
                         class="btn-red text-[10px] py-1 px-2 flex items-center gap-1 ml-2"
                         title="Sil"
                    >
                         <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                         </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Confirm Modal -->
      <ConfirmModal
        :show="showDeleteModal"
        type="danger"
        title="Dokümanı Sil"
        message="Bu dokümanı ve ilgili dosyalarını silmek istediğinize emin misiniz? Bu işlem geri alınamaz."
        confirm-text="Sil"
        @confirm="confirmDelete"
        @cancel="showDeleteModal = false"
      />
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

// Define document type
interface Document {
  id: string
  articleTitle: string
  citationCount: string | number
  createdAt: string
  files: {
    final_pdf: string | null
    excel: string | null
  }
}

const documents = ref<Document[]>([])
const showDeleteModal = ref(false)
const docToDelete = ref<Document | null>(null)

// Fetch documents from server API
const { data, refresh } = await useFetch<Document[]>('/api/documents')

onMounted(() => {
  if (data.value) {
    documents.value = data.value
  }
})

// Listen to refresh events (if any)
onNuxtReady(() => {
    refresh()
})

const formatDate = (isoString: string) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const openDeleteModal = (doc: Document) => {
    docToDelete.value = doc
    showDeleteModal.value = true
}

const confirmDelete = async () => {
    if (!docToDelete.value) return
    
    try {
        await $fetch('/api/delete-document', {
            method: 'POST',
            body: {
                id: docToDelete.value.id
            }
        })
        
        // Remove from list
        documents.value = documents.value.filter(d => d.id !== docToDelete.value?.id)
        showDeleteModal.value = false
        docToDelete.value = null
        
    } catch (e) {
        alert('Silme işlemi başarısız oldu.')
        console.error(e)
    }
}
</script>
