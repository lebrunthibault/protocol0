/* eslint-disable no-new */

import ActionRepository from './action_repository'
import { Action } from './action'
import API from '../service/api'
import ActionGroup from './action_group/action_group'
import DrumCategoriesUpdatedEvent from '../script_client/event/drum_categories_updated_event'
import FavoriteDeviceNamesUpdatedEvent from '../domain/device/favorite_device_names_updated_event'
import Icons from '../service/icons'
import { inject, injectable } from 'tsyringe'
import ToggleAction from './toggle_action'
import DrumRackVisibleUpdatedEvent from '../script_client/event/drum_rack_visible_updated_event'
import VocalCategoriesUpdatedEvent from '../script_client/event/vocal_categories_updated_event'
import AbletonSetShortcutsUpdatedEvent from '../script_client/event/ableton_favorite_sets_updated_event'
import { actionTypes } from './action_type'
import { loadDevice, selectOrLoadDevice } from '../domain/device/load_device'
import SelectedGroupedDevicesUpdatedEvent from '../domain/device/selected_grouped_devices_updated_event'

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
            () => {
            },
            null
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
            Icons.device,
            FavoriteDeviceNamesUpdatedEvent,
            selectOrLoadDevice,
            loadDevice
        )
        new ActionGroup(
            this.actionRepository,
            actionTypes.LOAD_GROUPED_DEVICE,
            Icons.device,
            SelectedGroupedDevicesUpdatedEvent,
            selectOrLoadDevice,
            loadDevice
        )
        new ActionGroup(
            this.actionRepository,
            actionTypes.LOAD_DRUM_TRACK,
            Icons.newTrack,
            DrumCategoriesUpdatedEvent,
            API.loadDrumSamples
        )
        new ActionGroup(
            this.actionRepository,
            actionTypes.LOAD_VOCAL_TRACK,
            Icons.newTrack,
            VocalCategoriesUpdatedEvent,
            API.loadVocalSamples
        )
        new ActionGroup(
            this.actionRepository,
            actionTypes.OPEN_SET,
            Icons.set,
            AbletonSetShortcutsUpdatedEvent,
            API.openSet,
            null,
            Icons.muted
        )
    }
}

export default ActionFactory
