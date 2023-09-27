<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4 px-3">
    <a class="navbar-brand" href="/">
      <img src="@/assets/protocol0_icon.png" width="30" height="30" alt="" />
    </a>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
        <li v-for="actionGroup in actionGroups" :key="actionGroup.id">
          <a
            :class="{ active: actionGroup === selectedActionGroup }"
            class="nav-item nav-link m-3"
            href="#"
            @click="selectedActionGroup = actionGroup"
            >{{ actionGroup.name }}</a
          >
        </li>
      </ul>
    </div>
  </nav>
  <ActionGroup :action-group="selectedActionGroup"></ActionGroup>
</template>

<script lang="ts">
import ActionGroupComponent from '@/components/actions/ActionGroup.vue'
import { ActionGroup } from '@/components/actions/actions'
import { PropType, defineComponent } from 'vue'
import { apiService } from '@/utils/apiService'

export default defineComponent({
  name: 'ScriptActions',
  components: { ActionGroup: ActionGroupComponent },
  data: () => ({
    actionGroups: [] as ActionGroup[],
    selectedActionGroup: Object as PropType<ActionGroup>
  }),
  async mounted() {
    this.actionGroups = await apiService.fetch('/actions')
    this.actionGroups.sort((a: ActionGroup) => {
      return a.name === 'Main' ? -1 : 1
    })
    this.selectedActionGroup = this.actionGroups[0]
  }
})
</script>

<style scoped>
.nav-item.active {
  font-weight: bold;
}
</style>
