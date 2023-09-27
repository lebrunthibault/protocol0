interface SceneData {
    name: string
    index: number
    start_time: number
    end_time: number
    track_names: string[]
}

interface AbletonSetMetadata {
    scenes: SceneData[]
}

// @ts-ignore
interface AbletonSet {
    path: string
    name: string
    metadata: AbletonSetMetadata
    audio_url?: string
}