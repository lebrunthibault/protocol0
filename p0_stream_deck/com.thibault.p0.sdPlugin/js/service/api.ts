import Config from '../config'

const API = {
    drumRackToSimpler () {
        fetch(`${Config.P0_API_URL}/drum_rack_to_simpler`).then(() => null)
    },
    loadDevice (name: string) {
        fetch(`${Config.P0_API_URL}/load_device?name=${name}`).then(() => null)
    },
    loadDrumSamples (category: string) {
        fetch(`${Config.P0_API_URL}/load_drum_rack/?category=drums&subcategory=${category}`).then(() => null)
    },
    loadVocalSamples (category: string) {
        fetch(`${Config.P0_API_URL}/load_drum_rack/?category=vocals&subcategory=${category}`).then(() => null)
    },
    openSet (shortcutName: string) {
        fetch(`${Config.P0_API_URL}/set/open?name=${shortcutName}`).then(() => null)
    },
    selectOrLoadDevice (name: string) {
        fetch(`${Config.P0_API_URL}/select_or_load_device?name=${name}`).then(() => null)
    }
}

export default API
