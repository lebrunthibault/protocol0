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

const AbletonSetSchema = z.object({
    current_state: AbletonSetCurrentStateSchema
})

// extract the inferred type
type AbletonSet = z.infer<typeof AbletonSetSchema>;
type SceneTrackState = z.infer<typeof SceneTrackStateSchema>;

export type { AbletonSet, SceneTrackState }
export default AbletonSetSchema
