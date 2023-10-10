import ActionSlot from '../../action/action_group/action_slot'
import SceneClipSlotItem from './scene_clip_slot_item'
import Icons from '../../service/icons'
import { toStreamDeckTitle } from '../../service/string_utils'

class SceneClipActionSlot extends ActionSlot {
    protected parameter: SceneClipSlotItem | null = null;

    protected enable () {
        super.enable()

        if (!this.parameter) {
            return
        }

        const clipState = this.parameter.item

        if (clipState.has_clip) {
            const groupName = clipState.group_name
            if (groupName === 'drums') {
                if (clipState.is_playing) {
                    this.display.setImage(Icons.drumsColor)
                } else {
                    this.display.setImage(Icons.drumsDimColor)
                }
            } else if (groupName === 'harmony') {
                if (clipState.is_playing) {
                    this.display.setImage(Icons.harmonyColor)
                } else {
                    this.display.setImage(Icons.harmonyDimColor)
                }
            } else if (groupName === 'melody') {
                if (clipState.is_playing) {
                    this.display.setImage(Icons.melodyColor)
                } else {
                    this.display.setImage(Icons.melodyDimColor)
                }
            } else if (groupName === 'bass') {
                if (clipState.is_playing) {
                    this.display.setImage(Icons.bassColor)
                } else {
                    this.display.setImage(Icons.bassDimColor)
                }
            }

            if (clipState.is_armed) {
                this.display.setTitle(`${toStreamDeckTitle(this.parameter.label)} *`)
            }
        } else if (clipState.is_armed) {
            this.display.setImage(Icons.trackArmedColor)
        }
    }
}

export default SceneClipActionSlot
