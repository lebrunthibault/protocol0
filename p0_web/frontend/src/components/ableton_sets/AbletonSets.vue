<template>
  <div v-if="selectedSet" class="row mb-4">
    <div class="d-flex flex-row justify-content-between mb-3">
      <div></div>
      <h3 class="mb-4 text-center">
        {{ selectedSet.path_info.name }}
      </h3>
      <div class="btn-group" role="group">
        <span class="my-auto" v-if="selectedSet.metadata">
          {{ selectedSet.metadata.tempo }} BPM
        </span>
        <AbletonSetStars :ableton-set="selectedSet"
          @update="sortSets"
        class="m-3"></AbletonSetStars>
        <AbletonSetInfo :ableton-set="selectedSet" @set-moved="hideSet"></AbletonSetInfo>
        <AbletonSetComment :ableton-set="selectedSet" :scene-data="currentScene"></AbletonSetComment>

        <div class="dropdown">
          <button class="btn btn-lg btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
            <i class="fa-regular fa-folder-open"></i>
          </button>
          <div class="dropdown-menu">
            <div @click="openInExplorer" class="dropdown-item">
              <i class="fa-regular fa-folder-open" style="width: 22px"></i>
              Open in explorer
            </div>
            <div @click="openSet" class="dropdown-item">
              <i class="fa-solid fa-up-right-from-square" style="width: 22px"></i>
              Open ableton set
            </div>
          </div>
        </div>
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
        <option value="commented">Commented</option>
      </select>
    </div>
    <div v-for="(setFolder, i) in ['Idea', 'Track', 'Release']" :key="i" class="col-sm px-5">
      <div class="d-flex justify-content-around">
        <div></div>
        <h2 class="text-center">{{ setFolder }} </h2>
        <small>{{ abletonSetsByStage[setFolder.toUpperCase()] ? abletonSetsByStage[setFolder.toUpperCase()].length: 0 }}</small>
      </div>
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
import {defineComponent} from 'vue'
import api from '@/utils/api'
import localApi from '@/utils/localApi'
import AbletonSetPlayer from "@/components/ableton_sets/AbletonSetPlayer.vue";
import AbletonSetComment from "@/components/ableton_sets/AbletonSetComment.vue";
import AbletonSetInfo from "@/components/ableton_sets/AbletonSetInfo.vue";
import AbletonSetStars from "@/components/ableton_sets/AbletonSetStars.vue";
import {AbletonSet, SceneData} from "@/components/ableton_sets/ableton_sets";


export default defineComponent({
  name: 'AbletonSets',
  components: {
    AbletonSetPlayer,
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
    },
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
    async openInExplorer() {
      await localApi.get(`/set/open_in_explorer?path=${this.selectedSet?.path_info.relative_name}`)
    },
    async openSet() {
      await localApi.get(`/set/open?path=${this.selectedSet?.path_info.relative_name}`)
    },
    onSceneChange(sceneData: SceneData) {
      this.currentScene = sceneData
    },
    sortSets() {
      if (!this.filterType) {
        return
      }

      const getPredicate = (filterType: string): Function => {
          if (filterType === "name") {
            return (a: AbletonSet, b: AbletonSet) => b.path_info.name.localeCompare(a.path_info.name, undefined, {numeric: true})
          } else if (filterType === "recent") {
            return (a: AbletonSet, b: AbletonSet) => a.path_info.saved_at < b.path_info.saved_at ? 1: -1
          } else if (filterType === "stars") {
            return (a: AbletonSet, b: AbletonSet) => {
              return a.metadata?.stars < b.metadata?.stars ? 1: - 1
            }
          } else if (filterType === "commented") {
            return (a: AbletonSet, b: AbletonSet) => {
              if (!b.metadata.comment) {
                return -1;
              } else if (!a.metadata.comment) {
                return 1;
              }

              const aLines = a.metadata.comment ? a.metadata.comment.split("\n").length : 0;
              const bLines = b.metadata.comment ? b.metadata.comment.split("\n").length : 0;

              return bLines - aLines;
            }
          }

          throw new Error(`unknown filter ${filterType}`)
      }

      this.abletonSets.sort(getPredicate(this.filterType))
    },
    async fetchSets() {
      const params = new URLSearchParams()
      if (this.setPlace) {
        params.set("place", this.setPlace)
      }
      if (this.$route.query.backup) {
        params.set("use_backup", "true")
      }

      const url = `/set/all?${params.toString()}`
      const abletonSets: AbletonSet[] = (await api.get(url) as AbletonSet[])
      this.abletonSets = abletonSets.filter((ableton_set: AbletonSet) => ableton_set.audio)

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

