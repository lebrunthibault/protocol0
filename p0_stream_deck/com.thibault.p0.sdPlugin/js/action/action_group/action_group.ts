import ActionRepository from '../action_repository'
import EventBus from '../../event_bus'
import ActionGroupAppearedEvent from './action_group_appeared_event'

import * as _ from 'lodash-es'
import { ActionSlotItem, ActionSlotItems, SetStateUpdatedEvent } from '../../script_client/event/set_state_updated_event'
import ActionSlot from './action_slot'
import Icons from '../../service/icons'
import { ActionType } from '../action_type'

/**
 * CLass representing handling the creation and update of list of correlated dynamic actions
 * The class instance is bound to a specific property and will update its action list
 * on each event update.
 *
 * Thus allowing dynamic action generation on the stream deck, something not possible with the stock script.
 */
class ActionGroup {
    private readonly emitGroupAppearedEventDebounced: Function;
    private lastUpdatedEvent: SetStateUpdatedEvent | null = null;

    constructor (
        private readonly actionRepository: ActionRepository,
        private readonly actionType: ActionType,
        private readonly icon: string,
        private readonly updateEvent: typeof SetStateUpdatedEvent,
        private readonly actionFunc: ActionSlotFunction,
        private readonly longPressFunc: ActionSlotFunction | null = null,
        private readonly icon_disabled: string = Icons.disabled
    ) {
        this.emitGroupAppearedEventDebounced = _.debounce(() => this.emitGroupAppearedEvent(), 10, { leading: false })

        $SD.on(`com.thibault.p0.${actionType.name}.willAppear`, (event: SDEvent) => this.onWillAppear(event))

        EventBus.subscribe(updateEvent, (event: SetStateUpdatedEvent) => this.onUpdateEvent(event))
    }

    private get slots (): ActionSlot[] {
        return this.actionRepository.getActionSlotByName(this.actionType.name)
    }

    private emitGroupAppearedEvent () {
        EventBus.emit(new ActionGroupAppearedEvent(this.actionType))

        // use the cached version to hydrate the group
        if (this.lastUpdatedEvent) {
            this.onUpdateEvent(this.lastUpdatedEvent)
        }
    }

    /**
     * Each time the action appears, create a dynamic action object
     * Then emit a group appeared event (debounced) so that the song state
     * is emitted, which will configure each dynamic action with a specific parameter
     */
    private onWillAppear (event: SDEvent) {
        // there are duplicate calls to this ..
        this.emitGroupAppearedEventDebounced()
        if (this.actionRepository.getActionByContext(event.context)) {
            return
        }

        this.actionRepository.save(new ActionSlot(
            event,
            this.actionType.name,
            this.icon,
            this.icon_disabled,
            this.actionFunc,
            this.longPressFunc
        ))
    }

    /**
     * The updateEvent is the specific update event configured
     * Each time we receive it, we update all actions
     * Action will be enabled or disabled depending on the size of the "event.items" array
     */
    private onUpdateEvent (event: SetStateUpdatedEvent) {
        if (
            this.lastUpdatedEvent &&
            _.isEqual(this.lastUpdatedEvent.items, event.items) &&
            this.slots.length === event.items.length && this.slots.every(slot => slot.shown)
        ) {
            return
        }

        this.lastUpdatedEvent = event

        if (this.slots.length === 0) {
            return
        }

        const activeSlots = [...this.getSlotsToEnable(this.lastUpdatedEvent.items)]
        // NB : we receive parameters in row form or grid form. flattening to row form for further processing.
        const parameters = this.lastUpdatedEvent.items.flat()

        // disable unused action slots
        this.slots.filter((slot: ActionSlot) => !activeSlots.includes(slot)).forEach(a => a.disable())

        if (activeSlots.length < parameters.length) {
            console.warn(`Got ${parameters.length} parameters to display but only ${activeSlots.length} action slots`)
        }

        activeSlots.forEach((slot: ActionSlot, i: number) => {
            slot.setParameter(parameters[i])
        })
    }

    private * getSlotsToEnable (parameters: ActionSlotItems): Generator<ActionSlot, ActionSlot[] | undefined, undefined> {
        if (parameters.length === 0) {
            return []
        }

        // grid or list shape
        if (parameters[0] instanceof Array) {
            for (const [i, rowParameters] of parameters.entries()) {
                yield * this.slots.filter((slot: ActionSlot) => slot.row === i).slice(0, (rowParameters as unknown as ActionSlotItem[]).length)
            }
        } else {
            yield * this.slots.slice(0, parameters.length)
        }
    }
}

export default ActionGroup
