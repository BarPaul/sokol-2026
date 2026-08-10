export interface ArticleCard {
  id: number
  title: string
  slug: string
  summary: string
  category: string
  updated_at: string
}

export interface Article extends ArticleCard {
  content: string
  region: string
  official_source: string
  restrictions: string
  author_id: number
  author_name: string
  status: string
  created_at: string
  published_at: string | null
  coauthors: Coauthor[]
  related: ArticleCard[]
}

export interface Coauthor {
  id: number
  first_name: string
  last_name: string
  email: string
}

export interface ArticleListResponse {
  items: ArticleCard[]
  total: number
  limit: number
  offset: number
}

export interface CategoryItem {
  name: string
  count: number
}

// Auth
export interface LoginPayload {
  email: string
  password: string
}

export interface Account {
  id: number
  first_name: string
  last_name: string
  email: string
  role: string
  status: string
  created_at?: string
  last_login_at?: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

// Assistant
export interface Chat {
  id: number
  session_id: string
  title: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: number
  chat_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface RecommendedArticle {
  id: number
  title: string
  slug: string
  summary: string
  category: string
}

export interface AssistantResponse {
  message: ChatMessage
  articles: RecommendedArticle[]
}

// Editor
export interface ArticleCreate {
  title: string
  summary: string
  content: string
  category: string
  region: string
  official_source: string
  restrictions: string
  status: 'draft' | 'published'
}

export interface EditorArticlesResponse {
  items: Article[]
  total: number
}

// Admin
export type EditorAccount = Account

export interface LogEntry {
  id: number
  account_id: number | null
  account_name: string
  action: string
  entity_type: string
  entity_id: number | null
  result: string
  description: string
  metadata: Record<string, unknown>
  created_at: string
}

export interface LogsResponse {
  items: LogEntry[]
  total: number
}

export interface AISettings {
  id: number
  system_prompt: string
  model: string
  temperature: number
  max_tokens: number
  knowledge_enabled: boolean
  updated_at?: string
}

export interface KnowledgeDocument {
  id: number
  title: string
  source: string
  category: string
  content: string
  is_active: boolean
  created_at: string
  updated_at: string
}