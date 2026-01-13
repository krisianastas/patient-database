<template>
  <component
    :is="componentTag"
    :to="to"
    :type="type"
    :disabled="disabled"
    class="inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400/70"
    :class="[variantClasses, disabledClasses]"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  to: {
    type: [String, Object],
    default: null
  },
  type: {
    type: String,
    default: 'button'
  }
})

const componentTag = computed(() => (props.to ? RouterLink : 'button'))

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'ghost':
      return 'border border-white/15 text-slate-200 hover:border-white/40 hover:text-white'
    case 'danger':
      return 'bg-rose-500/80 text-white hover:bg-rose-500'
    default:
      return 'bg-indigo-500/90 text-white hover:bg-indigo-500'
  }
})

const disabledClasses = computed(() =>
  props.disabled ? 'cursor-not-allowed opacity-60 hover:bg-indigo-500/90' : ''
)
</script>
