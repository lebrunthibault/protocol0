import Config from '../config'
import EventBus from '../event_bus'
import FavoriteDeviceNamesUpdatedEvent from '../domain/device/favorite_device_names_updated_event'
import { injectable } from 'tsyringe'
import DrumRackVisibleUpdatedEvent from './event/drum_rack_visible_updated_event'
import AbletonSetCurrentStateSchema, { AbletonSetCurrentState } from './ableton_set'
import SelectedSceneUpdated from '../domain/scene/selected_scene_updated_event'

interface WebSocketPayload {
    type: string
    data: any
}

@injectable()
class ScriptClient {
    async connect () {
        try {
            await this._connect()
            console.info('connected to websocket server')
        } catch (e) {
            console.warn(e)
            const delay = 5000
            console.warn(`scheduling reconnection in ${delay} ms`)
            setTimeout(async () => await this.connect(), delay)
        }
    }

    async _connect () {
        const p0WebSocket = new WebSocket(Config.P0_WS_URL)
        // explicit arrow func to keep this binding
        p0WebSocket.onmessage = (data) => ScriptClient.onWebSocketMessage(data)
        p0WebSocket.onclose = _ => this.connect()
    }

    private static onWebSocketMessage (message: any) {
        const data: WebSocketPayload = JSON.parse(message.data)

        switch (data.type) {
        case 'FAVORITE_DEVICES':
            console.log('FAVORITE_DEVICES', data.data)
            EventBus.emit(new FavoriteDeviceNamesUpdatedEvent(data.data))
            break
        case 'ACTIVE_SET':
            console.log('ACTIVE_SET', data.data)
            ScriptClient.emitActiveSet(AbletonSetCurrentStateSchema.parse(JSON.parse(data.data)))
            break
        default:
            console.error(`Got unknown web socket payload type: ${data.type}`)
        }
    }

    private static emitActiveSet (setCurrentState: AbletonSetCurrentState) {
        // deep copy
        setCurrentState = JSON.parse(JSON.stringify(setCurrentState))

        if (setCurrentState) {
            EventBus.emit(new SelectedSceneUpdated([
                setCurrentState.selected_scene.drums,
                setCurrentState.selected_scene.harmony,
                setCurrentState.selected_scene.melody,
                setCurrentState.selected_scene.bass
            ]))
            EventBus.emit(new DrumRackVisibleUpdatedEvent(setCurrentState.drum_rack_visible))
        } else {
            console.warn('No active set')
        }
    }
}

export default ScriptClient
