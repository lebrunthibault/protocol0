// in memory database

import { singleton } from 'tsyringe'
import ActionInterface from '../action/action_interface'
import ProfileNameEnum from '../domain/profile/ProfileNameEnum'

class ProfileHistory {
    private history : ProfileNameEnum[] = []

    push (profile: ProfileNameEnum) {
        if (this.history[0] !== profile) {
            this.history.unshift(profile)
            this.history.length = 2
        }
    }

    getPrevious (): ProfileNameEnum | null {
        return this.history[1] || null
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
