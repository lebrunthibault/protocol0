<script setup lang="ts">
import { RouterLink } from "vue-router";
import { DOCS_URL } from "../config";
import StatusPill from "./StatusPill.vue";
</script>

<template>
  <header>
    <div class="wrap">
      <nav class="nav">
        <RouterLink to="/" class="brand">
          <span class="dot">P0</span>
          <span>Protocol 0</span>
        </RouterLink>
        <div class="nav-links">
          <RouterLink to="/shortcuts">Keymapper</RouterLink>
          <RouterLink to="/api-docs">API docs</RouterLink>
          <a :href="DOCS_URL" target="_blank" rel="noopener">Docs</a>
        </div>
        <div class="nav-right">
          <StatusPill />
        </div>
      </nav>
    </div>
  </header>
</template>
