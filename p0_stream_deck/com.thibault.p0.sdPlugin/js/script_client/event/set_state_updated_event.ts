class ActionSlotItem {
    constructor (
        protected readonly _item: any
    ) {
    }

    get value (): string {
        return this._item
    }

    // noinspection JSUnusedGlobalSymbols
    get label (): string {
        return this._item
    }

    get active (): boolean {
        return true
    }
}

type ActionSlotItems = ActionSlotItem[] | ActionSlotItem[][]

abstract class SetStateUpdatedEvent {
    public readonly items: ActionSlotItems = []

    constructor (items: any[] | any[][]) {
        if (items.length === 0) {
            return
        }

        // checking for grid shape or simple list shape
        if (items[0] instanceof Array) {
            this.items = items.map(row => row.map((i: any) => new (this.getItemClass())(i)))
        } else {
            this.items = items.map(i => new (this.getItemClass())(i))
        }
    }

    toString (): string {
        return this.constructor.name
    }

    protected getItemClass (): typeof ActionSlotItem {
        return ActionSlotItem
    }
}

export type { ActionSlotItems }
export { SetStateUpdatedEvent, ActionSlotItem }
