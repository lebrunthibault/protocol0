import ActionDisplay from './action_display'
import Icons from '../service/icons'
import ActionPressState from './action_press_state'
import ActionContext from './action_context'
import { ActionType } from './action_type'

class Action {
    private readonly _context: ActionContext;
    private readonly _display: ActionDisplay;
    private pressState: ActionPressState;

    constructor (
        public readonly actionType: ActionType,
        private readonly pressFunc: Function,
        private readonly longPressFunc: Function|null = null,
        private readonly icon: string = '',
        private readonly iconDisabled: string = Icons.disabled,
        private readonly title: string = '',
        private readonly titleDisabled: string = ''
    ) {
        this._context = new ActionContext(actionType.name)
        this.pressState = new ActionPressState(this._context, pressFunc, longPressFunc)
        this._display = new ActionDisplay(
            this._context,
            this.icon,
            this.iconDisabled,
            this.title,
            this.titleDisabled
        )

        this._display = ActionDisplay.disabled()
        $SD.on(`com.thibault.p0.${actionType.name}.willAppear`, (event: SDEvent) => this.onWillAppear(event))
    }

    toString () {
        return `Action(name="${this.actionType.name}", context="${this.context}")`
    }

    // needed for ActionInterface
    get display (): ActionDisplay {
        return this._display
    }

    get context (): string {
        return this._context.context
    }

    private onWillAppear (event: SDEvent) {
        this._context.context = event.context
    }
}

export { Action }
