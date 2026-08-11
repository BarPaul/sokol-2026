<template>
  <div class="flex min-h-screen bg-slate-50">
    <aside class="hidden w-64 shrink-0 border-r border-slate-200 bg-white md:flex md:flex-col">
      <div class="flex h-16 items-center gap-2 border-b border-slate-200 px-5">
        <NuxtLink to="/" class="flex items-center gap-2">
          <span class="font-semibold text-slate-900">Панель админист.</span>
        </NuxtLink>
      </div>
      <nav class="flex flex-1 flex-col gap-1 p-4">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="rounded-lg px-3 py-2 text-sm font-medium hover:bg-indigo-50 hover:text-indigo-800"
          :class="isActive(item.to) ? 'bg-indigo-50 text-indigo-800 font-semibold' : 'text-slate-600'"
        >
          {{ item.label }}
        </NuxtLink>
      </nav>
      <div class="flex flex-col gap-2 p-4">
        <NuxtLink to="/" class="btn-secondary w-full text-center">На главный сайт</NuxtLink>
        <button class="btn-primary w-full" @click="logout">Выйти</button>
      </div>
    </aside>

    <div class="flex min-h-screen flex-1 flex-col md:hidden">
      <div class="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4">
        <span class="font-semibold text-slate-900">Панель админист.</span>
        <button class="rounded-lg p-2 text-slate-600" aria-label="Меню" @click="mobileOpen = !mobileOpen">
          <Icon name="heroicons:bars-3" class="h-6 w-6" />
        </button>
      </div>
      <div v-if="mobileOpen" class="border-b border-slate-200 bg-white p-4">
        <nav class="flex flex-col gap-3">
          <NuxtLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="font-medium"
            :class="isActive(item.to) ? 'text-indigo-700' : 'text-slate-700'"
            @click="mobileOpen = false"
          >
            {{ item.label }}
          </NuxtLink>
          <NuxtLink to="/" class="text-teal-700 font-medium" @click="mobileOpen = false">На главный сайт</NuxtLink>
        </nav>
      </div>
    </div>

    <main class="flex-1 p-4 md:p-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const mobileOpen = ref(false)
const { logout } = useApi()
const route = useRoute()

const navItems = [
  { label: 'Дашборд', to: '/admin' },
  { label: 'Редакторы', to: '/admin/editors' },
  { label: 'Статьи', to: '/admin/articles' },
  { label: 'Журнал действий', to: '/admin/logs' },
  { label: 'Категории', to: '/admin/categories' },
  { label: 'Настройки AI', to: '/admin/ai' },
  { label: 'База знаний', to: '/admin/knowledge' },
  { label: 'Профиль', to: '/admin/profile' },
]

const isActive = (to: string) => {
  if (to === '/admin') return route.path === '/admin'
  return route.path.startsWith(to)
}

definePageMeta({ layout: 'admin' })
</script>