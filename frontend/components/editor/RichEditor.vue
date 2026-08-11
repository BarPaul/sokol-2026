<template>
  <div class="rich-editor">
    <div class="mb-2 flex flex-wrap items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1.5">
      <button type="button" class="rich-btn" title="Жирный" :class="{ 'rich-btn-active': active('bold') }" @mousedown.prevent="exec('bold')">
        <Icon name="heroicons:bold" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Курсив" :class="{ 'rich-btn-active': active('italic') }" @mousedown.prevent="exec('italic')">
        <Icon name="heroicons:italic" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Подчёркнутый" :class="{ 'rich-btn-active': active('underline') }" @mousedown.prevent="exec('underline')">
        <Icon name="heroicons:underline" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Зачёркнутый" :class="{ 'rich-btn-active': active('strikeThrough') }" @mousedown.prevent="exec('strikeThrough')">
        <Icon name="heroicons:strikethrough" class="h-4 w-4" />
      </button>

      <span class="mx-1 h-5 w-px bg-slate-300" />

      <select class="rich-select" title="Размер текста" @change="setSize($event)">
        <option value="3">Обычный</option>
        <option value="4">Крупный</option>
        <option value="5">Заголовок 2</option>
        <option value="6">Заголовок 1</option>
        <option value="1">Мелкий</option>
        <option value="2">Маленький</option>
      </select>

      <input type="color" class="h-8 w-8 cursor-pointer rounded border border-slate-300 p-0.5" title="Цвет текста" @input="setColor($event)">
      <input type="color" class="h-8 w-8 cursor-pointer rounded border border-slate-300 p-0.5" title="Цвет фона" @input="setBgColor($event)">

      <span class="mx-1 h-5 w-px bg-slate-300" />

      <button type="button" class="rich-btn" title="Цитата" :class="{ 'rich-btn-active': active('formatBlock', 'blockquote') }" @mousedown.prevent="setBlock('blockquote')">
        <Icon name="heroicons:chat-bubble-bottom-center-text" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Список" :class="{ 'rich-btn-active': active('insertUnorderedList') }" @mousedown.prevent="exec('insertUnorderedList')">
        <Icon name="heroicons:list-bullet" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Ссылка" @mousedown.prevent="addLink">
        <Icon name="heroicons:link" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Картинка" @mousedown.prevent="openFile('image')">
        <Icon name="heroicons:photo" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Файл" @mousedown.prevent="openFile('file')">
        <Icon name="heroicons:paper-clip" class="h-4 w-4" />
      </button>

      <span class="mx-1 h-5 w-px bg-slate-300" />

      <button type="button" class="rich-btn" title="Скачать как Markdown" @mousedown.prevent="downloadMd">
        <Icon name="heroicons:arrow-down-tray" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Очистить" @mousedown.prevent="clear">
        <Icon name="heroicons:trash" class="h-4 w-4" />
      </button>
    </div>

    <div
      ref="editorEl"
      class="input-sf min-h-72 cursor-text whitespace-pre-wrap [&_blockquote]:ml-0 [&_blockquote]:border-l-4 [&_blockquote]:border-teal-300 [&_blockquote]:bg-teal-50 [&_blockquote]:px-4 [&_blockquote]:py-2 [&_blockquote]:italic [&_blockquote]:text-slate-600 [&_blockquote]:not-italic"
      contenteditable
      @input="emitChange"
      @keyup="trackActive"
    />

    <input ref="fileInput" type="file" class="hidden" accept="image/*" @change="onFilePicked">
    <input ref="anyFileInput" type="file" class="hidden" @change="onAnyFilePicked">
  </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue'

const props = defineProps<{
  modelValue: string
  placeholder?: string
}>()

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const editorEl: Ref<HTMLDivElement | null> = ref(null)
const fileInput: Ref<HTMLInputElement | null> = ref(null)
const anyFileInput: Ref<HTMLInputElement | null> = ref(null)
const api = useApi()

onMounted(() => {
  if (editorEl.value) {
    editorEl.value.innerHTML = props.modelValue || ''
    if (!props.modelValue && props.placeholder) {
      const ph = document.createElement('p')
      ph.className = 'text-slate-400'
      ph.textContent = props.placeholder
      ph.dataset.placeholder = '1'
      editorEl.value.appendChild(ph)
    }
  }
})

watch(
  () => props.modelValue,
  (v) => {
    const el = editorEl.value
    if (el && document.activeElement !== el && v !== el.innerHTML) {
      el.innerHTML = v || ''
    }
  },
)

function exec(cmd: string, value?: string) {
  if (!editorEl.value) return
  editorEl.value.focus()
  document.execCommand(cmd, false, value)
  emitChange()
  trackActive()
}

function setSize(e: Event) {
  const value = (e.target as HTMLSelectElement).value
  exec('fontSize', value)
  document.execCommand('styleWithCSS', false, 'true')
  const el = editorEl.value?.querySelector('font[size="' + value + '"]')
  if (el) {
    const span = document.createElement('span')
    const sizes: Record<string, string> = { '1': '0.75rem', '2': '0.85rem', '3': '1rem', '4': '1.25rem', '5': '1.5rem', '6': '2rem' }
    const fs = sizes[value]
    if (fs) span.style.fontSize = fs
    span.innerHTML = el.innerHTML
    el.replaceWith(span)
  }
  emitChange()
}

function setColor(e: Event) {
  document.execCommand('foreColor', false, (e.target as HTMLInputElement).value)
  emitChange()
}

function setBgColor(e: Event) {
  document.execCommand('hiliteColor', false, (e.target as HTMLInputElement).value)
  emitChange()
}

function setBlock(block: string) {
  exec('formatBlock', block)
}

function active(cmd: string, _value?: string): boolean {
  try {
    return document.queryCommandState(cmd)
  } catch {
    return false
  }
}

function trackActive() {
  // триггерит перерендер для подсветки активных кнопок
}

function addLink() {
  const url = window.prompt('Введите URL (https://...)')
  if (url) exec('createLink', url)
}

function openFile(kind: 'image' | 'file') {
  if (kind === 'image') fileInput.value?.click()
  else anyFileInput.value?.click()
}

async function upload(blob: File) {
  const form = new FormData()
  form.append('file', blob)
  const res = await $fetch(`${api.base}/api/editor/articles/upload`, {
    method: 'POST',
    body: form,
    headers: { Authorization: `Bearer ${api.token.value}` },
  })
  return (res as { url: string }).url
}

async function onFilePicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!editorEl.value || !file) return
  try {
    const url = await upload(file)
    editorEl.value.focus()
    document.execCommand('insertHTML', false, `<img src="${url}" alt="${file.name}" class="my-2 max-w-full rounded-lg" />`)
    emitChange()
  } catch {
    window.alert('Не удалось загрузить изображение')
  }
}

async function onAnyFilePicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!editorEl.value || !file) return
  try {
    const url = await upload(file)
    editorEl.value.focus()
    document.execCommand('insertHTML', false, `<a href="${url}" class="text-teal-700 underline">📎 ${file.name}</a>`)
    emitChange()
  } catch {
    window.alert('Не удалось загрузить файл')
  }
}

function emitChange() {
  if (!editorEl.value) return
  const el = editorEl.value
  if (el.dataset.placeholder && el.textContent?.trim() === '') {
    emit('update:modelValue', '')
  } else {
    el.querySelectorAll('[data-placeholder]').forEach(n => n.remove())
    emit('update:modelValue', el.innerHTML)
  }
}

function clear() {
  if (editorEl.value) {
    editorEl.value.innerHTML = ''
    emit('update:modelValue', '')
  }
}

function downloadMd() {
  const html = editorEl.value?.innerHTML || ''
  const md = htmlToMarkdown(html)
  const blob = new Blob([md], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'article.md'
  a.click()
  URL.revokeObjectURL(url)
}

function htmlToMarkdown(html: string): string {
  const div = document.createElement('div')
  div.innerHTML = html
  const walk = (el: HTMLElement): string => {
    const blocks: string[] = []
    el.childNodes.forEach((node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        blocks.push(node.textContent || '')
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        const n = node as HTMLElement
        const tag = n.tagName.toLowerCase()
        const inner = htmlToMarkdown(n.innerHTML) || n.textContent || ''
        if (tag === 'blockquote') blocks.push(`> ${inner.replace(/\n/g, '\n> ')}`)
        else if (tag === 'h1' || tag === 'h2' || tag === 'h3') blocks.push(`${'#'.repeat(Number(tag[1]))} ${inner}`)
        else if (tag === 'b' || tag === 'strong') blocks.push(`**${inner}**`)
        else if (tag === 'i' || tag === 'em') blocks.push(`*${inner}*`)
        else if (tag === 'u') blocks.push(`<u>${inner}</u>`)
        else if (tag === 's' || tag === 'strike' || tag === 'del') blocks.push(`~~${inner}~~`)
        else if (tag === 'a') blocks.push(`[${inner}](${n.getAttribute('href') || ''})`)
        else if (tag === 'img') blocks.push(`![${n.getAttribute('alt') || ''}](${n.getAttribute('src') || ''})`)
        else if (tag === 'ul') blocks.push(n.innerHTML.replace(/<[^>]+>/g, m => (m.includes('li') ? '\n- ' : '')))
        else if (tag === 'ol') blocks.push(n.innerHTML.replace(/<[^>]+>/g, m => (m.includes('li') ? '\n1. ' : '')))
        else if (tag === 'li') blocks.push(`- ${inner}`)
        else blocks.push(inner)
      }
    })
    return blocks.filter((b, i) => b !== '' || i === 0).join('\n')
  }
  return walk(div).replace(/\n{3,}/g, '\n\n').trim()
}
</script>

<style scoped>
.rich-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  width: 2rem;
  border-radius: 0.375rem;
  color: #475569;
  transition: background-color 0.15s;
}
.rich-btn:hover {
  background-color: #e2e8f0;
}
.rich-btn-active {
  background-color: #ccfbf1;
  color: #0f766e;
}
.rich-select {
  height: 2rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  background: #fff;
  font-size: 0.75rem;
  padding: 0 0.5rem;
  color: #475569;
}
</style>