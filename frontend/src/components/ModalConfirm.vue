<template>
  <teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" @click="$emit('cancel')"></div>
      <div class="relative z-10 w-[90vw] max-w-md rounded-2xl border border-white/10 bg-slate-950 p-6 shadow-2xl">
        <p class="text-lg font-semibold text-white">{{ title }}</p>
        <p class="mt-2 text-sm text-slate-400">{{ message }}</p>
        <div class="mt-6 flex flex-wrap items-center justify-end gap-3">
          <AppButton variant="ghost" type="button" @click="$emit('cancel')">Cancel</AppButton>
          <AppButton variant="danger" type="button" @click="$emit('confirm')">Confirm</AppButton>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import AppButton from './AppButton.vue'

defineEmits(['cancel', 'confirm'])

defineProps({
  open: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirm action'
  },
  message: {
    type: String,
    default: ''
  }
})
</script>
