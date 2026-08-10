<template>
  <NuxtLink
    :to="`/articles/${article.slug}`"
    class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 transition hover:border-teal-600"
  >
    <Icon name="heroicons:document-text" class="mt-0.5 h-5 w-5 shrink-0 text-teal-700" />
    <div>
      <span class="text-xs font-medium text-teal-700">{{ article.category }}</span>
      <p class="mt-0.5 text-sm font-medium text-slate-900">{{ article.title }}</p>
      <p class="mt-1 text-xs text-slate-500 line-clamp-2">{{ article.summary }}</p>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import type { RecommendedArticle } from '~/shared/types'

defineProps<{ article: RecommendedArticle }>()
</script>