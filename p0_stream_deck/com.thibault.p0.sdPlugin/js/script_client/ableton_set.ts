// noinspection TypeScriptValidateJSTypes

import { z } from 'zod'

const SceneTrackStateSchema = z.object({
    track_name: z.string(),
    group_name: z.string(),
    has_clip: z.boolean(),
    is_playing: z.boolean(),
    is_armed: z.boolean()
})

const AbletonSceneSchema = z.object({
    drums: z.array(SceneTrackStateSchema),
    harmony: z.array(SceneTrackStateSchema),
    melody: z.array(SceneTrackStateSchema),
    bass: z.array(SceneTrackStateSchema)
})

const AbletonSetCurrentStateSchema = z.object({
    selected_scene: AbletonSceneSchema,
    drum_rack_visible: z.boolean()
})

// extract the inferred type
type AbletonSetCurrentState = z.infer<typeof AbletonSetCurrentStateSchema>;
type SceneTrackState = z.infer<typeof SceneTrackStateSchema>;

export type { AbletonSetCurrentState, SceneTrackState }
export default AbletonSetCurrentStateSchema
