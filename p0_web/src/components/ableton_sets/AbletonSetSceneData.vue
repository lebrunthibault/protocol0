<template>
  <button @click="showSceneData" type="button" class="btn btn-lg btn-light">
    <i class="fa-solid fa-bars" data-toggle="tooltip" data-placement="top" title="Show scene details"></i>
  </button>
  <div class="modal" id="setSceneModal" tabindex="-1" role="dialog" v-if="sceneData">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ sceneData.name }}</h5>
          <div>
            <i v-if="hasPrev" @click="$emit('sceneSkip', -1)" class="fa-solid fa-arrow-left"></i>
            <small class="mx-3">{{ toTime(sceneData.start_time) }} : {{ toTime(sceneData.end_time )}}</small>
            <i v-if="hasNext" @click="$emit('sceneSkip', 1)" class="fa-solid fa-arrow-right"></i>
          </div>
        </div>
        <div class="modal-body">
          <div class="text-center">
            Tracks
          </div>
          <ol class="list-group list-group-flush">
            <li v-for="(trackNames, group) in trackNames" :key="group"
                class="list-group-item d-flex justify-content-between align-items-start mb-3"
            >
              <div class="">
                <div class="fw-bold">{{ group }}</div>
                <ul  class="list-group list-group-flush">
                  <li v-for="trackName in trackNames" :key="trackName" class="list-group-item">{{ trackName }}</li>
                </ul>
              </div>
            </li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">

import {defineComponent, PropType} from "vue";

export default defineComponent({
  name: 'AbletonSetSceneData',
  props: {
    abletonSet: Object as PropType<AbletonSet>,
    sceneData: Object as PropType<SceneData>,
  },
  emits: ['sceneSkip'],
  computed: {
    hasPrev(): boolean {
      return this.sceneData.index != 0
    },
    hasNext(): boolean {
      return this.sceneData.index < this.abletonSet.metadata.scenes.length - 1
    },
    trackNames(): Object {
      const namesByGroup: any = {};

      for (const track_name of this.sceneData?.track_names) {
        const parts = track_name.split(" - ");
        const group = parts[0]
        const name: string | null = parts.length > 1 ? parts.slice(1).join(" - ") : null

        if (!namesByGroup[group]) {
          namesByGroup[group] = [];
        }

        if (name) {
          namesByGroup[group].push(name);
        }
      }

      return namesByGroup
    }
  },
  methods: {
    showSceneData() {
      $('#setSceneModal').modal('show')
    },
    sceneSkip() {
      this.$emit('sceneSkip', 1)
    },
    toTime(seconds: number) {
      return new Date(seconds * 1000).toISOString().substring(14, 19)
    },
  }
})
</script>