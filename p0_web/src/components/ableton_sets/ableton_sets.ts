interface AbletonSetPath {
    filename: string
    name: string
    saved_at: number
}

interface MetadataFileInfo {
    filename: string
    saved_at: number
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

interface AbletonSetMetadata {
    path_info: MetadataFileInfo
    scenes: SceneStats[]
    stars: number
    comment: string
}

interface AudioFileInfo {
    filename: string
    saved_at: number
    url: string
    outdated: boolean
}

// @ts-ignore
interface AbletonSet {
    path_info: AbletonSetPath
    metadata: AbletonSetMetadata
    audio_info?: AudioFileInfo
}