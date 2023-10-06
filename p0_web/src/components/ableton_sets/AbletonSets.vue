<template>
  <div v-if="selectedSet" class="row mb-4">
    <div class="d-flex flex-row justify-content-between mb-3">
      <div></div>
      <h3 class="mb-4 text-center">
        {{ selectedSet.path_info.name }}
      </h3>
      <div class="btn-group" role="group">
        <AbletonSetStars :ableton-set="selectedSet" :stars="selectedSet.metadata?.stars"
          @update="sortSets"></AbletonSetStars>
        <AbletonSetSceneData
            :ableton-set="selectedSet"  :scene-data="currentScene" v-if="currentScene"
            @scene-skip="onSceneSkip"
        ></AbletonSetSceneData>
        <AbletonSetInfo :ableton-set="selectedSet"></AbletonSetInfo>
      </div>
    </div>
      <AbletonSetPlayer :ableton-set="selectedSet" @sceneChange="onSceneChange" :time="playerTime"></AbletonSetPlayer>
  </div>
  <div class="row" style="margin-top: 50px">
    <div class="col-sm" style="position: absolute; width: 200px">
      <select class="form-select" v-model="filterType">
        <option selected>Filter sets by</option>
        <option value="name">Name</option>
        <option value="recent">Recent</option>
        <option value="stars">Stars</option>
      </select>
    </div>
    <div v-for="(setFolder, i) in setFolders" :key="i" class="col-sm px-5">
      <h2 class="text-center mb-4">{{ setFolder }}</h2>
      <div class="list-group list-group-flush">
        <div v-for="(abletonSet, j) in getSetsFromFolder(setFolder)" :key="j"
             class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
        >
          <div @click="selectSet(abletonSet)" class="flex-grow-1 btn" style="text-align: left">
            {{ abletonSet.path_info.name }}
          </div>
          <div class="d-flex">
            <div style="width: 45px">
              <span @click="selectSet(abletonSet)" v-if="abletonSet.metadata?.stars"
              >
                {{ abletonSet.metadata.stars }}<i class="fa-solid fa-star ms-2" style="color: #c7b44b"></i>
              </span>
            </div>
            <div style="width: 45px">
              <span @click="selectSet(abletonSet)" class="badge rounded-pill mx-1"
                    :class="{'bg-success': !abletonSet.audio_info?.outdated, 'bg-warning': abletonSet.audio_info?.outdated}"
              >
                <i class="fa-solid fa-volume-high" v-if="abletonSet.audio_info"></i>
              </span>
            </div>
            <div style="width: 45px">
              <span @click="selectSet(abletonSet)" class="badge rounded-pill bg-secondary">
                <i class="fa-solid fa-bars" v-if="abletonSet.metadata"></i>
              </span>
            </div>
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
import AbletonSetStars from "@/components/ableton_sets/AbletonSetStars.vue";


export default defineComponent({
  name: 'AbletonSets',
  components: {AbletonSetStars, AbletonSetInfo, AbletonSetPlayer, AbletonSetSceneData},
  data: () => ({
    abletonSets: {},
    selectedSet: null as AbletonSet | null,
    currentScene: null as SceneData | null,
    playerTime: 0,
    filterType: "stars"
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
  watch: {
    filterType() {
      this.sortSets()
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
      this.currentScene = this.selectedSet.metadata ? this.selectedSet.metadata.scenes[0] : null
    },
    async openInExplorer() {
      await apiService.get(`/open_in_explorer?path=${this.selectedSet?.path_info.filename}`)
    },
    onSceneChange(sceneData: SceneData) {
      this.currentScene = sceneData
    },
    onSceneSkip(increment: number) {
      this.currentScene = this.selectedSet?.metadata.scenes[this.currentScene.index + increment]
      this.playerTime = this.currentScene?.start_time
    },
    sortSets() {
      const getProp = (filterType: string): Function => {
        switch (filterType) {
          case "name":
            return (set: AbletonSet) => set.path_info.name
          case "recent":
            return (set: AbletonSet) => set.path_info.saved_at
          case "stars":
            return (set: AbletonSet) => set.metadata?.stars
        }

        throw new Error(`unknown filter ${filterType}`)
      }
      const getPredicate = (getProp: Function, filterType: string): Function => {
          if (filterType === "name") {
            return (a: AbletonSet, b: AbletonSet) => getProp(a) > getProp(b) ? 1: - 1
          } else {
            return (a: AbletonSet, b: AbletonSet) => getProp(a) < getProp(b) ? 1: - 1
          }
      }
      for (const category in this.abletonSets) {
        this.abletonSets[category].sort(getPredicate(getProp(this.filterType), this.filterType))
      }
    }
  },
  async mounted() {
    this.abletonSets = await apiService.get('/sets')

    // add index to scenes
    for (const abletonSet of Object.values(this.abletonSets).flat()) {
      if (abletonSet?.metadata) {
        for (const i in abletonSet.metadata.scenes) {
          abletonSet.metadata.scenes[i].index = parseInt(i)
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

