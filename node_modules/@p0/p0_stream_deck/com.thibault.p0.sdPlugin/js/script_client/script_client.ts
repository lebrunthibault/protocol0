import Config from '../config'
import EventBus from '../event_bus'
import FavoriteDeviceNamesUpdatedEvent from '../domain/device/favorite_device_names_updated_event'
import { injectable } from 'tsyringe'

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
            EventBus.emit(new FavoriteDeviceNamesUpdatedEvent(data.data))
            break
        default:
            console.error(`Got unknown web socket payload type: ${data.type}`)
        }
    }
}

export default ScriptClient
