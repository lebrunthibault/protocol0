import { DeviceGroup } from '../../script_client/server_state'
import API from '../../service/api'
import EventBus from '../../event_bus'
import SelectedGroupedDevicesUpdatedEvent from './selected_grouped_devices_updated_event'

function selectOrLoadDevice (device: string | DeviceGroup) {
    if (typeof device === 'string') {
        API.loadDevice(device)
    } else {
        API.loadDevice(device.devices[0])
    }
}

function loadDevice (device: string | DeviceGroup) {
    if (typeof device === 'string') {
        API.loadDevice(device)
    } else {
        EventBus.emit(new SelectedGroupedDevicesUpdatedEvent(device.devices))
    }
}

export { selectOrLoadDevice, loadDevice }
