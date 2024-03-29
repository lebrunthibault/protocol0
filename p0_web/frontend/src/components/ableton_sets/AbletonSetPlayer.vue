<template>
    <div id="waveform"></div>
</template>

<script lang="ts">
import { PropType } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import WaveSurferRegions from 'wavesurfer.js/plugins/regions'
import { defineComponent } from "vue";
import { onKeyStroke } from '@vueuse/core'
import {AbletonSet, SceneData} from "@/components/ableton_sets/ableton_sets";
import {sceneName} from "@/utils/utils";


export default defineComponent({
  name: 'AbletonSetPlayer',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
    time: Number,
  },
  data: () => ({
    wavesurfer: null as WaveSurfer | null,
    currentScene: null as SceneData | null
  }),
  watch: {
    // whenever question changes, this function will run
    abletonSet() {
      this.loadWaveform()
    },
    time() {
      this.wavesurfer?.setTime(this.time)
    }
  },
  computed: {
    scenes(): SceneData[] {
      return this.abletonSet?.metadata.scenes
    }
  },
  methods: {
    getCurrentScene(): SceneData | null {
      if (!this.abletonSet?.metadata.scenes || !this.wavesurfer) {
        return null
      }

      for (const sceneData of this.scenes) {
        const beat_duration = 60 / this.abletonSet.metadata.tempo

        if (sceneData.end * beat_duration > this.wavesurfer?.getCurrentTime()) {
          return sceneData
        }
      }

      return null
    },
    loadWaveform() {
      if (!this.abletonSet?.audio?.url) {
        return
      }

      this.wavesurfer?.destroy()

      this.wavesurfer = WaveSurfer.create({
        container: '#waveform',
        url: this.abletonSet?.audio?.url,
        waveColor: '#227DD8',
        progressColor: '#0B2E50',
        barHeight: 1,
        mediaControls: true,
        dragToSeek: true,
        normalize: true
      })

      this.wavesurfer.once('ready', () => {
        this.wavesurfer.play()
      })

      this.wavesurfer.once('interaction', () => {
        this.wavesurfer.play()
      })

      if (this.abletonSet.metadata.scenes && this.abletonSet.metadata.tempo) {
        this.currentScene = this.scenes[0]
        this.$emit("sceneChange", this.currentScene)
        this.wavesurfer.on('timeupdate', () => {
          this.currentScene  = this.getCurrentScene()
          this.$emit("sceneChange", this.currentScene)
        })

        for (const sceneData of this.scenes) {
          const wsRegions = this.wavesurfer.registerPlugin(WaveSurferRegions.create())

          this.wavesurfer.on('ready', () => {
            const beat_duration = 60 / this.abletonSet.metadata.tempo

            wsRegions.addRegion({
              content: sceneName(sceneData.name),
              start: sceneData.start * beat_duration,
              color: 'rgba(199,49,49,0.18)',
            })
          })

          wsRegions.on('region-clicked', (region: any, e: any) => {
            e.stopPropagation() // prevent triggering a click on the waveform
            region.play()
          })
        }
      }
    }
  },
  mounted() {
    this.loadWaveform()
    const modalShown = () => $('#setCommentModal.show').length || $('#setInfoModal.show').length
    onKeyStroke(' ', (e: any) => {
      if (modalShown()) {
        return
      }
      e.preventDefault()
      this.wavesurfer?.playPause()
    }, {passive: false})

    onKeyStroke('ArrowLeft', (e: any) => {
      if (modalShown()) {
        return
      }
      if (e.altKey) {
        return // don't catch back navigation
      }
      this.wavesurfer?.skip(-5)
    })

    onKeyStroke('ArrowRight', (e: any) => {
      if (modalShown()) {
        return
      }
      e.preventDefault()
      this.wavesurfer?.skip(5)
    })
  }
})
</script>
