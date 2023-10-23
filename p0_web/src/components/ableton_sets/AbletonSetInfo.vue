<template>
  <button @click="showSetInfo" type="button" class="btn btn-lg btn-light">
    <i class="fa-solid fa-info" data-toggle="tooltip" data-placement="top" title="Show set info"></i>
  </button>
  <div class="modal" id="setInfoModal" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header d-flex">
          <h5 class="modal-title">{{ abletonSet.path_info.name }} <small>({{ modifiedSince }})</small></h5>
          <button v-if="!abletonSet.metadata?.stars || abletonSet.metadata?.stars < 3"
                  @click="deleteSet" type="button" class="btn btn-lg btn-light">
            <i class="fa-regular fa-trash-can" data-toggle="tooltip" data-placement="top" title="Move set to trash"></i>
          </button>
        </div>
        <div class="modal-body">
          <form action="" @submit.prevent="submit">
            <div class="form-group">
              <label for="name">Set name</label>
              <input v-model="name" type="text" class="form-control" id="name">
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
import moment from 'moment';
import {basename, notify} from '@/utils/utils'
import {apiService} from "@/utils/apiService";


export default defineComponent({
  name: 'AbletonSetInfo',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
  },
  data() {
    return {
      name: this.abletonSet?.path_info.name
    }
  },
  watch: {
    abletonSet() {
      this.name = this.abletonSet?.path_info.name
    }
  },
  computed: {
    modifiedSince(): string {
      const savedAt = moment(this.abletonSet?.path_info.saved_at * 1000)

      let measurement = "month"
      let count = moment().diff(savedAt, "months")

      if (count >= 24) {
        count /= 12
        measurement = "year"
      }

      if (count < 2) {
        count = moment().diff(savedAt, "days")
        measurement = "day"
      }

      if (count !== 1) {
        measurement += "s"
      }

      return `${count} ${measurement} ago`
    }
  },
  methods: {
    showSetInfo() {
      $('#setInfoModal').modal('show')
    },
    async submit() {
      await apiService.put(`/set/${encodeURI(this.abletonSet?.path_info.filename)}`, {name: this.name})
      this.abletonSet.path_info.name = this.name
      notify("Set renamed")
      // $('#setInfoModal').modal('hide')
    },
    basename,
    timeStampToDate(ts: number): string {
      return (new Date(ts * 1000)).toLocaleString()
    },
    async deleteSet() {
      await apiService.delete(`/set?path=${this.abletonSet?.path_info.filename}`)
      notify("Set moved to trash")
    }
  }
})
</script>