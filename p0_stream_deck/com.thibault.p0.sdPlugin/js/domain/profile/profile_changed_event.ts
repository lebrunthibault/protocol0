import ProfileNameEnum from './ProfileNameEnum'

class ProfileChangedEvent {
    constructor (public profile: ProfileNameEnum) {
    }
}

export default ProfileChangedEvent
