<template>
  <div class="min-h-screen bg-[#f7f7f7] flex flex-col">
    <!-- Simple Header -->
    <!-- Header -->
    <header class="bg-[#af5760] text-white py-4 px-6">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <NuxtLink to="/" class="flex items-center gap-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <div>
            <h1 class="text-lg font-bold">Doçentlik Atıf Dosyası Oluşturucu</h1>
            <p class="text-xs opacity-80">Akademisyenler için profesyonel atıf belgesi hazırlama aracı</p>
          </div>
        </NuxtLink>
        
        <NuxtLink to="/" class="text-sm font-medium hover:text-white/80 transition-colors flex items-center gap-1 opacity-80 hover:opacity-100">
           Ana Sayfa
        </NuxtLink>
      </div>
    </header>

    <!-- Content -->
    <main class="flex-1 flex items-center justify-center p-6">
      <div class="w-full max-w-xl">
        <slot />
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-6 text-center text-[#7c7c7c] text-xs border-t border-[#d0d0d0] bg-white">
      <p>Doçentlik Atıf Dosyası Oluşturucu - 2026</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Auth Layout
</script>
