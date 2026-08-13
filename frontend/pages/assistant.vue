<template>
  <div class="flex flex-col md:flex-row" :style="containerStyle">
    <ChatSidebar
      :chats="chats"
      :active-id="activeChatId"
      class="h-40 md:h-auto"
      @select="selectChat"
      @new-chat="newChat"
    />

    <main class="flex min-h-0 flex-1 flex-col bg-slate-50">
      <!-- Welcome -->
      <div v-if="!activeChatId" class="flex flex-1 flex-col items-center justify-center overflow-y-auto px-4 py-8">
        <div class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-700 text-2xl text-white">
          СФ
        </div>
        <h1 class="text-2xl font-bold text-slate-900">AI-помощник СтудСемья</h1>
        <p class="mt-2 max-w-lg text-center text-sm text-slate-500">
          Опишите свою ситуацию — я помогу разобраться, какие меры поддержки вам доступны, и подберу подходящие статьи.
        </p>
        <div class="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-xs text-amber-800">
          Информация носит справочный характер и не заменяет консультацию юриста.
        </div>

        <div class="mt-8 grid w-full max-w-lg gap-2 sm:grid-cols-2">
          <button
            v-for="q in suggested"
            :key="q"
            class="rounded-lg border border-slate-200 bg-white px-4 py-3 text-left text-sm text-slate-700 transition hover:border-teal-600"
            @click="startWithQuestion(q)"
          >
            {{ q }}
          </button>
        </div>
      </div>

      <!-- Chat -->
      <div v-else class="flex min-h-0 flex-1 flex-col">
        <div ref="scrollContainer" class="min-h-0 flex-1 overflow-y-auto p-4">
          <div class="flex flex-col gap-4">
            <ChatMessage v-for="m in messages" :key="m.id" :message="m" />

            <div v-if="loading" class="flex items-center gap-2 text-sm text-slate-500">
              <Icon name="heroicons:arrow-path" class="h-4 w-4 animate-spin" />
              Анализирую вашу ситуацию...
            </div>

            <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              AI-помощник временно недоступен. Попробуйте позже или воспользуйтесь ручным поиском по базе знаний.
            </div>

            <div v-if="recommended.length" class="mt-2">
              <p class="mb-2 text-sm font-medium text-slate-700">Полезные материалы:</p>
              <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                <RecommendedArticle v-for="a in recommended" :key="a.id" :article="a" />
              </div>
            </div>
          </div>
        </div>

        <ChatInput :loading="loading" :disabled="!!error" class="shrink-0 border-t" @send="sendMessage" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import type { AssistantResponse, Chat, ChatMessage, RecommendedArticle } from '~/shared/types'

const route = useRoute()
const { request } = useApi()

const chats = ref<Chat[]>([])
const messages = ref<ChatMessage[]>([])
const activeChatId = ref<number | null>(null)
const loading = ref(false)
const error = ref(false)
const recommended = ref<RecommendedArticle[]>([])

const containerStyle = ref<Record<string, string>>({ height: 'calc(100vh - 64px)' })
const scrollContainer = ref<HTMLElement | null>(null)

function scrollToBottom() {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  })
}

watch([messages, loading, recommended], scrollToBottom, { deep: true })

function updateContainerStyle() {
  const footer = document.querySelector('footer')
  const footerH = footer ? footer.offsetHeight + 48 : 0
  containerStyle.value = { height: `calc(100vh - 64px - ${footerH}px)` }
}

const suggested = [
  'Мне положены выплаты как студенческой семье?',
  'Какие льготы есть при рождении ребёнка?',
  'Как получить место в общежитии для семьи?',
]

function resetView() {
  messages.value = []
  recommended.value = []
  error.value = false
}

async function loadChats() {
  chats.value = await request<Chat[]>('/api/assistant/chats')
  if (route.query.q) {
    await newChat()
    return
  }
  if (chats.value.length > 0 && !activeChatId.value) {
    await selectChat(chats.value[0].id)
  }
}

async function newChat() {
  const created = await request<Chat>('/api/assistant/chats', { method: 'POST', body: { title: 'Новый диалог' } })
  chats.value.unshift(created)
  activeChatId.value = created.id
  resetView()
  if (route.query.q) {
    await sendMessage(String(route.query.q))
    navigateTo('/assistant', { replace: true })
  }
}

async function selectChat(id: number) {
  activeChatId.value = id
  resetView()
  messages.value = await request<ChatMessage[]>(`/api/assistant/chats/${id}/messages`)
}

async function sendMessage(content: string) {
  if (!activeChatId.value) return
  loading.value = true
  error.value = false
  messages.value.push({ id: -Date.now(), chat_id: activeChatId.value, role: 'user', content, created_at: new Date().toISOString() })
  try {
    const resp = await request<AssistantResponse>(`/api/assistant/chats/${activeChatId.value}/messages`, {
      method: 'POST',
      body: { content },
    })
    messages.value.push(resp.message)
    recommended.value = resp.articles
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

function startWithQuestion(q: string) {
  newChat().then(() => sendMessage(q))
}

onMounted(() => {
  updateContainerStyle()
  window.addEventListener('resize', updateContainerStyle)
  loadChats()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerStyle)
})
</script>