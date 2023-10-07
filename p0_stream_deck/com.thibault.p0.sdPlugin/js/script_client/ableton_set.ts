// noinspection TypeScriptValidateJSTypes

import { z } from 'zod'

const TracksSchema = z.object({
    drums: z.array(z.string()),
    harmony: z.array(z.string()),
    melody: z.array(z.string()),
    bass: z.array(z.string())
})

const AbletonSetCurrentStateSchema = z.object({
    tracks: TracksSchema,
    drum_rack_visible: z.boolean()
})

const AbletonSetSchema = z.object({
    current_state: AbletonSetCurrentStateSchema
})

// extract the inferred type
type AbletonSet = z.infer<typeof AbletonSetSchema>;

export type { AbletonSet }
export default AbletonSetSchema
