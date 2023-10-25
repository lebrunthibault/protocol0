<template>
  <div v-if="selectedSet" class="row mb-4">
    <div class="d-flex flex-row justify-content-between mb-3">
      <div></div>
      <h3 class="mb-4 text-center">
        {{ selectedSet.path_info.name }}
      </h3>
      <div class="btn-group" role="group">
        <AbletonSetStars :ableton-set="selectedSet"
          @update="sortSets"></AbletonSetStars>
        <AbletonSetSceneData
            :ableton-set="selectedSet"  :scene-data="currentScene" v-if="currentScene"
            @scene-skip="onSceneSkip"
        ></AbletonSetSceneData>
        <AbletonSetInfo :ableton-set="selectedSet" @set-moved="hideSet"></AbletonSetInfo>
        <AbletonSetComment :ableton-set="selectedSet"></AbletonSetComment>
        <button @click="openSet" type="button" class="btn btn-lg btn-light">
          <i class="fa-solid fa-up-right-from-square" data-toggle="tooltip" data-placement="top" title="Open in Ableton"></i>
        </button>
      </div>
    </div>
      <AbletonSetPlayer v-if="selectedSet.audio" :ableton-set="selectedSet" @sceneChange="onSceneChange" :time="playerTime"></AbletonSetPlayer>
      <h3 v-else class="text-center alert alert-warning">No audio <i class="px-3 fa-solid fa-volume-xmark"></i></h3>
  </div>
  <div class="row" style="margin-top: 50px">
    <div class="col-sm" style="position: absolute; width: 150px">
      <select class="form-select" v-model="filterType">
        <option selected>Filter sets by</option>
        <option value="name">Name</option>
        <option value="recent">Recent</option>
        <option value="stars">Stars</option>
      </select>
    </div>
    <div v-for="(setFolder, i) in ['Draft', 'Beta', 'Release']" :key="i" class="col-sm px-5">
      <h2 class="text-center mb-4">{{ setFolder }}</h2>
      <div class="list-group list-group-flush">
        <div v-for="(abletonSet, j) in abletonSetsByStage[setFolder.toUpperCase()]" :key="j"
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
              <span @click="selectSet(abletonSet)" class="badge rounded-pill bg-secondary position-relative"
                :class="{'hide-badge': !abletonSet.metadata.scenes.length}"
              >
                <i class="fa-solid fa-bars"></i>
                <span v-if="abletonSet.metadata.comment"
                  class="position-absolute top-0 start-100 translate-middle p-1 bg-danger border border-light rounded-circle">
                </span>
              </span>
            </div>
            <div style="width: 45px">
              <span @click="selectSet(abletonSet)" class="badge rounded-pill mx-1"
                    :class="{'bg-success': !abletonSet.audio?.outdated, 'bg-warning': abletonSet.audio?.outdated}"
              >
                <i class="fa-solid fa-volume-high" v-if="abletonSet.audio"></i>
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
import AbletonSetComment from "@/components/ableton_sets/AbletonSetComment.vue";
import AbletonSetInfo from "@/components/ableton_sets/AbletonSetInfo.vue";
import AbletonSetStars from "@/components/ableton_sets/AbletonSetStars.vue";
import {notify} from "@/utils/utils";
import {AbletonSet, SceneData} from "@/components/ableton_sets/ableton_sets";


export default defineComponent({
  name: 'AbletonSets',
  components: {
    AbletonSetPlayer,
    AbletonSetSceneData,
    AbletonSetComment,
    AbletonSetInfo,
    AbletonSetStars,
  },
  data: () => ({
    abletonSets: [],
    selectedSet: null as AbletonSet | null,
    currentScene: null as SceneData | null,
    playerTime: 0,
    filterType: "recent",
  }),
  computed: {
    abletonSetsByStage() {
      return Object.groupBy(this.abletonSets, (set: AbletonSet) => set.metadata.stage)
    },
    setPlace(): string | null {
      return this.$route.query.place ? this.$route.query.place.toUpperCase(): null
    }
  },
  watch: {
    filterType() {
      this.sortSets()
    },
    async setPlace() {
      await this.fetchSets()
    }
  },
  methods: {
    selectSet(abletonSet: AbletonSet) {
      this.selectedSet = abletonSet
      this.currentScene = this.selectedSet.metadata.scenes ? this.selectedSet.metadata.scenes[0] : null
    },
    async openSet() {
      notify("Opening set")
      await apiService.get(`/set/open?path=${this.selectedSet?.path_info.filename}`)
    },
    onSceneChange(sceneData: SceneData) {
      this.currentScene = sceneData
    },
    onSceneSkip(increment: number) {
      this.currentScene = this.selectedSet?.metadata.scenes[this.currentScene.index + increment]
      if (this.abletonSet.metadata.tempo) {
        this.playerTime = this.currentScene?.start * (60 / this.abletonSet.metadata.tempo)
      }
    },
    sortSets() {
      if (!this.filterType) {
        return
      }
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

      this.abletonSets.sort(getPredicate(getProp(this.filterType), this.filterType))
    },
    async fetchSets() {
      let url = '/set/all'
      if (this.setPlace) {
        url += `?place=${this.setPlace}`
      }
      this.abletonSets = await apiService.get(url)

      // add index to scenes
      for (const abletonSet of this.abletonSets) {
        if (abletonSet.metadata.scenes) {
          for (const i in abletonSet.metadata.scenes) {
            abletonSet.metadata.scenes[i].index = parseInt(i)
          }
        }
      }

      this.sortSets()
    },
    hideSet(abletonSet: AbletonSet) {
      this.abletonSets.splice(this.abletonSets.indexOf(abletonSet), 1)
    }
  },
  async mounted() {
    await this.fetchSets()
  }
})
</script>

<style scoped lang="scss">
.list-group-item .btn {
  border: hidden;
}
.hide-badge {
  background-color: white !important;
}
</style>

