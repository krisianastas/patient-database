<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="flex w-full items-center justify-between gap-3 rounded-2xl border border-theme bg-theme-elevated px-4 py-3 text-left text-sm text-theme transition hover:border-theme-strong focus:border-theme-strong focus:outline-none focus:ring-2 focus:ring-[var(--primary-ring)]"
      @click="toggleOpen"
    >
      <span class="truncate">{{ buttonLabel }}</span>
      <span class="text-xs uppercase tracking-[0.2em] text-theme-muted">{{ isOpen ? 'Close' : 'Open' }}</span>
    </button>

    <div
      v-if="isOpen"
      class="absolute z-20 mt-2 w-full rounded-2xl border border-theme bg-theme-elevated p-3 shadow-2xl"
    >
      <input
        v-model="searchQuery"
        type="text"
        class="mb-3 w-full rounded-xl border border-theme bg-theme-soft px-3 py-2 text-sm text-theme placeholder:text-theme-muted focus:border-theme-strong focus:outline-none focus:ring-2 focus:ring-[var(--primary-ring)]"
        placeholder="Search services"
      />

      <div v-if="filteredOptions.length" class="max-h-64 space-y-2 overflow-y-auto pr-1">
        <label
          v-for="option in filteredOptions"
          :key="option.id"
          class="flex items-center gap-3 rounded-xl border border-theme bg-theme-soft px-3 py-2 text-sm text-theme"
        >
          <input
            :checked="modelValue.includes(option.id)"
            type="checkbox"
            :disabled="readOnly"
            class="h-4 w-4 rounded border-theme bg-theme-elevated text-[var(--primary)] focus:ring-[var(--primary-ring)]"
            @change="toggleSelection(option.id)"
          />
          <span>{{ option.name }}</span>
        </label>
      </div>
      <p v-else class="px-1 py-2 text-sm text-theme-muted">{{ emptySearchText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type Option = {
  id: number
  name: string
}

const props = withDefaults(defineProps<{
  modelValue: number[]
  options: Option[]
  placeholder?: string
  emptyText?: string
  readOnly?: boolean
}>(), {
  placeholder: 'Select services',
  emptyText: 'No services configured yet.',
  readOnly: false
})

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
}>()

const root = ref<HTMLElement | null>(null)
const isOpen = ref(false)
const searchQuery = ref('')

const selectedOptions = computed(() =>
  props.options.filter((option) => props.modelValue.includes(option.id))
)

const buttonLabel = computed(() => {
  if (!props.options.length) {
    return props.emptyText
  }
  if (!selectedOptions.value.length) {
    return props.placeholder
  }
  if (selectedOptions.value.length <= 2) {
    return selectedOptions.value.map((option) => option.name).join(', ')
  }
  return `${selectedOptions.value.length} services selected`
})

const filteredOptions = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) {
    return props.options
  }
  return props.options.filter((option) => option.name.toLowerCase().includes(query))
})

const emptySearchText = computed(() => {
  if (!props.options.length) {
    return props.emptyText
  }
  return 'No services match your search.'
})

const toggleOpen = () => {
  isOpen.value = !isOpen.value
  if (!isOpen.value) {
    searchQuery.value = ''
  }
}

const toggleSelection = (id: number) => {
  if (props.readOnly) {
    return
  }
  if (props.modelValue.includes(id)) {
    emit('update:modelValue', props.modelValue.filter((value) => value !== id))
    return
  }
  emit('update:modelValue', [...props.modelValue, id])
}

const handleClickOutside = (event: MouseEvent) => {
  if (!root.value) {
    return
  }
  const target = event.target
  if (target instanceof Node && !root.value.contains(target)) {
    isOpen.value = false
    searchQuery.value = ''
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
