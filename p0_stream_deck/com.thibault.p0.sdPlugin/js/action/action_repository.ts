import DB from '../service/db'
import { ActionClass } from './action_class'

import { inject, injectable } from 'tsyringe'
import ActionSlot from './action_group/action_slot'
import ActionInterface from './action_interface'

@injectable()
class ActionRepository {
    /* eslint-disable no-useless-constructor */
    constructor (@inject(DB) private readonly db: DB) {}

    save (action: ActionInterface) {
        this.db.actions.push(action)
    }

    getActionsByClass<A extends ActionInterface> (cls: ActionClass<ActionInterface>): A[] {
        return <A[]> this.db.actions.filter((a: ActionInterface) => a instanceof cls)
    }

    getActionSlotByName (name: string): ActionSlot[] {
        return this
            .getActionsByClass<ActionSlot>(ActionSlot).filter((a: ActionSlot) => a.name === name)
            .sort((a: ActionSlot, b: ActionSlot) => a.index - b.index)
    }

    getActionByContext (context: string): ActionInterface|undefined {
        return this.db.actions.find((a: ActionInterface) => a.context === context)
    }
}

export default ActionRepository
