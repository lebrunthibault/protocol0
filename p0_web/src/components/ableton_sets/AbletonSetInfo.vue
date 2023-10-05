<template>
  <button @click="showSetInfo" type="button" class="btn btn-lg btn-light">
    <i class="fa-solid fa-info" data-toggle="tooltip" data-placement="top" title="Show set info"></i>
  </button>
  <div class="modal" id="setInfoModal" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ abletonSet.name }} <small>({{ modifiedSince }})</small></h5>
        </div>
        <div class="modal-body">
          <ol class="list-group list-group-flush">
            <li class="list-group-item">
              <i class="fa-solid fa-info ms-1" style="width: 22px"></i>
              {{ basename(abletonSet.filename) }} : {{ timeStampToDate(abletonSet.saved_at) }}
            </li>
            <li class="list-group-item">
              <i class="fa-solid fa-volume-low" style="width: 30px"></i>
              <span v-if="abletonSet.audio">
                {{ basename(abletonSet.audio.filename) }} : {{ timeStampToDate(abletonSet.audio.saved_at) }}
                <span class="badge bg-warning float-right ms-3" v-if="abletonSet.audio.outdated">Outdated</span>
              </span>
              <span v-else>No Audio</span>
            </li>
            <li class="list-group-item">
              <i class="fa-solid fa-bars" style="width: 30px"></i>
              <span v-if="abletonSet.metadata">{{ basename(abletonSet.metadata.filename) }} : {{ timeStampToDate(abletonSet.metadata.saved_at) }}</span>
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

export default defineComponent({
  name: 'AbletonSetInfo',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
  },
  computed: {
    modifiedSince(): string {
      const savedAt = moment(this.abletonSet?.saved_at * 1000)

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
    basename(filename: string): string {
      return filename.split('/').reverse()[0].split("\\").reverse()[0]
    },
    timeStampToDate(ts: number): string {
      return (new Date(ts * 1000)).toLocaleString()
    }
  }
})
</script>