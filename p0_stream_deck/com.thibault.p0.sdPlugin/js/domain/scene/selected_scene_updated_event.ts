import {
    ActionSlotItem,
    SetStateUpdatedEvent
} from '../../script_client/event/set_state_updated_event'
import SceneClipSlotItem from './scene_clip_slot_item'

class SelectedSceneUpdated extends SetStateUpdatedEvent {
    protected getItemClass (): typeof ActionSlotItem {
        return SceneClipSlotItem
    }
}

export default SelectedSceneUpdated
