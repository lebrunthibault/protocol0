<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4 px-3">
      <router-link to="/" class="nav-item nav-link m-3">
        <img src="@/assets/protocol0_icon.png" width="30" height="30" alt="" />
      </router-link>
    <div class="collapse navbar-collapse d-flex justify-content-between" id="navbarNav">
      <ul class="navbar-nav">
        <li>
          <router-link v-if="$route.query.place" to="/" class="nav-item nav-link m-3">Tracks</router-link>
        </li>
        <li>
          <router-link v-if="$route.query.place != 'archive'" to="/?place=archive" class="nav-item nav-link m-3">Archive</router-link>
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
  name: 'HomeView',
  components: {AbletonSets},
  data: () => ({}),
})
</script>

<style scoped>
.nav-item.active {
  font-weight: bold;
}
</style>
