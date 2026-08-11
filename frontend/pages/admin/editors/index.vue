<template>
  <div class="mx-auto max-w-6xl">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-slate-900">Редакторы</h1>
      <NuxtLink to="/admin/editors/new" class="btn-primary">Создать редактора</NuxtLink>
    </div>

    <div class="mb-4">
      <input v-model="search" class="input-sf max-w-md" placeholder="Поиск по имени, email..." @input="debouncedLoad">
    </div>

    <div class="card-sf overflow-x-auto">
      <table class="w-full min-w-[700px] text-left text-sm">
        <thead>
          <tr class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
            <th class="pb-3 pr-4">Имя</th>
            <th class="pb-3 pr-4">Email</th>
            <th class="pb-3 pr-4">Роль</th>
            <th class="pb-3 pr-4">Статус</th>
            <th class="pb-3">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in editors" :key="e.id" class="border-b border-slate-100 last:border-0">
            <td class="py-3 pr-4 font-medium text-slate-800">
              <NuxtLink :to="`/admin/editors/${e.id}`" class="hover:text-teal-700 hover:underline">{{ e.first_name }} {{ e.last_name }}</NuxtLink>
            </td>
            <td class="py-3 pr-4 text-slate-500">{{ e.email }}</td>
            <td class="py-3 pr-4">{{ e.role }}</td>
            <td class="py-3 pr-4">
              <span class="rounded-full px-2 py-0.5 text-xs" :class="e.status === 'active' ? 'bg-teal-50 text-teal-700' : 'bg-red-50 text-red-600'">
                {{ e.status === 'active' ? 'Активен' : 'Деактивирован' }}
              </span>
            </td>
            <td class="py-3">
              <button v-if="e.status === 'active'" class="text-red-600 hover:underline" @click="toggle(e)">
                Деактивировать
              </button>
              <button v-else class="text-teal-700 hover:underline" @click="toggle(e)">Активировать</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EditorAccount } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { request } = useApi()

const editors = ref<EditorAccount[]>([])
const search = ref('')

async function load() {
  const params = search.value ? `?q=${encodeURIComponent(search.value)}` : ''
  editors.value = await request<EditorAccount[]>('/api/admin/editors' + params)
}

let timer: ReturnType<typeof setTimeout> | null = null
const debouncedLoad = () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 400)
}

async function toggle(e: EditorAccount) {
  await request(`/api/admin/editors/${e.id}`, {
    method: 'PATCH',
    body: { status: e.status === 'active' ? 'inactive' : 'active' },
  })
  load()
}

onMounted(load)
</script>