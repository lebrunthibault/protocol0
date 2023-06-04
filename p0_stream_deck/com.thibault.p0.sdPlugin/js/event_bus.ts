class RegistryEntry {
    public eventClass: Class
    public subscribers: Set<Function> = new Set<Function>()

    public toString () {
        return `eventClass: ${this.eventClass}, subscribers: ${this.subscribers}`
    }

    constructor (eventClass: Class) {
        this.eventClass = eventClass
    }
}

class Registry {
    private readonly entries: RegistryEntry[] = []

    public toString () {
        return this.entries
    }

    public register (eventClass: Class, func: Function) {
        let registryEntry = this.entries.find((entry: RegistryEntry) => entry.eventClass === eventClass)
        if (!registryEntry) {
            registryEntry = new RegistryEntry(eventClass)
            this.entries.push(registryEntry)
        }

        registryEntry.subscribers.add(func)
    }

    public getSubscribers (eventClass: Class): Function[] {
        const registryEntry = this.entries.find((entry: RegistryEntry) => eventClass === entry.eventClass)
        if (!registryEntry) {
            console.warn(`event emitted without subscriber: ${eventClass}`)
            console.warn(this)
            return []
        }

        return Array.from(registryEntry.subscribers)
    }
}

const registry = new Registry()

class EventBus {
    static subscribe (eventClass: Class, func: Function) {
        registry.register(eventClass, func)
    }

    static emit (event: Object) {
        console.debug('emitting event ' + event.constructor.name)

        const subscribers = registry.getSubscribers(event.constructor)

        for (const subscriber of subscribers) {
            subscriber(event)
        }
    }
}

export default EventBus
