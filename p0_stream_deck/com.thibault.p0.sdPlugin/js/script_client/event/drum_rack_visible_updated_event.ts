class DrumRackVisibleUpdatedEvent {
    public readonly visible: boolean
    constructor (visible: boolean) {
        this.visible = visible
    }

    toBool (): boolean {
        return this.visible
    }
}

export default DrumRackVisibleUpdatedEvent
