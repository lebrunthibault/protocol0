// noinspection JSUnusedGlobalSymbols,JSUnusedLocalSymbols
// @ts-ignore
global.$SD = {
    on: () => null,
    api: {
        setTitle(context: string, title: string) {
            console.info(`SD ${context} set title '${title}'`)
        },

        setImage(context: string, image: string) {
            console.info(`SD ${context} set image`)
        },

        showAlert(context: string) {
            console.info(`SD ${context}`)
        },
    }
}

class SDEvent {
    public readonly context: string
    payload: Object
    constructor(context: string, row: number = 0, column: number = 0) {
        this.context = context
        this.payload = {
            coordinates: {
                row: row,
                column: column
            }
        }
    }
}

export {SDEvent}