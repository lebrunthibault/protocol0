interface PathInfo {
    filename: string
    name: string
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

enum AbletonSetPlace {
    TRACKS= "TRACKS",
    ARCHIVE = "ARCHIVE",
}

enum SetStage {
  DRAFT = "DRAFT",
  BETA = "BEAT",
  RELEASE = "RELEASE"
}

interface AbletonSetMetadata {
    path_info: PathInfo
    scenes: SceneStats[]
    stars: number
    comment: string
    stage: SetStage
}

interface AudioInfo {
    url: string
    outdated: boolean
}

// @ts-ignore
interface AbletonSet {
    place: AbletonSetPlace
    path_info: PathInfo
    metadata: AbletonSetMetadata
    audio?: AudioInfo
}

export {AbletonSetPlace}