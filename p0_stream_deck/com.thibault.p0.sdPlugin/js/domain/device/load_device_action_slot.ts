import ActionSlot from '../../action/action_group/action_slot'
import Icons from '../../service/icons'

class LoadDeviceActionSlot extends ActionSlot {
    protected enable () {
        super.enable()
        const name = this.parameter?.value
        if (!name) {
            return
        }

        if (['SYLENTH1_BASS', 'SERUM_BASS'].includes(name)) {
            this.display.setImage(Icons.bassDimColor)
        } else if (['SYLENTH1_KEYS', 'SERUM_KEYS', 'SYLENTH1_PLUCK', 'SERUM_PLUCK'].includes(name)) {
            this.display.setImage(Icons.harmonyDimColor)
        } else if (['SYLENTH1_LEAD', 'SERUM_LEAD'].includes(name)) {
            this.display.setImage(Icons.melodyDimColor)
        }
    }
}

export default LoadDeviceActionSlot
