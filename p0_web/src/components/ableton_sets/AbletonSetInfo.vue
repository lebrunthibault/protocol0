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
          <ol class="list-group list-group-flush">
            <li class="list-group-item">
              <i class="fa-solid fa-info ms-1" style="width: 22px"></i>
              {{ basename(abletonSet.path_info.filename) }} : {{ timeStampToDate(abletonSet.path_info.saved_at) }}
            </li>
            <li class="list-group-item">
              <i class="fa-solid fa-volume-low" style="width: 30px"></i>
              <span v-if="abletonSet.audio_info">
                {{
                  basename(abletonSet.audio_info.filename)
                }} : {{ timeStampToDate(abletonSet.audio_info.saved_at) }}
                <span class="badge bg-warning float-right ms-3" v-if="abletonSet.audio_info.outdated">Outdated</span>
              </span>
              <span v-else>No Audio</span>
            </li>
            <li class="list-group-item">
              <i class="fa-solid fa-bars" style="width: 30px"></i>
              <span v-if="abletonSet.metadata.path_info">{{
                  basename(abletonSet.metadata.path_info.filename)
                }} : {{ timeStampToDate(abletonSet.metadata.path_info.saved_at) }}</span>
              <span v-else>No metadata</span>
            </li>
          </ol>
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