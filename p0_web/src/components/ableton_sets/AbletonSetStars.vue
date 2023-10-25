<template>
  <div class="d-inline-flex align-items-center me-3">
      <i
          v-for="i in [1, 2, 3, 4, 5]" :key="i"
          @mouseover="stars = i"
          @mouseleave="stars = abletonSet.metadata.stars"
          @click="save"
          class="fa-star mx-1 ms-2 fa-lg"
          :class="{'fa-solid': stars && stars >= i, 'fa-regular': !stars || stars < i}"
      ></i>
  </div>
</template>

<script lang="ts">
import {defineComponent, PropType} from "vue";
import {apiService} from '@/utils/apiService';
import {notify} from '@/utils/utils';
import {AbletonSet} from "@/components/ableton_sets/ableton_sets";


export default defineComponent({
  name: 'AbletonSetStars',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
  },
  data() {
    return {
      stars: this.abletonSet.metadata.stars
    }
  },
  watch: {
    abletonSet() {
      this.stars = this.abletonSet?.metadata.stars
    }
  },
  methods: {
    async save() {
      await apiService.put(`/set/${encodeURI(this.abletonSet?.path_info.filename)}`, {stars: this.stars})
      this.abletonSet.metadata.stars = this.stars
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