// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  devtools: { enabled: false },
  modules: [
    '@nuxt/ui',
    '@nuxt/eslint',
  ],
  components: [
    {
      path: '~/components',
      pathPrefix: false,
    },
  ],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      appName: process.env.NUXT_PUBLIC_APP_NAME || 'СтудСемья',
    },
  },
  app: {
    head: {
      title: 'СтудСемья — помощь студенческим семьям',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Информационный портал о льготах и поддержке студенческих семей.',
        },
      ],
    },
  },
  colorMode: {
    preference: 'light',
    fallback: 'light',
  },
  tailwindcss: {
    cssPath: ['~/assets/css/main.css', { injectPosition: 'first' }],
  },
})