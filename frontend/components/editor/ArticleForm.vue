<template>
  <div class="mx-auto max-w-4xl">
    <h1 class="mb-6 text-2xl font-bold text-slate-900">{{ title }}</h1>

    <form class="card-sf mb-6 flex flex-col gap-5" @submit.prevent="saveDraft">
      <div>
        <label class="label-sf">Заголовок *</label>
        <input v-model="form.title" class="input-sf" required>
      </div>
      <div>
        <label class="label-sf">Категория *</label>
        <input v-model="form.category" class="input-sf" placeholder="Выплаты и льготы" required>
      </div>
      <div>
        <label class="label-sf">Краткое описание</label>
        <textarea v-model="form.summary" class="input-sf" rows="2" placeholder="Кратко о чём статья" />
      </div>
      <div>
        <label class="label-sf">Содержание *</label>
        <textarea v-model="form.content" class="input-sf" rows="12" placeholder="Полный текст статьи. ## для подзаголовков" required />
      </div>
      <div class="grid gap-5 sm:grid-cols-3">
        <div>
          <label class="label-sf">Регион</label>
          <input v-model="form.region" class="input-sf">
        </div>
        <div>
          <label class="label-sf">Официальный источник</label>
          <input v-model="form.official_source" class="input-sf">
        </div>
        <div>
          <label class="label-sf">Ограничения</label>
          <input v-model="form.restrictions" class="input-sf">
        </div>
      </div>

      <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

      <div class="flex flex-wrap gap-3">
        <button class="btn-secondary" type="button" @click="router.push('/editor/articles')">Отмена</button>
        <button class="btn-primary" type="submit" :disabled="saving">
          {{ saving ? 'Сохранение...' : 'Сохранить черновик' }}
        </button>
        <button
          class="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-slate-900 hover:bg-amber-400 disabled:opacity-50"
          type="button"
          :disabled="saving"
          @click="publish"
        >
          Опубликовать
        </button>
      </div>
    </form>

    <div v-if="isEdit" class="card-sf">
      <div class="flex items-center justify-between">
        <p class="font-semibold text-slate-900">Соавторы</p>
        <NuxtLink :to="`/editor/articles/${articleId}/coauthors`" class="text-sm text-teal-700 hover:underline">
          Управление →
        </NuxtLink>
      </div>
      <div class="mt-3 flex flex-wrap gap-2">
        <span
          v-for="c in coauthors"
          :key="c.id"
          class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700"
        >
          {{ c.first_name }} {{ c.last_name }}
        </span>
        <span v-if="coauthors.length === 0" class="text-sm text-slate-400">Соавторов пока нет</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { articleSchema } from '~/shared/schemas'
import type { Article } from '~/shared/types'

const props = defineProps<{
  articleId: number | null
  initial?: Partial<Article> | null
}>()

const router = useRouter()
const { request } = useApi()

const isEdit = computed(() => props.articleId !== null)
const title = computed(() => (isEdit.value ? 'Редактирование статьи' : 'Создание статьи'))

const form = reactive({
  title: '',
  category: '',
  summary: '',
  content: '',
  region: '',
  official_source: '',
  restrictions: '',
  status: 'draft',
})

const coauthors = ref<{ id: number; first_name: string; last_name: string; email: string }[]>([])
const saving = ref(false)
const error = ref('')

if (props.initial) {
  Object.assign(form, {
    title: props.initial.title,
    category: props.initial.category,
    summary: props.initial.summary,
    content: props.initial.content,
    region: props.initial.region,
    official_source: props.initial.official_source,
    restrictions: props.initial.restrictions,
    status: props.initial.status,
  })
  coauthors.value = props.initial.coauthors || []
}

async function persist(status: 'draft' | 'published') {
  error.value = ''
  const parsed = articleSchema.safeParse({ ...form })
  if (!parsed.success) {
    error.value = parsed.error.errors[0]?.message || 'Проверьте заполнение полей'
    return
  }
  saving.value = true
  try {
    const body = { ...form, status }
    if (isEdit.value) {
      await request(`/api/editor/articles/${props.articleId}`, { method: 'PATCH', body })
    } else {
      await request('/api/editor/articles', { method: 'POST', body })
    }
    router.push('/editor/articles')
  } catch (e) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

const saveDraft = () => persist('draft')
const publish = () => persist('published')
</script>