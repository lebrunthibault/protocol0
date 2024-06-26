interface PathInfo {
    relative_name: string
    name: string
    has_own_folder: boolean
    saved_at: number
    place: AbletonSetPlace
}

interface SceneData {
    name: string
    index: number
    start: number
    end: number
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
  IDEA = "IDEA",
  TRACK = "TRACK",
  RELEASE = "RELEASE"
}

interface AbletonSetMetadata {
    path_info: PathInfo
    scenes: SceneStats[]
    stars: number
    comment: string
    stage: SetStage
    tempo: number
}

interface AudioInfo {
    url: string
    outdated: boolean
}

interface AbletonSet {
    path_info: PathInfo
    metadata: AbletonSetMetadata
    audio?: AudioInfo
}

export {AbletonSet, AbletonSetPlace, SceneData}