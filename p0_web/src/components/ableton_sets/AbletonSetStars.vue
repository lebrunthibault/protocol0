<template>
  <div class="d-inline-flex align-items-center me-3">
      <i
          v-for="i in [1, 2, 3, 4, 5]" :key="i"
          @mouseover="starCount = i"
          @mouseleave="starCount = stars"
          @click="save"
          class="fa-star mx-1 ms-2 fa-lg"
          :class="{'fa-solid': starCount && starCount >= i, 'fa-regular': !starCount || starCount < i}"
      ></i>
  </div>
</template>

<script lang="ts">
import {defineComponent, PropType} from "vue";
import { apiService } from '@/utils/apiService';
import { notify } from '@/utils/utils';


export default defineComponent({
  name: 'AbletonSetStars',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
    stars: Number,
  },
  data() {
    return {
      starCount: this.stars
    }
  },
  watch: {
    stars() {
      this.starCount = this.stars
    }
  },
  methods: {
    async save() {
      this.abletonSet.metadata.stars = this.starCount
      await apiService.post(`/set/${encodeURI(this.abletonSet?.path_info.filename)}/stars`, {stars: this.starCount})
      notify("Set saved")
      this.$emit("update")
    }
  },
})
</script>

<style scoped lang="scss">
.fa-solid {
  color: #c7b44b;
}
</style>