import EventBus from '../../event_bus'
import { inject, injectable } from 'tsyringe'
import DB from '../../service/db'
import ActionGroupAppearedEvent from '../../action/action_group/action_group_appeared_event'
import ActionPressedEvent from '../../action/action_pressed_event'
import { actionTypes, BACK_TO_PREVIOUS_PROFILE } from '../../action/action_type'
import ProfileNameEnum from './ProfileNameEnum'
import SelectedGroupedDevicesUpdatedEvent from '../device/selected_grouped_devices_updated_event'
import ProfileChangedEvent from './profile_changed_event'

@injectable()
class ProfileListeners {
    constructor (@inject(DB) private readonly db: DB) {
    }

    public setup () {
        EventBus.subscribe(ActionGroupAppearedEvent, (event: ActionGroupAppearedEvent) => this.onActionGroupAppearedEvent(event))
        EventBus.subscribe(ActionPressedEvent, (event: ActionPressedEvent) => this.onActionPressedEvent(event))
        EventBus.subscribe(ProfileChangedEvent, (event: ProfileChangedEvent) => this.onProfileChangedEvent(event))
    }

    private onActionGroupAppearedEvent (event: ActionGroupAppearedEvent) {
        if (event.actionType.profile) {
            this.db.profileHistory.push(event.actionType.profile)
        }
    }

    private onActionPressedEvent (event: ActionPressedEvent) {
        const actionType = actionTypes.fromName(event.context.name)

        if (actionType.profileAutoSwitch) {
            this.switchProfile(actionType.profileAutoSwitch)
        } else if (actionType.name === BACK_TO_PREVIOUS_PROFILE) {
            this.switchProfile(this.db.profileHistory.getPrevious() || ProfileNameEnum.HOME)

            this.db.profileHistory.clear()
        }
    }

    private onProfileChangedEvent (event: ProfileChangedEvent) {
        this.switchProfile(event.profile)
    }

    private switchProfile (profile: ProfileNameEnum) {
        // clean previous profiles
        EventBus.emit(new SelectedGroupedDevicesUpdatedEvent([[], [], [], []]))

        $SD.api.switchToProfile('', this.db.deviceId, profile)
    }
}

export default ProfileListeners
