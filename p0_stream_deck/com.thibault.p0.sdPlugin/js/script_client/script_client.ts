import Config from '../config'
import EventBus from '../event_bus'
import DrumCategoriesUpdatedEvent from './event/drum_categories_updated_event'
import FavoriteDeviceNamesUpdatedEvent from '../domain/device/favorite_device_names_updated_event'
import { injectable } from 'tsyringe'
import DrumRackVisibleUpdatedEvent from './event/drum_rack_visible_updated_event'
import VocalCategoriesUpdatedEvent from './event/vocal_categories_updated_event'
import ServerStateSchema, { ServerState } from './server_state'
import { AbletonSet } from './ableton_set'
import TracksUpdatedEvent from '../domain/clip/tracks_updated_event'

interface WebSocketPayload {
    type: string
    data: any
}

@injectable()
class ScriptClient {
    private serverState: ServerState | null = null

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
        p0WebSocket.onmessage = (data) => this.onWebSocketMessage(data)
        p0WebSocket.onclose = _ => this.connect()
    }

    private onWebSocketMessage (message: any) {
        const data: WebSocketPayload = JSON.parse(message.data)

        switch (data.type) {
        case 'SERVER_STATE':
            this.serverState = ServerStateSchema.parse(data.data)
            ScriptClient.emitServerState(this.serverState)
            break
        default:
            console.error(`Got unknown web socket payload type: ${data.type}`)
        }
    }

    private static emitSet (set: AbletonSet) {
        EventBus.emit(new DrumRackVisibleUpdatedEvent(set.current_state.drum_rack_visible))
    }

    private static emitServerState (serverState: ServerState) {
        // deep copy
        serverState = JSON.parse(JSON.stringify(serverState))

        EventBus.emit(new DrumCategoriesUpdatedEvent(serverState.sample_categories.drums))
        EventBus.emit(new VocalCategoriesUpdatedEvent(serverState.sample_categories.vocals))
        EventBus.emit(new FavoriteDeviceNamesUpdatedEvent(serverState.favorite_device_names))

        if (serverState.active_set) {
            EventBus.emit(new TracksUpdatedEvent([
                serverState.active_set.current_state.tracks.drums,
                serverState.active_set.current_state.tracks.harmony,
                serverState.active_set.current_state.tracks.melody,
                serverState.active_set.current_state.tracks.bass
            ]))
        }

        if (serverState.active_set) {
            ScriptClient.emitSet(serverState.active_set)
        } else {
            console.warn('No active set')
        }
    }
}

export default ScriptClient
