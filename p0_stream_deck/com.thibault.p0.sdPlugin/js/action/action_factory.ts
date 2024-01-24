/* eslint-disable no-new */

import ActionRepository from './action_repository'
import { Action } from './action'
import API from '../service/api'
import ActionGroup from './action_group/action_group'
import FavoriteDeviceNamesUpdatedEvent from '../domain/device/favorite_device_names_updated_event'
import Icons from '../service/icons'
import { inject, injectable } from 'tsyringe'
import ToggleAction from './toggle_action'
import DrumRackVisibleUpdatedEvent from '../script_client/event/drum_rack_visible_updated_event'
import { actionTypes } from './action_type'
import { loadDevice, loadInstruments, selectOrLoadDevice } from '../domain/device/load_device'
import SelectedGroupedDevicesUpdatedEvent from '../domain/device/selected_grouped_devices_updated_event'
import SelectedSceneUpdated from '../domain/scene/selected_scene_updated_event'

@injectable()
class ActionFactory {
    /* eslint-disable no-useless-constructor */
    constructor (
        @inject(ActionRepository) private actionRepository: ActionRepository
    ) {
    }

    createActions () {
        new Action(
            actionTypes.BACK_TO_PREVIOUS_PROFILE,
            () => {},
            null
        )
        new Action(
            actionTypes.CAPTURE_MIDI,
            API.captureMidi,
            null
        )
        new Action(
            actionTypes.CAPTURE_MIDI_VALIDATE,
            API.captureMidiValidate,
            null
        )
        new ActionGroup(
            this.actionRepository,
            actionTypes.CLIP_SLOT_CONTROL,
            Icons.empty,
            SelectedSceneUpdated,
            API.selectClip,
            API.toggleClip
        )
        new ToggleAction(new Action(
            actionTypes.DRUM_RACK_TO_SIMPLER,
            API.drumRackToSimpler,
            null,
            Icons.drumRackToSimpler
        ),
        DrumRackVisibleUpdatedEvent
        )
        new ActionGroup(
            this.actionRepository,
            actionTypes.LOAD_DEVICE,
            Icons.empty,
            FavoriteDeviceNamesUpdatedEvent,
            selectOrLoadDevice,
            loadDevice
        )
        new ActionGroup(
            this.actionRepository,
            actionTypes.LOAD_GROUPED_DEVICE,
            Icons.empty,
            SelectedGroupedDevicesUpdatedEvent,
            loadDevice,
            selectOrLoadDevice
        )
        new Action(
            actionTypes.LOAD_INSTRUMENT,
            loadInstruments,
            null
        )
    }
}

export default ActionFactory
