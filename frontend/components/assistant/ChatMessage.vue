<template>
  <div class="flex gap-3" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
    <div
      v-if="message.role === 'assistant'"
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-teal-700 text-xs text-white"
    >
      AI
    </div>
    <div
      class="max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed"
      :class="message.role === 'user' ? 'bg-teal-700 text-white' : 'bg-slate-100 text-slate-800'"
    >
      {{ message.content }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from '~/shared/types'

defineProps<{ message: ChatMessage }>()
</script>