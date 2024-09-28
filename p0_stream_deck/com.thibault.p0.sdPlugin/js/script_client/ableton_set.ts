// noinspection TypeScriptValidateJSTypes

import { z } from 'zod'

const SceneTrackStateSchema = z.object({
    track_name: z.string(),
    group_name: z.string(),
    has_clip: z.boolean(),
    is_playing: z.boolean(),
    is_armed: z.boolean()
})

// extract the inferred type
type SceneTrackState = z.infer<typeof SceneTrackStateSchema>;

export type { SceneTrackState }
