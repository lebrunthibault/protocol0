import { ActionSlotItem } from '../../script_client/event/set_state_updated_event'
import { SceneTrackState } from '../../script_client/ableton_set'

class SceneClipSlotItem extends ActionSlotItem {
    constructor (
        protected readonly _item: SceneTrackState
    ) {
        super(_item)
    }

    get item (): SceneTrackState {
        return this._item
    }

    get value (): string {
        return this._item.track_name
    }

    get label (): string {
        return this._item.track_name
    }
}

export default SceneClipSlotItem
