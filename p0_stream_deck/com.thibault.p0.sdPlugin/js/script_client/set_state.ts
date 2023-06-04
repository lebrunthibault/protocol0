// noinspection TypeScriptValidateJSTypes

import { z } from 'zod'

const AbletonSetSchema = z.object({
    id: z.string(),
    title: z.string(),
    muted: z.boolean(),
    drum_rack_visible: z.boolean()
})

// extract the inferred type
type AbletonSet = z.infer<typeof AbletonSetSchema>;

export type { AbletonSet }
export default AbletonSetSchema
