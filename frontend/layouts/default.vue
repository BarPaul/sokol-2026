<template>
  <div class="flex min-h-screen flex-col">
    <header class="border-b border-slate-200 bg-white">
      <div class="container-sf flex h-16 items-center justify-between">
        <NuxtLink to="/" class="flex items-center gap-2">
          <span class="text-xl font-bold tracking-tight text-slate-900">СтудСемья</span>
        </NuxtLink>
        <nav class="hidden items-center gap-6 md:flex">
          <NuxtLink to="/" class="text-sm font-medium text-slate-600 hover:text-teal-700">Главная</NuxtLink>
          <NuxtLink to="/articles" class="text-sm font-medium text-slate-600 hover:text-teal-700">Статьи</NuxtLink>
          <NuxtLink to="/search" class="text-sm font-medium text-slate-600 hover:text-teal-700">Поиск</NuxtLink>
          <NuxtLink to="/assistant" class="text-sm font-medium text-slate-600 hover:text-teal-700">AI-помощник</NuxtLink>
          <template v-if="isAuthed">
            <NuxtLink
              :to="panelPath"
              class="rounded-lg border border-teal-200 px-3 py-1.5 text-sm font-medium text-teal-700 hover:bg-teal-50"
            >
              {{ isAdmin ? 'Панель админист.' : 'Кабинет редактора' }}
            </NuxtLink>
            <button
              class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
              @click="logout"
            >
              Выйти
            </button>
          </template>
          <NuxtLink v-else to="/login" class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
            Войти
          </NuxtLink>
        </nav>
        <button class="rounded-lg p-2 text-slate-600 md:hidden" aria-label="Меню" @click="mobileOpen = !mobileOpen">
          <Icon name="heroicons:bars-3" class="h-6 w-6" />
        </button>
      </div>
      <div v-if="mobileOpen" class="border-t border-slate-200 bg-white p-4 md:hidden">
        <nav class="flex flex-col gap-3">
          <NuxtLink to="/" class="text-sm font-medium text-slate-700" @click="mobileOpen = false">Главная</NuxtLink>
          <NuxtLink to="/articles" class="text-sm font-medium text-slate-700" @click="mobileOpen = false">Статьи</NuxtLink>
          <NuxtLink to="/search" class="text-sm font-medium text-slate-700" @click="mobileOpen = false">Поиск</NuxtLink>
          <NuxtLink to="/assistant" class="text-sm font-medium text-slate-700" @click="mobileOpen = false">AI-помощник</NuxtLink>
          <template v-if="isAuthed">
            <NuxtLink :to="panelPath" class="text-sm font-medium text-teal-700" @click="mobileOpen = false">
              {{ isAdmin ? 'Панель админист.' : 'Кабинет редактора' }}
            </NuxtLink>
            <button class="text-sm font-medium text-slate-700" @click="logout">Выйти</button>
          </template>
          <NuxtLink v-else to="/login" class="text-sm font-medium text-teal-700" @click="mobileOpen = false">Войти</NuxtLink>
        </nav>
      </div>
    </header>

    <main class="flex-1">
      <slot />
    </main>

    <footer class="mt-12 border-t border-slate-200 bg-white">
      <div class="container-sf py-8">
        <div class="grid gap-6 md:grid-cols-3">
          <div>
            <p class="font-semibold text-slate-900">СтудСемья</p>
            <p class="mt-2 text-sm text-slate-500">Информационный портал о поддержке студенческих семей.</p>
          </div>
          <div>
            <p class="text-sm font-medium text-slate-900">Разделы</p>
            <div class="mt-2 flex flex-col gap-1.5 text-sm text-slate-600">
              <NuxtLink to="/articles" class="hover:text-teal-700">Статьи</NuxtLink>
              <NuxtLink to="/search" class="hover:text-teal-700">Поиск</NuxtLink>
              <NuxtLink to="/assistant" class="hover:text-teal-700">AI-помощник</NuxtLink>
            </div>
          </div>
          <div>
            <p class="text-sm text-slate-500">Информация на сайте носит справочный характер и не заменяет консультацию юриста.</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const mobileOpen = ref(false)

const { token, logout } = useApi()
const role = computed(() =>
  token.value && import.meta.client ? localStorage.getItem('sf_role') : null,
)
const isAuthed = computed(() => Boolean(token.value))
const isAdmin = computed(() => role.value === 'moderator')
const panelPath = computed(() => (role.value === 'moderator' ? '/admin' : '/editor'))
</script>