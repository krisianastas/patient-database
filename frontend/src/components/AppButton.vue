<template>
  <component
    :is="componentTag"
    :to="to"
    :type="type"
    :disabled="disabled"
    class="inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary-ring)]"
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
      return 'border border-theme text-theme hover:border-theme-strong'
    case 'danger':
      return 'bg-[var(--danger)] text-white hover:bg-[var(--danger-strong)]'
    default:
      return 'bg-[var(--primary)] text-white hover:bg-[var(--primary-strong)]'
  }
})

const disabledClasses = computed(() =>
  props.disabled ? 'cursor-not-allowed opacity-60' : ''
)
</script>
