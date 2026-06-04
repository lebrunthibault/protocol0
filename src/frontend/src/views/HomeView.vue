<script setup lang="ts">
import { RouterLink } from "vue-router";
import { DOCS_URL } from "../config";
</script>

<template>
  <section class="home">
    <div class="col home-hero">
      <div class="kicker">Ableton 12 · Windows</div>
      <h1 class="home-title">Your Ableton, on muscle memory.</h1>
      <p class="home-sub">
        Protocol 0 lets you drive Ableton Live from global keyboard shortcuts — remap Ableton shortcuts, use smart actions and add your own.
      </p>

      <RouterLink to="/shortcuts" class="card card--compact home-cta">
        <div class="home-cta-text">
          <div class="label-accent">Keymapper</div>
          <div class="home-cta-title">Manage your keyboard shortcuts →</div>
          <div class="home-cta-desc">
            Record combos, assign actions, and resolve conflicts. Saved instantly to disk.
          </div>
        </div>
      </RouterLink>

      <div class="home-links">
        <a :href="DOCS_URL" target="_blank" rel="noopener" class="btn btn-ghost">Documentation</a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home-hero {
  text-align: center;
}
.home-title {
  font-size: var(--fs-h1);
  font-weight: var(--fw-semibold);
  letter-spacing: var(--ls-tight);
  line-height: var(--lh-tight);
  margin-top: var(--space-4);
}
.home-sub {
  color: var(--muted);
  font-size: var(--fs-lg);
  line-height: var(--lh-relaxed);
  margin: var(--space-5) auto 0;
  max-width: 52ch;
}
.home-cta {
  display: block;
  text-align: left;
  margin-top: var(--space-7);
}
.home-cta-title {
  font-size: var(--fs-xl);
  font-weight: var(--fw-semibold);
  margin-top: var(--space-1);
}
.home-cta-desc {
  color: var(--muted);
  font-size: var(--fs-base);
  margin-top: var(--space-2);
}
.home-links {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  margin-top: var(--space-6);
}
</style>
