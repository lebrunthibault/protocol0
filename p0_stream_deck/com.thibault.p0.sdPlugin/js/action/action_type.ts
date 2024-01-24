/* eslint-disable no-unused-vars */

import ProfileNameEnum from '../domain/profile/ProfileNameEnum'
import ActionSlot from './action_group/action_slot'
import SceneClipActionSlot from '../domain/scene/scene_clip_slot_action_slot'
import LoadDeviceActionSlot from '../domain/device/load_device_action_slot'

class ActionType {
    constructor (
        public name: string,
        public profile: ProfileNameEnum | null,
        public profileAutoSwitch: ProfileNameEnum | null = null,
        public actionSlotClass: typeof ActionSlot = ActionSlot
    ) {
    }
}

const BACK_TO_PREVIOUS_PROFILE = 'back-to-previous-profile'

const actionTypes = {
    BACK_TO_PREVIOUS_PROFILE: new ActionType(BACK_TO_PREVIOUS_PROFILE, null),
    CAPTURE_MIDI: new ActionType('capture-midi', ProfileNameEnum.SELECTED_SCENE, ProfileNameEnum.CLIP_LOOP),
    CAPTURE_MIDI_VALIDATE: new ActionType('capture-midi-validate', ProfileNameEnum.CLIP_LOOP, ProfileNameEnum.SELECTED_SCENE),
    DRUM_RACK_TO_SIMPLER: new ActionType('drum-rack-to-simpler', ProfileNameEnum.DRUMS),
    LOAD_DEVICE: new ActionType('load-device', ProfileNameEnum.DEVICES),
    LOAD_GROUPED_DEVICE: new ActionType(
        'load-grouped-device',
        ProfileNameEnum.DEVICE_GROUP,
        ProfileNameEnum.BACK_TO_PREVIOUS_PROFILE,
        LoadDeviceActionSlot
    ),
    LOAD_INSTRUMENT: new ActionType('load-instrument', ProfileNameEnum.DEVICE_GROUP),
    OPEN_SET: new ActionType('open-set', ProfileNameEnum.HOME, ProfileNameEnum.DEVICES),
    CLIP_SLOT_CONTROL: new ActionType(
        'clip-slot-control',
        ProfileNameEnum.SELECTED_SCENE,
        null,
        SceneClipActionSlot
    ),

    fromName (name: string): ActionType {
        for (const key in this) {
            // @ts-ignore
            const type: any = this[key]

            if (type instanceof ActionType && type.name === name) {
                return type
            }
        }

        throw new Error(`Couldn't find action type from ${name}`)
    }
}

export { actionTypes, ActionType, BACK_TO_PREVIOUS_PROFILE }
