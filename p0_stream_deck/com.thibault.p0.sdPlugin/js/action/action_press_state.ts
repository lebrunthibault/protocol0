import Config from '../config'
import EventBus from '../event_bus'
import ActionPressedEvent from './action_pressed_event'
import ActionContext from './action_context'

class ActionPressState {
    private pressedAt: number | null = null;

    constructor (
        private actionContext: ActionContext,
        private pressFunc: Function,
        private longPressFunc: Function | null = null,
        private context: string| null = null
    ) {
        $SD.on(`com.thibault.p0.${actionContext.name}.keyDown`, (event: SDEvent) => this.onKeyDown(event))
        $SD.on(`com.thibault.p0.${actionContext.name}.keyUp`, (event: SDEvent) => this.onKeyUp(event))
    }

    private onKeyDown (sdEvent: SDEvent) {
        if (this.context && this.context !== sdEvent.context) {
            return
        }
        this.pressedAt = performance.now()
    }

    private onKeyUp (sdEvent: SDEvent) {
        if (this.context && this.context !== sdEvent.context) {
            return
        }

        if (!this.pressedAt) {
            console.error('Got Key up without key down')
            return
        }

        const longPress = (performance.now() - this.pressedAt) > Config.LONG_PRESS_THRESHOLD
        this.pressedAt = null
        EventBus.emit(new ActionPressedEvent(this.actionContext))

        if (longPress) {
            (this.longPressFunc || this.pressFunc)()
        } else {
            this.pressFunc()
        }
    }
}

export default ActionPressState
