import Config from '../config'

const API = {
    captureMidi () {
        fetch(`${Config.P0_API_URL}/record/capture_midi`).then(() => null)
    },
    captureMidiValidate () {
        fetch(`${Config.P0_API_URL}/record/capture_midi/validate`).then(() => null)
    },
    drumRackToSimpler () {
        fetch(`${Config.P0_API_URL}/drum_rack_to_simpler`).then(() => null)
    },
    loadDevice (name: string) {
        fetch(`${Config.P0_API_URL}/device/load?name=${name}`).then(() => null)
    },
    loadDeviceInNewTrack (name: string) {
        fetch(`${Config.P0_API_URL}/device/load?name=${name}&create_track=true`).then(() => null)
    },
    selectClip (trackName: string) {
        fetch(`${Config.P0_API_URL}/clip/select?track_name=${trackName}`).then(() => null)
    },
    toggleClip (trackName: string) {
        fetch(`${Config.P0_API_URL}/clip/toggle?track_name=${trackName}`).then(() => null)
    }
}

export default API
