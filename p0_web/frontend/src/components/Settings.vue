<template>
<!--  <button @click="ShowSettings" type="button" class="btn btn-lg btn-light position-relative" id="button">-->
<!--    <i class="fa-solid fa-gear" data-toggle="tooltip" data-placement="top" title="Access settings"></i>-->
<!--  </button>-->
  <div class="modal" id="settingsModal" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header d-flex">
          <h5 class="modal-title">
            Settings
          </h5>
        </div>
        <div class="modal-body">
          <form action="" @submit.prevent="submit">
            <div class="form-group">
              <label for="tracks-directory">Tracks directory</label>
              <input type="text" v-model="settings.tracks_directory" class="form-control" id="tracks-directory">
            </div>
            <button type="submit" class="btn btn-primary mt-2">Ok</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">

import {defineComponent} from "vue";
import {notify} from '@/utils/utils'
import {apiService} from "@/utils/apiService";


export default defineComponent({
  name: 'AbletonSetComment',
  data() {
    return {
      settings: {}
    }
  },
  methods: {
    ShowSettings() {
      $('#settingsModal').modal('show')
    },
    async submit() {
      // save in localStorage
      await apiService.put(`/settings/`, this.settings)
      notify("Set saved")
      // $('#settingsModal').modal('hide')
    }
  },
  async mounted() {
    this.settings = await apiService.get("/settings")
    console.log(this.settings)
  }
})
</script>

<style scoped>
#button {
  z-index: 2
}
</style>