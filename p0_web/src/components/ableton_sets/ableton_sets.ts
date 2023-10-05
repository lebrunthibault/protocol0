interface AbletonSetPath {
    filename: string
    saved_at: number
}

interface AudioFileInfo {
    filename: string
    saved_at: number
    url: string
    outdated: boolean
}

interface SceneData {
    name: string
    index: number
    start_time: number
    end_time: number
    track_names: string[]
}

interface SceneStats {
    filename: string
    saved_at: number
    scenes: SceneData[]
}


// @ts-ignore
interface AbletonSet {
    path_info: AbletonSetPath
    name: string
    metadata_info: SceneStats
    audio_info?: AudioFileInfo
    scene_stats: SceneStats
}