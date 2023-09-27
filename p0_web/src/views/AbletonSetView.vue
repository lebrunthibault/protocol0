<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4 px-3">
    <a class="navbar-brand" href="/">
      <img src="@/assets/protocol0_icon.png" width="30" height="30" alt="" />
    </a>
  </nav>
  <AbletonSet v-if="abletonSet" :ableton-set="abletonSet"></AbletonSet>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import AbletonSet from "@/components/ableton_sets/AbletonSet.vue";
import {apiService} from "@/utils/apiService";

export default defineComponent({
  name: 'AbletonSetView',
  components: {AbletonSet},
  data: () => ({
    abletonSet: null as AbletonSet | null,
  }),
  async mounted() {
    this.abletonSet = await apiService.fetch(`/set?path=${this.$route.query.path}`)
    console.log(this.abletonSet)
    if (this.abletonSet?.metadata) {
      for (const i in this.abletonSet.metadata.scenes) {
        this.abletonSet.metadata.scenes[i].index = parseInt(i)
      }
    }
  }})
</script>
