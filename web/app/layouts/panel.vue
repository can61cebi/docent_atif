<template>
  <div class="min-h-screen flex bg-[#f7f7f7]">
    <!-- Left Sidebar -->
    <aside class="w-[230px] bg-[#e8e8e8] min-h-screen fixed left-0 top-0 flex flex-col border-r border-[#d0d0d0]">
      <!-- Header with Logo -->
      <div class="bg-[#af5760] px-4 py-3 flex items-center gap-2">
        <button class="text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span class="text-white text-sm font-medium">DOÇENTLİK DOSYASI</span>
      </div>

      <!-- Profile Section -->
      <div class="p-4 border-b border-[#d0d0d0]">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-[#d0d0d0] flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-[#7c7c7c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <p class="text-[#7c7c7c] text-xs uppercase">Aday</p>
            <ClientOnly>
              <h2 class="text-[#30302f] font-medium text-sm">{{ user?.name || 'Kullanıcı' }}</h2>
              <template #fallback>
                <h2 class="text-[#30302f] font-medium text-sm">&nbsp;</h2>
              </template>
            </ClientOnly>
          </div>
        </div>
      </div>

      <!-- Navigation Menu -->
      <nav class="flex-1 py-2">
        <ul>
          <li>
            <NuxtLink 
              to="/panel" 
              class="flex items-center gap-3 px-4 py-3 text-[#ae5961] hover:bg-[#f0f0f0] transition-colors border-l-4"
              :class="$route.path === '/panel' ? 'bg-white border-[#ae5961]' : 'border-transparent'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span class="text-sm font-medium">Kişisel Bilgiler</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink 
              to="/panel/import" 
              class="flex items-center gap-3 px-4 py-3 text-[#ae5961] hover:bg-[#f0f0f0] transition-colors border-l-4"
              :class="$route.path === '/panel/import' ? 'bg-white border-[#ae5961]' : 'border-transparent'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <span class="text-sm font-medium">WoS İçe Aktar</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink 
              to="/panel/pdfs" 
              class="flex items-center gap-3 px-4 py-3 text-[#ae5961] hover:bg-[#f0f0f0] transition-colors border-l-4"
              :class="$route.path === '/panel/pdfs' ? 'bg-white border-[#ae5961]' : 'border-transparent'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <span class="text-sm font-medium">PDF Dosyaları</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink 
              to="/panel/generate" 
              class="flex items-center gap-3 px-4 py-3 text-[#ae5961] hover:bg-[#f0f0f0] transition-colors border-l-4"
              :class="$route.path === '/panel/generate' ? 'bg-white border-[#ae5961]' : 'border-transparent'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span class="text-sm font-medium">Doküman Oluştur</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink 
              to="/panel/documents" 
              class="flex items-center gap-3 px-4 py-3 text-[#ae5961] hover:bg-[#f0f0f0] transition-colors border-l-4"
              :class="$route.path === '/panel/documents' ? 'bg-white border-[#ae5961]' : 'border-transparent'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
              <span class="text-sm font-medium">Doküman Arşivi</span>
            </NuxtLink>
          </li>
        </ul>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-3 border-t border-[#d0d0d0] flex items-center justify-between">
        <NuxtLink to="/" class="text-[#7c7c7c] hover:text-[#ae5961] transition-colors text-xs">
          Ana Sayfa
        </NuxtLink>
        <button @click="handleLogout" class="text-xs text-[#bc5f68] hover:underline">Çıkış</button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="ml-[230px] flex-1 flex flex-col min-h-screen">
      <!-- Top Navigation -->
      <header class="bg-white border-b border-[#d0d0d0] px-5 py-3 sticky top-0 z-40">
        <div class="flex items-center justify-between">
          <div class="text-[#30302f] text-sm font-medium">
            Doçentlik Atıf Dosyası
          </div>
          
          <div class="flex items-center gap-2">
            <ClientOnly>
              <span class="text-sm text-[#30302f]">{{ user?.name }}</span>
            </ClientOnly>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 p-5">
        <slot />
      </main>

      <!-- Footer -->
      <footer class="bg-white border-t border-[#d0d0d0] py-3 px-5">
        <div class="text-center text-[#7c7c7c] text-xs">
          Doçentlik Atıf Dosyası Oluşturucu - 2026
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
const { user, logout } = useAuth()

const handleLogout = () => {
  logout()
  navigateTo('/')
}
</script>
