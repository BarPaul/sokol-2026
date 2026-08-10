<template>
  <div class="flex min-h-screen bg-slate-50">
    <aside class="hidden w-64 shrink-0 border-r border-slate-200 bg-white md:flex md:flex-col">
      <div class="flex h-16 items-center gap-2 border-b border-slate-200 px-5">
        <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-700 text-white">А</span>
        <span class="font-semibold text-slate-900">Панель админист.</span>
      </div>
      <nav class="flex flex-1 flex-col gap-1 p-4">
        <NuxtLink to="/admin" class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-800">Дашборд</NuxtLink>
        <NuxtLink to="/admin/editors" class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-800">Редакторы</NuxtLink>
        <NuxtLink to="/admin/logs" class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-800">Журнал действий</NuxtLink>
        <NuxtLink to="/admin/ai" class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-800">Настройки AI</NuxtLink>
        <NuxtLink to="/admin/knowledge" class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-800">База знаний</NuxtLink>
        <NuxtLink to="/admin/profile" class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-800">Профиль</NuxtLink>
      </nav>
      <div class="p-4">
        <button class="btn-secondary w-full" @click="logout">Выйти</button>
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
          <NuxtLink to="/admin" @click="mobileOpen = false">Дашборд</NuxtLink>
          <NuxtLink to="/admin/editors" @click="mobileOpen = false">Редакторы</NuxtLink>
          <NuxtLink to="/admin/logs" @click="mobileOpen = false">Журнал</NuxtLink>
          <NuxtLink to="/admin/ai" @click="mobileOpen = false">Настройки AI</NuxtLink>
          <NuxtLink to="/admin/knowledge" @click="mobileOpen = false">База знаний</NuxtLink>
          <NuxtLink to="/admin/profile" @click="mobileOpen = false">Профиль</NuxtLink>
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

definePageMeta({ layout: 'admin' })
</script>