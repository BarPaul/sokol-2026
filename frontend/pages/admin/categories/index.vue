<template>
  <div class="mx-auto max-w-4xl">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Категории</h1>
      <p class="mt-1 text-sm text-slate-500">
        Фиксированные категории каталога. Порядок задаётся числом сортировки.
      </p>
    </div>

    <form class="card-sf mb-6 flex flex-col gap-4 sm:flex-row sm:items-end" @submit.prevent="create">
      <div class="flex-1">
        <label class="label-sf">Название новой категории</label>
        <input v-model="newName" class="input-sf" placeholder="Например: Стипендии" required>
      </div>
      <div class="sm:w-32">
        <label class="label-sf">Порядок</label>
        <input v-model.number="newSort" type="number" class="input-sf" min="0">
      </div>
      <button class="btn-primary" type="submit" :disabled="creating">Создать</button>
    </form>

    <p v-if="error" class="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

    <div class="card-sf">
      <div class="divide-y divide-slate-100">
        <div
          v-for="c in categories"
          :key="c.id"
          class="flex flex-col gap-3 py-3 sm:flex-row sm:items-center"
        >
          <input v-model="editing[c.id].name" class="input-sf flex-1" :disabled="editingId !== c.id">
          <input
            v-model.number="editing[c.id].sort_order"
            type="number"
            class="input-sf !w-24"
            min="0"
            :disabled="editingId !== c.id"
          >
          <div class="flex gap-2 sm:justify-end">
            <template v-if="editingId === c.id">
              <button class="btn-primary !py-1.5 !text-xs" @click="save(c)">Сохранить</button>
              <button class="btn-secondary !py-1.5 !text-xs" @click="cancelEdit(c)">Отмена</button>
            </template>
            <template v-else>
              <button class="text-indigo-600 hover:underline" @click="startEdit(c)">Ред.</button>
              <span class="text-xs text-slate-400">{{ countLabel(c) }}</span>
              <button class="text-red-600 hover:underline" @click="remove(c)">Удалить</button>
            </template>
          </div>
        </div>
        <EmptyState v-if="categories.length === 0" title="Категории не найдены" description="Создайте первую категорию." />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Category } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { request } = useApi()

const categories = ref<Category[]>([])
const editing = ref<Record<number, { name: string; sort_order: number }>>({})
const editingId = ref<number | null>(null)
const newName = ref('')
const newSort = ref(0)
const creating = ref(false)
const error = ref('')

const countLabel = (c: Category) => (c.count ? `${c.count} ст.` : '')

function startEdit(c: Category) {
  editingId.value = c.id
  editing.value[c.id] = { name: c.name, sort_order: c.sort_order }
}

function cancelEdit(c: Category) {
  editingId.value = null
  editing.value[c.id] = { name: c.name, sort_order: c.sort_order }
}

async function load() {
  categories.value = await request<Category[]>('/api/admin/categories')
  for (const c of categories.value) {
    editing.value[c.id] = { name: c.name, sort_order: c.sort_order }
  }
}

async function create() {
  error.value = ''
  creating.value = true
  try {
    await request('/api/admin/categories', { method: 'POST', body: { name: newName.value.trim(), sort_order: newSort.value } })
    newName.value = ''
    newSort.value = 0
    await load()
  } catch (e) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || 'Ошибка создания'
  } finally {
    creating.value = false
  }
}

async function save(c: Category) {
  error.value = ''
  try {
    await request(`/api/admin/categories/${c.id}`, {
      method: 'PATCH',
      body: { name: editing.value[c.id].name.trim(), sort_order: editing.value[c.id].sort_order },
    })
    editingId.value = null
    await load()
  } catch (e) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || 'Ошибка сохранения'
  }
}

async function remove(c: Category) {
  if (!confirm(`Удалить категорию «${c.name}»?`)) return
  try {
    await request(`/api/admin/categories/${c.id}`, { method: 'DELETE' })
    await load()
  } catch (e) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || 'Ошибка удаления'
  }
}

onMounted(load)
</script>