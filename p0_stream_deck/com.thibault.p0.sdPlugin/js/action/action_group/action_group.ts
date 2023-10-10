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
        private readonly iconDisabled: string = Icons.disabled
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

        this.actionRepository.save(new (this.actionType.actionSlotClass)(
            event,
            this.actionType.name,
            this.icon,
            this.iconDisabled,
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

        // reset slots
        this.slots.forEach(a => a.disable())

        const activeSlots = this.getSlotsToEnable(this.lastUpdatedEvent.items)

        if (activeSlots[0] instanceof Array) {
            for (const [i, activeSlotRow] of activeSlots?.entries()) {
                (activeSlotRow as ActionSlot[]).forEach((slot: ActionSlot, j: number) => {
                    slot.setParameter((event.items as [][])[i][j])
                })
            }
        } else {
            (activeSlots as ActionSlot[]).forEach((slot: ActionSlot, i: number) => {
                slot.setParameter((event.items as [])[i])
            })
        }

        // grid or list shape
        const flatItems = event.items.flat()
        const flatActiveSlots = activeSlots.flat()
        if (flatActiveSlots.length < flatItems.length) {
            console.warn(`Got ${flatItems.length} parameters to display but only ${flatActiveSlots.length} action slots`)
        }
    }

    private getSlotsToEnable (parameters: ActionSlotItems): ActionSlot[] | ActionSlot[][] {
        if (parameters.length === 0) {
            return []
        }

        // grid or list shape
        if (parameters[0] instanceof Array) {
            const activeSlots: ActionSlot[][] = []
            console.log(parameters, this.slots)
            for (const [rowIndex, slotItems] of parameters.entries()) {
                const rowSlots = this.slots.filter((slot: ActionSlot) => slot.row === rowIndex)
                activeSlots.push(rowSlots.slice(0, (slotItems as ActionSlotItem[]).length))
            }
            return activeSlots
        } else {
            return this.slots.slice(0, parameters.length)
        }
    }
}

export default ActionGroup
