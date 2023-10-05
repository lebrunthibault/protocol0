interface SceneData {
    name: string
    index: number
    start_time: number
    end_time: number
    track_names: string[]
}

interface AbletonSetMetadata {
    filename: string
    saved_at: number
    scenes: SceneData[]
}

interface AudioFileInfo {
    filename: string
    url: string
    saved_at: number
    outdated: boolean
}

// @ts-ignore
interface AbletonSet {
    filename: string
    saved_at: number
    name: string
    metadata: AbletonSetMetadata
    audio?: AudioFileInfo
}