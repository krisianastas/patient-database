<template>
  <div class="overflow-x-auto rounded-2xl border border-white/10 bg-white/5">
    <table class="min-w-[720px] w-full text-left text-sm">
      <thead class="bg-white/5 text-xs uppercase tracking-[0.2em] text-slate-400">
        <tr>
          <th v-for="column in columns" :key="String(column.key)" class="px-6 py-4">
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, rowIndex) in rows"
          :key="getRowKey(row, rowIndex)"
          class="border-t border-white/5"
        >
          <td v-for="column in columns" :key="String(column.key)" class="px-6 py-4">
            <slot :name="`cell-${String(column.key)}`" :row="row">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts" generic="Row extends Record<string, string | number>">
type Column<Row> = {
  key: keyof Row | 'actions'
  label: string
}

const props = withDefaults(
  defineProps<{
    columns: Column<Row>[]
    rows: Row[]
    rowKey?: keyof Row | string
  }>(),
  {
    rowKey: 'id'
  }
)

const getRowKey = (row: Row, index: number): string | number => {
  const keyValue = row[props.rowKey as keyof Row]
  if (keyValue !== undefined) {
    return keyValue
  }
  if (row.id !== undefined) {
    return row.id
  }
  return index
}
</script>
