import { Action } from './action'
import EventBus from '../event_bus'
import toBoolean, { toBooleanClass } from '../script_client/event/to_boolean'

class ToggleAction {
    private _enabled: boolean = true;
    constructor (
        private readonly action: Action,
        private readonly updateEventClass: toBooleanClass
    ) {
        EventBus.subscribe(updateEventClass, (event: toBoolean) => this.onUpdateEvent(event))
    }

    // noinspection JSUnusedGlobalSymbols
    get enabled () {
        return this._enabled
    }

    set enabled (enabled: boolean) {
        this._enabled = enabled
        this.action.display.enabled = enabled
    }

    private onUpdateEvent (event: toBoolean) {
        this.enabled = event.toBool()
    }
}

export default ToggleAction
