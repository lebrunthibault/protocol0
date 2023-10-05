// noinspection TypeScriptValidateJSTypes

import { z } from 'zod'

const AbletonSetCurrentStateSchema = z.object({
    drum_rack_visible: z.boolean()
})

const AbletonSetSchema = z.object({
    id: z.string(),
    title: z.string(),
    muted: z.boolean(),
    current_state: AbletonSetCurrentStateSchema
})

// extract the inferred type
type AbletonSet = z.infer<typeof AbletonSetSchema>;

export type { AbletonSet }
export default AbletonSetSchema
