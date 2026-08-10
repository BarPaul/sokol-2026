import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(4, 'Минимум 4 символа'),
})

export const articleSchema = z.object({
  title: z.string().min(3, 'Название не короче 3 символов').max(300),
  category: z.string().min(1, 'Укажите категорию'),
  summary: z.string().max(500, 'Слишком длинное описание'),
  content: z.string().min(10, 'Содержание не короче 10 символов'),
  region: z.string(),
  official_source: z.string(),
  restrictions: z.string(),
})

export const editorCreateSchema = z.object({
  first_name: z.string().min(1, 'Имя обязательно').max(100),
  last_name: z.string().min(1, 'Фамилия обязательна').max(100),
  email: z.string().email('Некорректный email'),
  password: z.string().min(6, 'Минимум 6 символов'),
  role: z.literal('editor'),
})

export const passwordChangeSchema = z
  .object({
    current_password: z.string().min(4),
    new_password: z.string().min(6, 'Минимум 6 символов'),
    confirm: z.string(),
  })
  .refine(v => v.new_password === v.confirm, {
    message: 'Пароли не совпадают',
    path: ['confirm'],
  })

export const aiSettingsSchema = z.object({
  model: z.string().min(1),
  temperature: z.number().min(0).max(1),
  max_tokens: z.number().int().min(1).max(8192),
  knowledge_enabled: z.boolean(),
  system_prompt: z.string(),
})