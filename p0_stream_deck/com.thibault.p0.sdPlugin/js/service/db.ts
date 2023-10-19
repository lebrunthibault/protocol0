// in memory database

import { singleton } from 'tsyringe'
import ActionInterface from '../action/action_interface'
import ProfileNameEnum from '../domain/profile/ProfileNameEnum'

class ProfileHistory {
    private history : ProfileNameEnum[] = []

    push (profile: ProfileNameEnum) {
        this.history.unshift(profile)
    }

    getPrevious (): ProfileNameEnum | null {
        return this.history[0] || null
    }

    clear () {
        this.history = []
    }
}

@singleton()
class DB {
    public readonly actions: ActionInterface[] = [];
    public deviceId: string = ''
    public profileHistory: ProfileHistory = new ProfileHistory()
}

export default DB
