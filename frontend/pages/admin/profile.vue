<template>
  <div class="mx-auto max-w-4xl">
    <h1 class="mb-6 text-2xl font-bold text-slate-900">Профиль администратора</h1>

    <div v-if="loading" class="py-12 text-center text-sm text-slate-500">Загрузка...</div>
    <div v-else>
      <div class="card-sf mb-6">
        <div class="flex items-center gap-4">
          <div class="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-700 text-xl text-white">
            {{ initials }}
          </div>
          <div v-if="account">
            <p class="text-lg font-semibold text-slate-900">{{ account.first_name }} {{ account.last_name }}</p>
            <p class="text-sm text-slate-500">{{ account.email }}</p>
            <span class="mt-1 inline-block rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
              Модератор
            </span>
          </div>
        </div>
      </div>

      <form class="card-sf flex flex-col gap-4" @submit.prevent="saveProfile">
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="label-sf">Имя</label>
            <input v-model="profile.first_name" class="input-sf">
          </div>
          <div>
            <label class="label-sf">Фамилия</label>
            <input v-model="profile.last_name" class="input-sf">
          </div>
        </div>
        <div>
          <label class="label-sf">Email</label>
          <input v-model="profile.email" type="email" class="input-sf">
        </div>
        <p v-if="profileMsg" class="rounded-lg bg-teal-50 px-3 py-2 text-sm text-teal-800">{{ profileMsg }}</p>
        <button class="btn-primary !w-fit" type="submit" :disabled="savingProfile">
          {{ savingProfile ? 'Сохранение...' : 'Сохранить изменения' }}
        </button>
      </form>

      <form class="card-sf mt-6 flex flex-col gap-4" @submit.prevent="savePassword">
        <p class="font-semibold text-slate-900">Смена пароля</p>
        <div>
          <label class="label-sf">Текущий пароль</label>
          <input v-model="pwd.current_password" type="password" class="input-sf">
        </div>
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="label-sf">Новый пароль</label>
            <input v-model="pwd.new_password" type="password" class="input-sf">
          </div>
          <div>
            <label class="label-sf">Подтверждение</label>
            <input v-model="pwd.confirm" type="password" class="input-sf">
          </div>
        </div>
        <p v-if="pwdMsg" class="rounded-lg px-3 py-2 text-sm" :class="pwdErr ? 'bg-red-50 text-red-700' : 'bg-teal-50 text-teal-800'">{{ pwdMsg }}</p>
        <button class="btn-primary !w-fit" type="submit" :disabled="savingPwd">Изменить пароль</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { passwordChangeSchema } from '~/shared/schemas'
import type { Account } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { request } = useApi()

const account = ref<Account | null>(null)
const loading = ref(true)
const profile = reactive({ first_name: '', last_name: '', email: '' })
const profileMsg = ref('')
const savingProfile = ref(false)
const pwd = reactive({ current_password: '', new_password: '', confirm: '' })
const pwdMsg = ref('')
const pwdErr = ref(false)
const savingPwd = ref(false)

const initials = computed(() => {
  if (!account.value) return 'А'
  return `${account.value.first_name?.[0] || ''}${account.value.last_name?.[0] || ''}` || 'А'
})

async function saveProfile() {
  savingProfile.value = true
  profileMsg.value = ''
  try {
    const updated = await request<Account>('/api/auth/me', { method: 'PATCH', body: { ...profile } })
    account.value = updated
    profileMsg.value = 'Профиль сохранён'
  } finally {
    savingProfile.value = false
  }
}

async function savePassword() {
  pwdMsg.value = ''
  pwdErr.value = false
  const res = passwordChangeSchema.safeParse({ ...pwd })
  if (!res.success) {
    pwdErr.value = true
    pwdMsg.value = res.error.errors[0]?.message || 'Ошибка'
    return
  }
  savingPwd.value = true
  try {
    await request('/api/auth/change-password', { method: 'POST', body: { current_password: pwd.current_password, new_password: pwd.new_password } })
    pwdMsg.value = 'Пароль изменён'
    pwd.current_password = ''
    pwd.new_password = ''
    pwd.confirm = ''
  } catch {
    pwdErr.value = true
    pwdMsg.value = 'Не удалось изменить пароль'
  } finally {
    savingPwd.value = false
  }
}

onMounted(async () => {
  try {
    account.value = await request<Account>('/api/auth/me')
    profile.first_name = account.value.first_name
    profile.last_name = account.value.last_name
    profile.email = account.value.email
  } finally {
    loading.value = false
  }
})
</script>