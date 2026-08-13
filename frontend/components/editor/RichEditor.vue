<template>
  <div class="rich-editor">
    <div class="mb-2 flex flex-wrap items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1.5">
      <button
        type="button"
        class="rich-btn"
        title="Жирный"
        :class="{ 'rich-btn-active': editor?.isActive('bold') }"
        @mousedown.prevent="editor?.chain().focus().toggleBold().run()"
      >
        <Icon name="heroicons:bold" class="h-4 w-4" />
      </button>
      <button
        type="button"
        class="rich-btn"
        title="Курсив"
        :class="{ 'rich-btn-active': editor?.isActive('italic') }"
        @mousedown.prevent="editor?.chain().focus().toggleItalic().run()"
      >
        <Icon name="heroicons:italic" class="h-4 w-4" />
      </button>
      <button
        type="button"
        class="rich-btn"
        title="Подчёркнутый"
        :class="{ 'rich-btn-active': editor?.isActive('underline') }"
        @mousedown.prevent="editor?.chain().focus().toggleUnderline().run()"
      >
        <Icon name="heroicons:underline" class="h-4 w-4" />
      </button>
      <button
        type="button"
        class="rich-btn"
        title="Зачёркнутый"
        :class="{ 'rich-btn-active': editor?.isActive('strike') }"
        @mousedown.prevent="editor?.chain().focus().toggleStrike().run()"
      >
        <Icon name="heroicons:strikethrough" class="h-4 w-4" />
      </button>

      <span class="mx-1 h-5 w-px bg-slate-300" />

      <button
        type="button"
        class="rich-btn"
        title="Обычный текст"
        :class="{ 'rich-btn-active': editor?.isActive('paragraph') }"
        @mousedown.prevent="editor?.chain().focus().setParagraph().run()"
      >
        <span class="text-xs font-medium">¶</span>
      </button>
      <button
        type="button"
        class="rich-btn"
        title="Заголовок 1"
        :class="{ 'rich-btn-active': editor?.isActive('heading', { level: 1 }) }"
        @mousedown.prevent="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
      >
        <span class="text-xs font-bold">H1</span>
      </button>
      <button
        type="button"
        class="rich-btn"
        title="Заголовок 2"
        :class="{ 'rich-btn-active': editor?.isActive('heading', { level: 2 }) }"
        @mousedown.prevent="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
      >
        <span class="text-xs font-bold">H2</span>
      </button>

      <span class="mx-1 h-5 w-px bg-slate-300" />

      <input type="color" class="h-8 w-8 cursor-pointer rounded border border-slate-300 p-0.5" title="Цвет текста" @input="setColor($event, 'text')">
      <input type="color" class="h-8 w-8 cursor-pointer rounded border border-slate-300 p-0.5" title="Цвет фона" @input="setColor($event, 'bg')">

      <span class="mx-1 h-5 w-px bg-slate-300" />

      <button
        type="button"
        class="rich-btn"
        title="Цитата"
        :class="{ 'rich-btn-active': editor?.isActive('blockquote') }"
        @mousedown.prevent="editor?.chain().focus().toggleBlockquote().run()"
      >
        <Icon name="heroicons:chat-bubble-bottom-center-text" class="h-4 w-4" />
      </button>
      <button
        type="button"
        class="rich-btn"
        title="Маркированный список"
        :class="{ 'rich-btn-active': editor?.isActive('bulletList') }"
        @mousedown.prevent="editor?.chain().focus().toggleBulletList().run()"
      >
        <Icon name="heroicons:list-bullet" class="h-4 w-4" />
      </button>
      <button
        type="button"
        class="rich-btn"
        title="Нумерованный список"
        :class="{ 'rich-btn-active': editor?.isActive('orderedList') }"
        @mousedown.prevent="editor?.chain().focus().toggleOrderedList().run()"
      >
        <Icon name="heroicons:numbered-list" class="h-4 w-4" />
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

      <button
        type="button"
        class="rich-btn"
        title="Отменить"
        :disabled="!editor?.can().undo()"
        @mousedown.prevent="editor?.chain().focus().undo().run()"
      >
        <Icon name="heroicons:arrow-uturn-left" class="h-4 w-4" />
      </button>
      <button
        type="button"
        class="rich-btn"
        title="Повторить"
        :disabled="!editor?.can().redo()"
        @mousedown.prevent="editor?.chain().focus().redo().run()"
      >
        <Icon name="heroicons:arrow-uturn-right" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Скачать как Markdown" @mousedown.prevent="downloadMd">
        <Icon name="heroicons:arrow-down-tray" class="h-4 w-4" />
      </button>
      <button type="button" class="rich-btn" title="Очистить" @mousedown.prevent="clear">
        <Icon name="heroicons:trash" class="h-4 w-4" />
      </button>
    </div>

    <EditorContent :editor="editor" class="input-sf min-h-72 cursor-text" />

    <input ref="fileInput" type="file" class="hidden" accept="image/*" @change="onFilePicked">
    <input ref="anyFileInput" type="file" class="hidden" @change="onAnyFilePicked">
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import { TextStyle } from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import Highlight from '@tiptap/extension-highlight'
import Underline from '@tiptap/extension-underline'
import type { Ref } from 'vue'

const props = defineProps<{
  modelValue: string
  placeholder?: string
}>()

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const fileInput: Ref<HTMLInputElement | null> = ref(null)
const anyFileInput: Ref<HTMLInputElement | null> = ref(null)
const api = useApi()

const editor = useEditor({
  content: props.modelValue || '',
  extensions: [
    StarterKit.configure({
      link: false,
      underline: false,
    }),
    Underline,
    Link.configure({
      openOnClick: false,
      autolink: true,
      HTMLAttributes: { rel: 'noopener noreferrer nofollow', target: '_blank' },
    }),
    Image.configure({ allowBase64: true, inline: false }),
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
  ],
  editorProps: {
    attributes: {
      placeholder: props.placeholder || '',
      class: 'outline-none min-h-72',
    },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.isEmpty ? '' : editor.getHTML())
  },
})

watch(
  () => props.modelValue,
  (v) => {
    const ed = editor.value
    if (ed && v !== ed.getHTML()) {
      ed.commands.setContent(v || '')
    }
  },
)

function setColor(e: Event, kind: 'text' | 'bg') {
  const value = (e.target as HTMLInputElement).value
  if (!editor.value) return
  if (kind === 'text') editor.value.chain().focus().setColor(value).run()
  else editor.value.chain().focus().toggleHighlight({ color: value }).run()
}

function addLink() {
  if (!editor.value) return
  const prev = editor.value.getAttributes('link').href as string | undefined
  const url = window.prompt('Введите URL (https://...)', prev || 'https://')
  if (url === null) return
  if (url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
  } else {
    editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
  }
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
  if (!editor.value || !file) return
  try {
    const url = await upload(file)
    editor.value.chain().focus().setImage({ src: url, alt: file.name }).run()
  } catch {
    window.alert('Не удалось загрузить изображение')
  }
}

async function onAnyFilePicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!editor.value || !file) return
  try {
    const url = await upload(file)
    editor.value.chain().focus().insertContent(`<a href="${url}" class="text-teal-700 underline">📎 ${file.name}</a>`).run()
  } catch {
    window.alert('Не удалось загрузить файл')
  }
}

function clear() {
  editor.value?.chain().focus().clearContent(true).run()
  emit('update:modelValue', '')
}

function downloadMd() {
  const html = editor.value?.getHTML() || ''
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
.rich-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.rich-btn-active {
  background-color: #ccfbf1;
  color: #0f766e;
}
:deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
  color: #94a3b8;
}
:deep(.tiptap blockquote) {
  margin: 0.5rem 0;
  border-left: 4px solid #5eead4;
  background: #f0fdfa;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  color: #475569;
}
:deep(.tiptap img) {
  max-width: 100%;
  border-radius: 0.5rem;
  margin: 0.5rem 0;
}
:deep(.tiptap ul),
:deep(.tiptap ol) {
  padding-left: 1.25rem;
  margin: 0.5rem 0;
}
:deep(.tiptap a) {
  color: #0f766e;
  text-decoration: underline;
  cursor: pointer;
}
:deep(.tiptap h1),
:deep(.tiptap h2),
:deep(.tiptap h3) {
  margin: 1rem 0 0.5rem;
  font-weight: 600;
  color: #0f172a;
}
</style>
