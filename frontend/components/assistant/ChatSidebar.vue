<template>
  <aside class="flex w-full flex-col border-b border-slate-200 bg-white md:w-72 md:border-b-0 md:border-r">
    <div class="flex h-14 items-center justify-between border-b border-slate-200 px-4">
      <span class="font-semibold text-slate-900">Диалоги</span>
      <button
        class="rounded-lg bg-teal-700 p-1.5 text-white hover:bg-teal-800"
        title="Новый чат"
        @click="$emit('new-chat')"
      >
        <Icon name="heroicons:plus" class="h-4 w-4" />
      </button>
    </div>
    <nav class="flex-1 overflow-y-auto p-2">
      <button
        v-for="chat in chats"
        :key="chat.id"
        class="mb-1 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-slate-700 transition hover:bg-teal-50"
        :class="activeId === chat.id ? 'bg-teal-50 text-teal-800' : ''"
        @click="$emit('select', chat.id)"
      >
        <Icon name="heroicons:chat-bubble-left-right" class="h-4 w-4 shrink-0 text-slate-400" />
        <span class="truncate">{{ chat.title }}</span>
      </button>
      <p v-if="chats.length === 0" class="px-3 py-4 text-xs text-slate-400">
        Пока нет диалогов. Начните новый.
      </p>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import type { Chat } from '~/shared/types'

defineProps<{
  chats: Chat[]
  activeId: number | null
}>()

defineEmits<{
  select: [id: number]
  'new-chat': []
}>()
</script>