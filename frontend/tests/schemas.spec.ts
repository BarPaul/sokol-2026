import { describe, it, expect } from 'vitest'
import {
  loginSchema,
  articleSchema,
  editorCreateSchema,
  passwordChangeSchema,
  aiSettingsSchema,
} from '../shared/schemas'

describe('loginSchema', () => {
  it('accepts valid credentials', () => {
    const r = loginSchema.safeParse({ email: 'user@example.com', password: '1234' })
    expect(r.success).toBe(true)
  })

  it('rejects invalid email', () => {
    const r = loginSchema.safeParse({ email: 'not-an-email', password: '1234' })
    expect(r.success).toBe(false)
  })

  it('rejects short password', () => {
    const r = loginSchema.safeParse({ email: 'user@example.com', password: '12' })
    expect(r.success).toBe(false)
  })
})

describe('articleSchema', () => {
  const valid = {
    title: 'Короткое название',
    category: 'Выплаты',
    summary: 'Описание',
    content: 'Содержание статьи длиной более десяти символов',
    region: 'Москва',
    official_source: 'https://example.com',
    restrictions: 'нет',
  }

  it('accepts valid article', () => {
    expect(articleSchema.safeParse(valid).success).toBe(true)
  })

  it('rejects too short title', () => {
    const r = articleSchema.safeParse({ ...valid, title: 'Аб' })
    expect(r.success).toBe(false)
  })

  it('rejects too short content', () => {
    const r = articleSchema.safeParse({ ...valid, content: 'коротко' })
    expect(r.success).toBe(false)
  })

  it('rejects missing category', () => {
    const r = articleSchema.safeParse({ ...valid, category: '' })
    expect(r.success).toBe(false)
  })
})

describe('editorCreateSchema', () => {
  it('accepts valid editor payload', () => {
    const r = editorCreateSchema.safeParse({
      first_name: 'Иван',
      last_name: 'Петров',
      email: 'ivan@example.com',
      password: 'secret123',
      role: 'editor',
    })
    expect(r.success).toBe(true)
  })

  it('rejects weak password', () => {
    const r = editorCreateSchema.safeParse({
      first_name: 'Иван',
      last_name: 'Петров',
      email: 'ivan@example.com',
      password: '123',
      role: 'editor',
    })
    expect(r.success).toBe(false)
  })

  it('rejects wrong role', () => {
    const r = editorCreateSchema.safeParse({
      first_name: 'Иван',
      last_name: 'Петров',
      email: 'ivan@example.com',
      password: 'secret123',
      role: 'admin',
    })
    expect(r.success).toBe(false)
  })
})

describe('passwordChangeSchema', () => {
  it('accepts matching passwords', () => {
    const r = passwordChangeSchema.safeParse({
      current_password: '1234',
      new_password: 'newpass1',
      confirm: 'newpass1',
    })
    expect(r.success).toBe(true)
  })

  it('rejects mismatched confirmation', () => {
    const r = passwordChangeSchema.safeParse({
      current_password: '1234',
      new_password: 'newpass1',
      confirm: 'different',
    })
    expect(r.success).toBe(false)
  })
})

describe('aiSettingsSchema', () => {
  it('accepts valid settings', () => {
    const r = aiSettingsSchema.safeParse({
      system_prompt: 'Ты помощник',
      model: 'deepseek-v4-flash',
      temperature: 0.5,
      max_tokens: 1024,
      knowledge_enabled: true,
    })
    expect(r.success).toBe(true)
  })

  it('rejects temperature above 1', () => {
    const r = aiSettingsSchema.safeParse({
      system_prompt: '',
      model: 'm',
      temperature: 1.5,
      max_tokens: 100,
      knowledge_enabled: false,
    })
    expect(r.success).toBe(false)
  })
})