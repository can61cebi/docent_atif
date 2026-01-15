<template>
  <div class="min-h-screen bg-[#f7f7f7]">
    <!-- Header -->
    <header class="bg-[#af5760] text-white py-4 px-6">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <div>
            <h1 class="text-lg font-bold">Doçentlik Atıf Dosyası Oluşturucu</h1>
            <p class="text-xs opacity-80">Akademisyenler için profesyonel atıf belgesi hazırlama aracı</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <NuxtLink to="/login" class="px-4 py-2 text-sm font-medium hover:bg-white/10 transition-colors">
            Giriş Yap
          </NuxtLink>
          <NuxtLink to="/register" class="px-4 py-2 bg-white text-[#af5760] text-sm font-medium hover:bg-gray-100 transition-colors">
            Kayıt Ol
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="bg-[#e8e8e8] py-16 border-b border-[#d0d0d0]">
      <div class="max-w-4xl mx-auto text-center px-6">
        <h2 class="text-3xl font-bold text-[#30302f] mb-4">
          Doçentlik Başvurunuz İçin<br>Profesyonel Atıf Dosyası
        </h2>
        <p class="text-[#7c7c7c] text-lg mb-8 max-w-2xl mx-auto">
          YÖK formatına uygun, A.1-A.4 bölümlerini içeren eksiksiz atıf dosyaları oluşturun. 
          Web of Science verilerinizi yükleyin, PDF'lerinizi ekleyin ve profesyonel belgenizi indirin.
        </p>
        <NuxtLink to="/register" class="inline-block px-8 py-3 bg-[#5eab8c] text-white font-medium hover:bg-[#4d9a7a] transition-colors">
          Hemen Başlayın
        </NuxtLink>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 px-6">
      <div class="max-w-6xl mx-auto">
        <h3 class="text-2xl font-bold text-[#30302f] text-center mb-12">Nasıl Çalışır?</h3>
        
        <div class="grid md:grid-cols-4 gap-6">
          <!-- Step 1 -->
          <div class="bg-white border border-[#d0d0d0] p-6">
            <div class="w-10 h-10 bg-[#af5760] text-white flex items-center justify-center font-bold mb-4">1</div>
            <h4 class="font-bold text-[#30302f] mb-2">Bilgilerinizi Girin</h4>
            <p class="text-sm text-[#7c7c7c]">
              Ad, kurum, bölüm ve kaynak makale bilgilerinizi sisteme kaydedin.
            </p>
          </div>

          <!-- Step 2 -->
          <div class="bg-white border border-[#d0d0d0] p-6">
            <div class="w-10 h-10 bg-[#af5760] text-white flex items-center justify-center font-bold mb-4">2</div>
            <h4 class="font-bold text-[#30302f] mb-2">WoS Dosyası Yükleyin</h4>
            <p class="text-sm text-[#7c7c7c]">
              Web of Science'tan export ettiğiniz savedrecs.txt dosyasını yükleyin.
            </p>
          </div>

          <!-- Step 3 -->
          <div class="bg-white border border-[#d0d0d0] p-6">
            <div class="w-10 h-10 bg-[#af5760] text-white flex items-center justify-center font-bold mb-4">3</div>
            <h4 class="font-bold text-[#30302f] mb-2">PDF ve Kapak Yükleyin</h4>
            <p class="text-sm text-[#7c7c7c]">
              Her makale için tam metin PDF'i ve zorunlu kapak sayfasını yükleyin.
            </p>
          </div>

          <!-- Step 4 -->
          <div class="bg-white border border-[#d0d0d0] p-6">
            <div class="w-10 h-10 bg-[#af5760] text-white flex items-center justify-center font-bold mb-4">4</div>
            <h4 class="font-bold text-[#30302f] mb-2">Belgenizi İndirin</h4>
            <p class="text-sm text-[#7c7c7c]">
              A.1-A.4 formatında hazırlanmış, sarı işaretli profesyonel PDF'inizi indirin.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Document Structure Section -->
    <section class="py-16 px-6 bg-white border-y border-[#d0d0d0]">
      <div class="max-w-4xl mx-auto">
        <h3 class="text-2xl font-bold text-[#30302f] text-center mb-8">Oluşturulan Doküman Yapısı</h3>
        
        <div class="bg-[#f9f9f9] border border-[#d0d0d0] p-6">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-[#d0d0d0]">
                <th class="text-left py-2 text-[#30302f]">Bölüm</th>
                <th class="text-left py-2 text-[#30302f]">İçerik</th>
                <th class="text-left py-2 text-[#30302f]">Zorunlu</th>
              </tr>
            </thead>
            <tbody>
              <tr class="border-b border-[#d0d0d0]">
                <td class="py-2 font-medium text-[#ae5961]">A.1</td>
                <td class="py-2 text-[#7c7c7c]">Yayının Ünvan Sayfası (dergi kapağı)</td>
                <td class="py-2 text-[#5eab8c]">Evet</td>
              </tr>
              <tr class="border-b border-[#d0d0d0]">
                <td class="py-2 font-medium text-[#ae5961]">A.2</td>
                <td class="py-2 text-[#7c7c7c]">Eserin Başlık Sayfası</td>
                <td class="py-2 text-[#5eab8c]">Evet</td>
              </tr>
              <tr class="border-b border-[#d0d0d0]">
                <td class="py-2 font-medium text-[#ae5961]">A.3</td>
                <td class="py-2 text-[#7c7c7c]">İlk atıf yapılan sayfa (sarı işaretli)</td>
                <td class="py-2 text-[#5eab8c]">Evet</td>
              </tr>
              <tr>
                <td class="py-2 font-medium text-[#ae5961]">A.4</td>
                <td class="py-2 text-[#7c7c7c]">Kaynakça Sayfası (referans sarı işaretli)</td>
                <td class="py-2 text-[#5eab8c]">Evet</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 px-6 bg-[#af5760] text-white">
      <div class="max-w-4xl mx-auto text-center">
        <h3 class="text-2xl font-bold mb-4">Hemen Başlayın</h3>
        <p class="opacity-80 mb-8">Ücretsiz hesap oluşturun ve doçentlik başvurunuz için profesyonel atıf dosyanızı hazırlayın.</p>
        <div class="flex items-center justify-center gap-4">
          <NuxtLink to="/register" class="px-8 py-3 bg-white text-[#af5760] font-medium hover:bg-gray-100 transition-colors">
            Kayıt Ol
          </NuxtLink>
          <NuxtLink to="/login" class="px-8 py-3 border border-white text-white font-medium hover:bg-white/10 transition-colors">
            Giriş Yap
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="py-6 px-6 bg-[#30302f] text-white/60 text-xs text-center">
      <p>Doçentlik Atıf Dosyası Oluşturucu - 2026 © Tüm hakları saklıdır</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

// Client-side only redirect check
onMounted(() => {
  const { isLoggedIn } = useAuth()
  if (isLoggedIn.value) {
    navigateTo('/panel')
  }
})
</script>
