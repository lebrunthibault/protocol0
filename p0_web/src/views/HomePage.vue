<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4 px-3">
    <a class="navbar-brand" href="#">
      <img src="@/assets/protocol0_icon.png" width="30" height="30" alt="" />
    </a>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
        <li>
          <router-link to="/actions" class="nav-item nav-link m-3">Actions</router-link>
        </li>
      </ul>
    </div>
  </nav>
  <div class="container">
    <AbletonSets></AbletonSets>
  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import AbletonSets from "@/components/ableton_sets/AbletonSets.vue";

export default defineComponent({
  name: 'HomePage',
  components: {AbletonSets},
  data: () => ({}),
})
</script>

<style scoped>
.nav-item.active {
  font-weight: bold;
}
</style>
