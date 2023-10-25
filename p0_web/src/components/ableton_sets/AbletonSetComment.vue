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
        <div class="modal-header">
          <h5 class="modal-title">{{ abletonSet.path_info.name }} comment</h5>
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
import {notify} from '@/utils/utils'
import {apiService} from "@/utils/apiService";
import {AbletonSet} from "@/components/ableton_sets/ableton_sets";


export default defineComponent({
  name: 'AbletonSetComment',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
  },
  data() {
    return {
      comment: this.abletonSet.metadata.comment
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
      await apiService.put(`/set/${encodeURI(this.abletonSet?.path_info.filename)}`, {comment: this.comment})
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