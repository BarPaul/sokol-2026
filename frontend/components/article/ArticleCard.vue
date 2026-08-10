<template>
  <NuxtLink
    :to="`/articles/${article.slug}`"
    class="card-sf flex flex-col transition hover:border-teal-600 hover:shadow-md"
  >
    <span class="mb-3 w-fit rounded-full bg-teal-50 px-2.5 py-1 text-xs font-medium text-teal-800">
      {{ article.category || 'Без категории' }}
    </span>
    <h3 class="text-base font-semibold text-slate-900">{{ article.title }}</h3>
    <p class="mt-2 line-clamp-3 flex-1 text-sm text-slate-600">{{ article.summary }}</p>
    <div class="mt-4 flex items-center justify-between text-xs text-slate-400">
      <time :datetime="article.updated_at">{{ formatDate(article.updated_at) }}</time>
      <span>5 мин чтения</span>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import type { ArticleCard } from '~/shared/types'

defineProps<{ article: ArticleCard }>()

const formatDate = (iso: string) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>