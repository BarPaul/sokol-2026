<template>
  <div>
    <ArticleForm :article-id="null" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'editor', middleware: 'editor' })
</script>