<template>
  <div>
    <div v-if="loading" class="py-16 text-center text-sm text-slate-500">Загрузка...</div>
    <ArticleForm v-else-if="article" :article-id="articleId" :initial="article" />
  </div>
</template>

<script setup lang="ts">
import type { Article } from '~/shared/types'

definePageMeta({ layout: 'editor', middleware: 'editor' })

const route = useRoute()
const { request } = useApi()

const articleId = Number(route.params.id)
const article = ref<Article | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    article.value = await request<Article>(`/api/editor/articles/${articleId}`)
  } finally {
    loading.value = false
  }
})
</script>