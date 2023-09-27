<template>
  <div class="row">
    <div v-for="(category, i) in ['palettes', 'paused', 'tracks']" :key="i" class="col-sm px-5">
      <h2 class="text-center mb-4">{{category}}</h2>
      <div class="list-group list-group-flush">
        <button  v-for="(abletonSet, j) in abletonSets[category]" :key="j" @click="selectSet(abletonSet)"
           type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
        >
          {{ abletonSet.name }}

          <div>
            <span class="badge rounded-pill bg-success mx-1">
            <i class="fa-solid fa-volume-high" v-if="abletonSet.audio_url"></i>
          </span>
          <span class="badge rounded-pill bg-secondary">
            <i class="fa-solid fa-bars" v-if="abletonSet.metadata"></i>
          </span>
          </div>

        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { apiService } from '@/utils/apiService'

export default defineComponent({
  name: 'AbletonSets',
  data: () => ({
    abletonSets: {},
  }),
  methods: {
    selectSet(abletonSet: AbletonSet) {
      this.$router.push(`/set?path=${abletonSet.path}`);
    }
  },
  async mounted() {
    this.abletonSets = await apiService.fetch('/sets')
  }
})
</script>

