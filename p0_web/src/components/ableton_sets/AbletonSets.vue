<template>
  <div v-if="selectedSet" class="row mb-4">
    <div class="d-flex flex-row justify-content-between mb-3">
      <div></div>
      <h3 class="mb-4 text-center">
        {{ selectedSet.path_info.name }}
      </h3>
      <div class="btn-group" role="group">
        <AbletonSetSceneData
            :ableton-set="selectedSet"  :scene-data="currentScene" v-if="currentScene"
            @scene-skip="onSceneSkip"
        ></AbletonSetSceneData>
        <AbletonSetInfo :ableton-set="selectedSet"></AbletonSetInfo>
      </div>
    </div>
      <AbletonSetPlayer :ableton-set="selectedSet" @sceneChange="onSceneChange" :time="playerTime"></AbletonSetPlayer>
  </div>
  <div class="row">
    <div v-for="(setFolder, i) in setFolders" :key="i" class="col-sm px-5">
      <h2 class="text-center mb-4">{{ setFolder }}</h2>
      <div class="list-group list-group-flush">
        <div v-for="(abletonSet, j) in getSetsFromFolder(setFolder)" :key="j"
             class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
        >
          <div @click="selectSet(abletonSet)" class="flex-grow-1 btn" style="text-align: left">
            {{ abletonSet.path_info.name }}
          </div>
          <div>
            <span  @click="selectSet(abletonSet)" class="badge rounded-pill mx-1"
                  :class="{'bg-success': !abletonSet.audio_info?.outdated, 'bg-warning': abletonSet.audio_info?.outdated}">
              <i class="fa-solid fa-volume-high"></i>
            </span>
            <span @click="selectSet(abletonSet)" class="badge rounded-pill bg-secondary">
              <i class="fa-solid fa-bars" v-if="abletonSet.metadata_info"></i>
            </span>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { apiService } from '@/utils/apiService'
import AbletonSetPlayer from "@/components/ableton_sets/AbletonSetPlayer.vue";
import AbletonSetSceneData from "@/components/ableton_sets/AbletonSetSceneData.vue";
import AbletonSetInfo from "@/components/ableton_sets/AbletonSetInfo.vue";


export default defineComponent({
  name: 'AbletonSets',
  components: {AbletonSetInfo, AbletonSetPlayer, AbletonSetSceneData},
  data: () => ({
    abletonSets: {},
    selectedSet: null as AbletonSet | null,
    currentScene: null as SceneData | null,
    playerTime: 0,
  }),
  computed: {
    setFolders() {
        if (this.showArchives) {
          return ['_released', 'paused']
        } else {
          return ['drafts', 'tracks']
        }
    },
    showArchives(): boolean {
      return Boolean(this.$route.query.archive)
    }
  },
  methods: {
    getSetsFromFolder(category: string): AbletonSet[] {
      const isSetValid = (abletonSet: AbletonSet) => {
        return !["test", "tests"].includes(abletonSet?.path_info.name.toLowerCase().trim())
      }

      const sets = this.abletonSets[category]
      
      return sets ? this.abletonSets[category].filter(isSetValid) : []
    },
    selectSet(abletonSet: AbletonSet) {
      this.selectedSet = abletonSet
      this.currentScene = this.selectedSet.scene_stats ? this.selectedSet.scene_stats.scenes[0] : null
    },
    async openInExplorer() {
      await apiService.fetch(`/open_in_explorer?path=${this.selectedSet?.path_info.filename}`)
    },
    onSceneChange(sceneData: SceneData) {
      this.currentScene = sceneData
    },
    onSceneSkip(increment: number) {
      this.currentScene = this.selectedSet?.scene_stats.scenes[this.currentScene.index + increment]
      this.playerTime = this.currentScene?.start_time
    }
  },
  async mounted() {
    this.abletonSets = await apiService.fetch('/sets')

    // add index to scenes
    for (const abletonSet of Object.values(this.abletonSets).flat()) {
      if (abletonSet?.scene_stats) {
        for (const i in abletonSet.scene_stats.scenes) {
          abletonSet.scene_stats.scenes[i].index = parseInt(i)
        }
      }
    }
  }
})
</script>

<style scoped lang="scss">
.list-group-item .btn {
  border: hidden;
}
</style>

