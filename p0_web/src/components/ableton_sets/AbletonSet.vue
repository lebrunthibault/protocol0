<template>
  <div class="d-flex flex-row justify-content-between">
    <div></div>
    <h1 class="mb-4 text-center">
      {{ abletonSet.name }}
    </h1>
    <div class="btn-group" role="group">
      <button @click="openInExplorer" type="button" class="btn btn-lg btn-light">
        <i class="fa-solid fa-folder" data-toggle="tooltip" data-placement="top" title="Open in Explorer"></i>
      </button>
    </div>
  </div>

  <div v-if="abletonSet.audio_url" class="mb-4 mt-3">
    <div class="text-center m-4">
      <div class="btn-group" role="group" v-if="abletonSet.metadata">
<!--        <button @click="goToScene" type="button" class="btn btn-lg btn-light">-->
<!--          {{ this.currentScene?.name }} <i class="fa-solid fa-arrow-down-long" data-toggle="tooltip" data-placement="top" title="Go to Scene"></i>-->
<!--        </button>-->
      </div>
    </div>
    <AbletonSetPlayer :ableton-set="abletonSet" @sceneChange="onSceneChange"></AbletonSetPlayer>
  </div>
  <div v-else>No wav</div>
  <AbletonSetDetails :ableton-set="abletonSet" :scene-data="currentScene" v-if="currentScene"></AbletonSetDetails>

<!--  <div v-if="abletonSet.metadata">-->
<!--    <h2>Scenes</h2>-->
<!--    <table class="table">-->
<!--      <thead>-->
<!--        <tr>-->
<!--          <th scope="col" style="width: 25%">Name</th>-->
<!--          <th scope="col" style="width: 10%">Time</th>-->
<!--          <th scope="col" style="width: 65%">Audio</th>-->
<!--        </tr>-->
<!--      </thead>-->
<!--      <tbody>-->
<!--        <tr v-for="(sceneData, i) in abletonSet.metadata.scenes" ref="scenes" :key="i" :class="{'table-warning': sceneData.index === currentScene?.index}">-->
<!--          <td>-->
<!--            <button type="button" @click="showScene(sceneData)" class="btn btn-default">-->
<!--              {{ sceneData.name }}-->
<!--            </button>-->
<!--          </td>-->
<!--          <td>-->
<!--            <a href="#" :ref="'input-' + sceneData.index" class="inactive-link">-->
<!--              {{ toTime(sceneData.start_time) }}-->
<!--            </a>-->
<!--          </td>-->
<!--          <td>-->
<!--            <div @click="playScene(sceneData)" :id="'waveform-' + sceneData.index" style="width: 950px !important"></div>-->
<!--          </td>-->
<!--        </tr>-->
<!--      </tbody>-->
<!--    </table>-->
<!--  </div>-->
<!--  <div v-else>No metadata</div>-->
</template>

<script lang="ts">
import { PropType } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import { defineComponent } from "vue";
import { apiService } from '@/utils/apiService'
import AbletonSetPlayer from "@/components/ableton_sets/AbletonSetPlayer.vue";
import AbletonSetDetails from "@/components/ableton_sets/AbletonSetDetails.vue";


export default defineComponent({
  name: 'AbletonSet',
  components: {AbletonSetDetails, AbletonSetPlayer},
  props: {
    abletonSet: Object as PropType<AbletonSet>,
  },
  data: () => ({
    wavesurfer: null as WaveSurfer | null,
    // sceneWs: [] as WaveSurfer[],
    // currentWs: null as WaveSurfer | null,
    currentScene: null as SceneData | null
  }),
  computed: {
    scenes(): SceneData[] {
      return this.abletonSet?.metadata.scenes
    }
  },
  methods: {
    toTime(seconds: number) {
      return new Date(seconds * 1000).toISOString().substring(14, 19)
    },
    async openInExplorer() {
      await apiService.fetch(`/open_in_explorer?path=${this.abletonSet?.path}`)
    },
    onSceneChange(sceneData: SceneData) {
      this.currentScene = sceneData
    },
    // playPause() {
    //   const isPlaying = this.wavesurfer?.isPlaying() || this.sceneWs.some(s => s.isPlaying())
    //
    //   if (isPlaying) {
    //     this.pause()
    //   } else if (this.currentWs) {
    //     this.currentWs.play()
    //   }
    // },
    // pause() {
    //   if (this.currentWs) {
    //     this.currentWs.pause()
    //   }
    // },
    // goToScene() {
    //   this.$refs[`input-` + this.currentScene.index][0].focus()
    // },
    // playScene(sceneData: SceneData) {
    //   if (!this.wavesurfer) {
    //     return
    //   }
    //
    //   const ws = this.sceneWs[sceneData.index]
    //   if (!ws) {
    //     return
    //   }
    //
    //   this.pause()
    //
    //   ws.play()
    //   ws.setTime(sceneData.start_time)
    //   this.currentWs = ws
    // }
  },
  // mounted() {
  //   if (!this.abletonSet?.audio_url) {
  //     return
  //   }
  //
  //   this.wavesurfer.on('interaction', () => {
  //     if (this.currentWs && this.currentWs != this.wavesurfer) {
  //       this.pause()
  //     }
  //     this.currentWs = this.wavesurfer
  //   })
  //
  //   this.wavesurfer.on('play', () => {
  //     this.currentWs = this.wavesurfer
  //   })
  //
  //   if (this.abletonSet.metadata) {
  //       for (const sceneData of this.scenes) {
  //         const wavesurfer = WaveSurfer.create({
  //           container: `#waveform-${sceneData.index}`,
  //           url: this.abletonSet?.audio_url,
  //           waveColor: '#227DD8',
  //           progressColor: '#0B2E50',
  //           height: 50,
  //           minPxPerSec: 20,
  //           autoCenter: true,
  //           dragToSeek: true,
  //         })
  //
  //         const sceneRegions = wavesurfer.registerPlugin(WaveSurferRegions.create())
  //
  //         wavesurfer.on('ready', () => {
  //           sceneRegions.addRegion({
  //             content: 'Start',
  //             start: sceneData.start_time,
  //             color: 'rgba(199,49,49,0.18)',
  //           })
  //           sceneRegions.addRegion({
  //             content: 'End',
  //             start: sceneData.end_time,
  //             color: 'rgba(199,49,49,0.18)',
  //           })
  //
  //           wavesurfer.setTime(sceneData.start_time)
  //         })
  //
  //         wavesurfer.on("play", () => {
  //           this.currentScene = sceneData
  //         })
  //
  //         this.sceneWs.push(wavesurfer)
  //       }
  //   }
  // }
})
</script>

<style scoped>
.inactive-link {
  pointer-events: none;
  cursor: default;
  color: initial;
  text-decoration: none;
}
</style>
