// noinspection TypeScriptValidateJSTypes

import { z } from 'zod'
import AbletonSetSchema from './ableton_set'

const SampleCategoriesSchema = z.object({
    drums: z.array(z.string()),
    vocals: z.array(z.string())
})

const DeviceGroupSchema = z.object({
    name: z.string(),
    devices: z.array(z.string())
})

const ServerStateSchema = z.object({
    active_set: z.nullable(AbletonSetSchema),
    sample_categories: SampleCategoriesSchema,
    favorite_device_names: z.array(z.array(z.union([z.string(), DeviceGroupSchema])))
})

// extract the inferred type
type ServerState = z.infer<typeof ServerStateSchema>;
type DeviceGroup = z.infer<typeof DeviceGroupSchema>;

export type { ServerState, DeviceGroup }
export default ServerStateSchema
