import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ArticleCard from '../components/article/ArticleCard.vue'

const stubs = {
  NuxtLink: {
    props: ['to'],
    template: '<a :href="to"><slot /></a>',
  },
}

const article = {
  id: 1,
  title: 'Пособия для студенческих семей',
  slug: 'posobiya',
  summary: 'Краткое описание поддержки',
  category: 'Выплаты',
  updated_at: '2026-01-15T10:00:00Z',
}

describe('ArticleCard', () => {
  it('renders title, summary and category', () => {
    const wrapper = mount(ArticleCard, { props: { article }, global: { stubs } })
    expect(wrapper.text()).toContain('Пособия для студенческих семей')
    expect(wrapper.text()).toContain('Краткое описание поддержки')
    expect(wrapper.text()).toContain('Выплаты')
  })

  it('links to the article page by slug', () => {
    const wrapper = mount(ArticleCard, { props: { article }, global: { stubs } })
    expect(wrapper.find('a').attributes('href')).toBe('/articles/posobiya')
  })

  it('renders "Без категории" fallback', () => {
    const wrapper = mount(ArticleCard, { props: { article: { ...article, category: '' } }, global: { stubs } })
    expect(wrapper.text()).toContain('Без категории')
  })
})