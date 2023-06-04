// make sharing / setting the action context easier
class ActionContext {
    constructor (public readonly name: string, public context: string = '') {

    }
}

export default ActionContext
