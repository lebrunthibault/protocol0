<template>
  <button @click="showSetInfo" type="button" class="btn btn-lg btn-light">
    <i class="fa-solid fa-info" data-toggle="tooltip" data-placement="top" title="Show set info"></i>
  </button>
  <div class="modal" id="setInfoModal" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header d-flex">
          <h5 class="modal-title">{{ abletonSet.path_info.name }} <small>({{ modifiedSince }})</small></h5>
          <div>
            <button v-if="abletonSet.audio"
                @click="prepareForSoundCloud" type="button" class="btn btn-lg btn-light mx-2">
              <i class="fa-brands fa-soundcloud" data-toggle="tooltip" data-placement="top" title="Export to mp3"></i>
            </button>
            <button v-if="!abletonSet.path_info.has_own_folder"
                    @click="createSetFolder" type="button" class="btn btn-lg btn-light mx-2">
              <i class="fa-solid fa-folder-plus" data-toggle="tooltip" data-placement="top" title="Create set folder"></i>
            </button>
            <button v-if="canArchive"
                    @click="archiveSet" type="button" class="btn btn-lg btn-light mx-2">
              <i class="fa-solid fa-box-archive" data-toggle="tooltip" data-placement="top" title="Archive set"></i>
            </button>
            <button v-if="canUnArchive"
                    @click="unArchiveSet" type="button" class="btn btn-lg btn-light mx-2">
              <i class="fa-solid fa-trash-arrow-up" data-toggle="tooltip" data-placement="top" title="Restore set"></i>
            </button>
            <button v-if="canDelete"
                    @click="deleteSet" type="button" class="btn btn-lg btn-outline-danger mx-2">
              <i class="fa-regular fa-trash-can" data-toggle="tooltip" data-placement="top" title="Delete set"></i>
            </button>
          </div>
        </div>
        <div class="modal-body my-1">
          <form action="" @submit.prevent="submit">
            <div v-if="abletonSet.metadata" class="mb-3">
              {{ abletonSet.metadata.tempo }} BPM, {{ barLength }} bars
            </div>
            <div class="btn-group" role="group">
              <input type="radio" class="btn-check" name="stage_idea" id="stage_idea" autocomplete="off"
                     v-model="stage" value="IDEA" :checked="stage === 'IDEA'">
              <label class="btn btn-outline-primary" for="stage_idea">Idea</label>

              <input type="radio" class="btn-check" name="stage_track" id="stage_track" autocomplete="off"
                     v-model="stage" value="TRACK" :checked="stage === 'TRACK'">
              <label class="btn btn-outline-primary" for="stage_track">Track</label>

              <input type="radio" class="btn-check" name="stage_release" id="stage_release" autocomplete="off"
                     v-model="stage" value="RELEASE" :checked="stage === 'RELEASE'">
              <label class="btn btn-outline-primary" for="stage_release">Release</label>
            </div>
            <div class="form-group mt-3">
              <label for="name">Set name</label>
              <input v-model="name" type="text" class="form-control" id="name">
            </div>
            <button type="submit" class="btn btn-primary mt-4">Ok</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">

import {defineComponent, PropType} from "vue";
import moment from 'moment';
import {notify} from '@/utils/utils'
import api from "@/utils/api";
import localApi from '@/utils/localApi'
import {AbletonSet, AbletonSetPlace} from '@/components/ableton_sets/ableton_sets';



export default defineComponent({
  name: 'AbletonSetInfo',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
  },
  emits: ['setMoved'],
  data() {
    return {
      name: this.abletonSet?.path_info.name,
      stage: this.abletonSet?.metadata?.stage
    }
  },
  watch: {
    abletonSet() {
      this.name = this.abletonSet?.path_info.name
      this.stage = this.abletonSet?.metadata?.stage
    },
    async stage() {
      await api.put(`/set/?filename=${encodeURIComponent(this.abletonSet?.path_info.relative_name)}`, {stage: this.stage})
      this.abletonSet.metadata.stage = this.stage
    }
  },
  computed: {
    barLength(): number {
        if (!this.abletonSet.metadata || !this.abletonSet.metadata?.scenes.length) {
          return 0
        }

        return this.abletonSet.metadata.scenes.at(-1).end / 4
    },
    canArchive(): boolean {
      return this.abletonSet.place == AbletonSetPlace.TRACKS && (this.abletonSet.metadata.stars < 4)
    },
    canUnArchive(): boolean {
      return this.abletonSet.place == AbletonSetPlace.ARCHIVE && (this.abletonSet.metadata.stars < 4)
    },
    canDelete(): boolean {
      return this.abletonSet.place == AbletonSetPlace.ARCHIVE && (this.abletonSet.metadata.stars < 4)
    },
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
      await api.put(`/set/?filename=${encodeURIComponent(this.abletonSet?.path_info.relative_name)}`, {name: this.name})
      this.abletonSet.path_info.relative_name = this.abletonSet.path_info.relative_name.replace(this.abletonSet.path_info.name, this.name)
      this.abletonSet.path_info.name = this.name
      $('#setInfoModal').modal('hide')
    },
    async prepareForSoundCloud() {
      await localApi.post(`/set/prepare_for_soundcloud?path=${this.abletonSet?.path_info.relative_name}`)
      notify("Set exported to mp3")
      $('#setInfoModal').modal('hide')
    },
    async createSetFolder() {
      await api.post(`/set/create_folder?path=${this.abletonSet?.path_info.relative_name}`)
      notify("Set folder created")
      $('#setInfoModal').modal('hide')
    },
    async archiveSet() {
      await api.post(`/set/archive?path=${this.abletonSet?.path_info.relative_name}`)
      this.$emit('setMoved', this.abletonSet)
      notify("Set archived")
      $('#setInfoModal').modal('hide')
    },
    async unArchiveSet() {
      await api.post(`/set/un_archive?path=${this.abletonSet?.path_info.relative_name}`)
      this.$emit('setMoved', this.abletonSet)
      notify("Set restored")
      $('#setInfoModal').modal('hide')
    },
    async deleteSet() {
      await api.delete(`/set?path=${this.abletonSet?.path_info.relative_name}`)
      this.$emit('setMoved', this.abletonSet)
      notify("Set moved to trash")
      $('#setInfoModal').modal('hide')
    }
  }
})
</script>