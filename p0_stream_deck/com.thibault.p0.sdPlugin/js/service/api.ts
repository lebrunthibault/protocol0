import Config from '../config'

const API = {
    drumRackToSimpler () {
        fetch(`${Config.P0_API_URL}/drum_rack_to_simpler`).then(() => null)
    },
    loadDevice (name: string) {
        fetch(`${Config.P0_API_URL}/load_device?name=${name}`).then(() => null)
    },
    loadDeviceInNewTrack (name: string) {
        fetch(`${Config.P0_API_URL}/load_device?name=${name}&create_track=true`).then(() => null)
    },
    loadDrumSamples (category: string) {
        fetch(`${Config.P0_API_URL}/load_drum_rack/?category=drums&subcategory=${category}`).then(() => null)
    },
    loadVocalSamples (category: string) {
        fetch(`${Config.P0_API_URL}/load_drum_rack/?category=vocals&subcategory=${category}`).then(() => null)
    },
    selectClip (trackName: string) {
        fetch(`${Config.P0_API_URL}/clip/select?track_name=${trackName}`).then(() => null)
    },
    toggleClip (trackName: string) {
        fetch(`${Config.P0_API_URL}/clip/toggle?track_name=${trackName}`).then(() => null)
    }
}

export default API
