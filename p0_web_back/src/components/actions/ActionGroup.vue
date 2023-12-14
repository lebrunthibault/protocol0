<template>
  <div class="grid">
    <div v-for="(action, i) in rows" :key="i" class="cell">
      <Action v-if="action" :action="action" :action-group-id="actionGroup.id"></Action>
      <span v-else style="min-height: 20px"></span>
    </div>
  </div>
</template>

<script lang="ts">
import ActionComponent from '@/components/actions/ScriptAction.vue'
import { Action, ActionGroup } from './actions'
import { PropType, defineComponent } from 'vue'

export default defineComponent({
  name: 'ActionGroup',
  components: { Action: ActionComponent },
  props: {
    actionGroup: {
      type: Object as PropType<ActionGroup>,
      required: true
    }
  },
  computed: {
    rows(): Array<Action | null> {
      const slots = Array(16)

      for (const action of this.actionGroup.actions || []) {
        slots[action.id - 1] = action
      }

      return slots
    }
  }
})
</script>

<style scoped lang="scss">
.grid {
  display: grid;

  max-width: 800px;

  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, 1fr);
  grid-gap: 1px;
  margin: 0 auto;
}

.cell {
  background-color: white;
  padding: 10px;
}

.cell:not(:nth-last-child(-n + 4)) {
  border-bottom: 1px dashed #b5c1c3;
}

.cell:not(:nth-child(4n)) {
  border-right: 1px dashed #b5c1c3;
}
</style>
