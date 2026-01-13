<template>
  <div class="min-h-screen bg-slate-950 text-slate-100">
    <div class="pointer-events-none fixed inset-0 opacity-50">
      <div class="absolute -top-40 left-1/2 h-96 w-[36rem] -translate-x-1/2 rounded-full bg-indigo-500/30 blur-3xl"></div>
      <div class="absolute -bottom-40 right-[-10rem] h-80 w-80 rounded-full bg-fuchsia-500/20 blur-3xl"></div>
    </div>
    <div class="relative">
      <slot />
    </div>
  </div>
</template>
