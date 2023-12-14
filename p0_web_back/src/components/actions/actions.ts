interface Action {
  id: number
  name: string
}

interface ActionGroup {
  id: number
  name: string
  actions: Action[]
}

export { Action, ActionGroup }
