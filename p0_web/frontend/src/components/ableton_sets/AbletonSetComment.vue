<template>
  <button @click="showSetComment" type="button" class="btn btn-lg btn-light position-relative" id="button">
    <i class="fa-regular fa-comment" data-toggle="tooltip" data-placement="top" title="Update set comment"></i>
    <span v-if="abletonSet.metadata.comment"
      class="position-absolute top-0 start-100 translate-middle p-2 bg-danger border border-light rounded-circle">
    </span>
  </button>
  <div class="modal" id="setCommentModal" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header d-flex">
          <h5 class="modal-title">
            {{ abletonSet.path_info.name }}
          </h5>
          <span v-if="sceneData" class="font-italic">{{ sceneName }}</span>
        </div>
        <div class="modal-body">
          <form action="" @submit.prevent="submit">
            <div class="form-group">
              <textarea v-model="comment" class="form-control" id="comment" rows="15"></textarea>
            </div>
            <button type="submit" class="btn btn-primary mt-2">Ok</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">

import {defineComponent, PropType} from "vue";
import {notify, sceneName} from '@/utils/utils'
import api from "@/utils/api";
import {AbletonSet, SceneData} from "@/components/ableton_sets/ableton_sets";


export default defineComponent({
  name: 'AbletonSetComment',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
    sceneData: Object as PropType<SceneData> | null,
  },
  data() {
    return {
      comment: this.abletonSet.metadata.comment
    }
  },
  computed: {
    sceneName(): string {
      return sceneName(this.sceneData?.name)
    }
  },
  watch: {
    abletonSet() {
      this.comment = this.abletonSet?.metadata.comment
    }
  },
  methods: {
    showSetComment() {
      $('#setCommentModal').modal('show')
    },
    async submit() {
      await api.put(`/set/?filename=${encodeURIComponent(this.abletonSet?.path_info.relative_name)}`, {comment: this.comment})
      this.abletonSet.metadata.comment = this.comment
      notify("Set saved")
      $('#setCommentModal').modal('hide')
    }
  }
})
</script>

<style scoped>
#button {
  z-index: 2
}
</style>