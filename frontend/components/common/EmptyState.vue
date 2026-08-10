<template>
  <div class="card-sf flex flex-col items-center justify-center py-14 text-center">
    <Icon name="heroicons:document-magnifying-glass" class="mb-4 h-12 w-12 text-slate-300" />
    <h3 class="text-lg font-semibold text-slate-900">{{ title }}</h3>
    <p class="mt-2 max-w-md text-sm text-slate-500">{{ description }}</p>
    <div class="mt-4">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()
</script>