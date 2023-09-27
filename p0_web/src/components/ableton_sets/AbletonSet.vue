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
        <button @click="goToScene" type="button" class="btn btn-lg btn-light">
          {{ this.currentScene?.name }} <i class="fa-solid fa-arrow-down-long" data-toggle="tooltip" data-placement="top" title="Go to Scene"></i>
        </button>
        <button @click="showScene(this.currentScene)" type="button" class="btn btn-lg btn-light" data-bs-toggle="modal" data-bs-target="#sceneModal">
          <i class="fa-solid fa-bars" data-toggle="tooltip" data-placement="top" title="Show scene details"></i>
        </button>
      </div>
    </div>
    <div id="waveform"></div>
  </div>
  <div v-else>No wav</div>
  <div v-if="abletonSet.metadata">
    <h2>Scenes</h2>
    <table class="table">
      <thead>
        <tr>
          <th scope="col" style="width: 25%">Name</th>
          <th scope="col" style="width: 10%">Time</th>
          <th scope="col" style="width: 65%">Audio</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(sceneData, i) in abletonSet.metadata.scenes" ref="scenes" :key="i" :class="{'table-warning': sceneData.index === currentScene?.index}">
          <td>
            <button type="button" @click="showScene(sceneData)" class="btn btn-default"
               data-bs-toggle="modal" data-bs-target="#sceneModal"
            >
              {{ sceneData.name }}
            </button>
          </td>
          <td>
            <a href="#" :ref="'input-' + sceneData.index" class="inactive-link">
              {{ toTime(sceneData.start_time) }}
            </a>
          </td>
          <td>
            <div @click="playScene(sceneData)" :id="'waveform-' + sceneData.index" style="width: 950px !important"></div>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="modal" id="sceneModal" tabindex="-1" role="dialog" v-if="currentScene">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ currentScene.name }}</h5>
            <button type="button" class="close" data-bs-dismiss="modal" aria-label="Close">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div class="modal-body">
            <ul>
              <li v-for="(trackName, i) in currentScene.track_names" :key="i"> {{ trackName }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else>No metadata</div>
</template>

<script lang="ts">
import { PropType } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import WaveSurferRegions from 'wavesurfer.js/plugins/regions'
import { defineComponent } from "vue";
import { onKeyStroke } from '@vueuse/core'
import { apiService } from '@/utils/apiService'


export default defineComponent({
  name: 'AbletonSet',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
  },
  data: () => ({
    wavesurfer: null as WaveSurfer | null,
    sceneWs: [] as WaveSurfer[],
    currentWs: null as WaveSurfer | null,
    currentScene: null as SceneData | null
  }),
  computed: {
    scenes(): SceneData[] {
      return this.abletonSet?.metadata.scenes
    }
  },
  methods: {
    getCurrentScene(): SceneData | null {
      if (!this.abletonSet?.metadata || !this.wavesurfer) {
        return null
      }

      for (const sceneData of this.scenes) {
        if (sceneData.end_time > this.wavesurfer?.getCurrentTime()) {
          return sceneData
        }
      }

      return null
    },
    toTime(seconds: number) {
      return new Date(seconds * 1000).toISOString().substring(14, 19)
    },
    async openInExplorer() {
      await apiService.fetch(`/open_in_explorer?path=${this.abletonSet?.path}`)
    },
    async openSet() {
      await apiService.fetch(`/set/open?path=${this.abletonSet?.path}`)
    },
    playPause() {
      const isPlaying = this.wavesurfer?.isPlaying() || this.sceneWs.some(s => s.isPlaying())

      if (isPlaying) {
        this.pause()
      } else if (this.currentWs) {
        this.currentWs.play()
      }
    },
    pause() {
      if (this.currentWs) {
        this.currentWs.pause()
      }
    },
    goToScene() {
      this.$refs[`input-` + this.currentScene.index][0].focus()
    },
    showScene(sceneData: SceneData) {
      this.currentScene = sceneData
    },
    playScene(sceneData: SceneData) {
      if (!this.wavesurfer) {
        return
      }

      const ws = this.sceneWs[sceneData.index]
      if (!ws) {
        return
      }

      this.pause()

      ws.play()
      ws.setTime(sceneData.start_time)
      this.currentWs = ws
    }
  },
  mounted() {
    if (!this.abletonSet?.audio_url) {
      return
    }

    this.wavesurfer = WaveSurfer.create({
      container: '#waveform',
      url: this.abletonSet?.audio_url,
      waveColor: '#227DD8',
      progressColor: '#0B2E50',
      barHeight: 1,
      mediaControls: true,
      dragToSeek: true,
      normalize: true
    })

    this.wavesurfer.once('interaction', () => {
      this.wavesurfer.play()
    })

    this.wavesurfer.on('interaction', () => {
      if (this.currentWs && this.currentWs != this.wavesurfer) {
        this.pause()
      }
      this.currentWs = this.wavesurfer
    })

    this.wavesurfer.on('play', () => {
      this.currentWs = this.wavesurfer
    })

    onKeyStroke(' ', (e: any) => {
      e.preventDefault()
      this.playPause()
    }, {passive: false})

    onKeyStroke('ArrowLeft', (e: any) => {
      if (e.altKey) {
        return // don't catch back navigation
      }
      this.wavesurfer?.skip(-5)
    })

    onKeyStroke('ArrowRight', (e: any) => {
      e.preventDefault()
      this.wavesurfer?.skip(5)
    })

    if (this.abletonSet.metadata) {
      /** On audio position change, fires continuously during playback */
        this.currentScene = this.scenes[0]
        this.wavesurfer.on('timeupdate', () => {
          this.currentScene  = this.getCurrentScene()
        })

        for (const sceneData of this.scenes) {
          const wavesurfer = WaveSurfer.create({
            container: `#waveform-${sceneData.index}`,
            url: this.abletonSet?.audio_url,
            waveColor: '#227DD8',
            progressColor: '#0B2E50',
            height: 50,
            minPxPerSec: 20,
            autoCenter: true,
            dragToSeek: true,
          })

          const wsRegions = wavesurfer.registerPlugin(WaveSurferRegions.create())

          wavesurfer.on('ready', () => {
            wsRegions.addRegion({
              content: 'Start',
              start: sceneData.start_time,
              color: 'rgba(199,49,49,0.18)',
            })
            wsRegions.addRegion({
              content: 'End',
              start: sceneData.end_time,
              color: 'rgba(199,49,49,0.18)',
            })

            wavesurfer.setTime(sceneData.start_time)
          })

          wavesurfer.on("play", () => {
            this.currentScene = sceneData
          })

          this.sceneWs.push(wavesurfer)
        }
    }
  }
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
