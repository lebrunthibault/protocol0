import { ActionType } from '../action_type'

class ActionGroupAppearedEvent {
    constructor (public actionType: ActionType) {
    }
}

export default ActionGroupAppearedEvent
