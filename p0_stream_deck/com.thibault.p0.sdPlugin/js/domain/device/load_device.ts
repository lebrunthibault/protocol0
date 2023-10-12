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
        API.loadDeviceInNewTrack(device)
    } else {
        if (['Sylenth1', 'Serum'].includes(device.name)) {
            // removing the base option for instruments
            // and displaying options on the base row
            EventBus.emit(new SelectedGroupedDevicesUpdatedEvent([[], [], [], device.devices.slice(1)]))
        } else {
            EventBus.emit(new SelectedGroupedDevicesUpdatedEvent([[], [], [], device.devices]))
        }
    }
}

export { selectOrLoadDevice, loadDevice }
