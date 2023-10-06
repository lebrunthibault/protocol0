<template>
  <button type="button" class="btn btn-light" @click="execute(action.id)">{{ name }}</button>
</template>

<script lang="ts">
import { Action } from './actions'
import { PropType } from 'vue'
import { apiService } from '@/utils/apiService'
import { capitalizeFirstLetter } from '@/utils/utils'

export default {
  name: 'ScriptAction',
  props: {
    action: Object as PropType<Action>,
    actionGroupId: Number
  },
  methods: {
    async execute(action_id: number) {
      await apiService.get(`/actions/${this.actionGroupId}/${action_id}`)
    }
  },
  computed: {
    name(): string {
      return capitalizeFirstLetter(this.action.name)
    }
  }
}
</script>

<style scoped></style>
