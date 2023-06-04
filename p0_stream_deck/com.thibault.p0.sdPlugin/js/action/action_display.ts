import Icons from '../service/icons'
import ActionContext from './action_context'

class ActionDisplay {
    /* eslint-disable no-useless-constructor */
    constructor (
        private readonly actionContext: ActionContext,
        private readonly icon: string,
        private readonly iconDisabled: string = Icons.disabled,
        private readonly title: string = '',
        private readonly titleDisabled: string = ''
    ) {
    }

    toString (): string {
        return this.constructor.name
    }

    static disabled () {
        return new ActionDisplay(new ActionContext(''), '', '', '')
    }

    // noinspection JSUnusedGlobalSymbols
    get enabled (): boolean {
        return true // unused
    }

    set enabled (enabled: boolean) {
        if (enabled) {
            if (this.title) {
                this.setTitle(this.title)
            }
            this.setImage(this.icon)
        } else {
            this.setTitle(this.titleDisabled)
            this.setImage(this.iconDisabled)
        }
    }

    setTitle (title: string) {
        $SD.api.setTitle(this.actionContext.context, title)
    }

    setImage (image: string) {
        $SD.api.setImage(this.actionContext.context, image)
    }
}

export default ActionDisplay
