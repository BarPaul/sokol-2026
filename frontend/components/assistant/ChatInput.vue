<template>
  <div class="border-t border-slate-200 bg-white p-3">
    <form class="flex gap-2" @submit.prevent="send">
      <input
        v-model="text"
        type="text"
        class="input-sf flex-1"
        :placeholder="disabled ? 'AI временно недоступен' : 'Опишите вашу ситуацию...'"
        :disabled="disabled"
      >
      <button class="btn-primary !px-4" type="submit" :disabled="disabled || !text.trim() || loading">
        <Icon v-if="loading" name="heroicons:arrow-path" class="h-4 w-4 animate-spin" />
        <span v-else>Отправить</span>
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
const text = ref('')

const props = defineProps<{
  loading: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  send: [content: string]
}>()

function send() {
  if (!text.value.trim() || props.loading || props.disabled) return
  emit('send', text.value.trim())
  text.value = ''
}
</script>