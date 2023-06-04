import { ActionSlotItem, SetStateUpdatedEvent } from '../../script_client/event/set_state_updated_event'
import { DeviceGroup } from '../../script_client/server_state'

class FavoriteDeviceNameItem extends ActionSlotItem {
    constructor (
        protected readonly _item: string | DeviceGroup
    ) {
        super(_item)
    }

    get label (): string {
        if (typeof this._item === 'string') {
            return this._item
        } else {
            return this._item.name + '*'
        }
    }
}

class FavoriteDeviceNamesUpdatedEvent extends SetStateUpdatedEvent {
    protected getItemClass (): typeof ActionSlotItem {
        return FavoriteDeviceNameItem
    }
}

export default FavoriteDeviceNamesUpdatedEvent
