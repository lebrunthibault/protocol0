// noinspection TypeScriptValidateJSTypes

import { z } from 'zod'

const DeviceGroupSchema = z.object({
    name: z.string(),
    devices: z.array(z.string())
})
//
// const ServerStateSchema = z.object({
//     active_set: z.nullable(AbletonSetSchema),
//     // sample_categories: SampleCategoriesSchema,
//     favorite_device_names: z.array(z.array(z.union([z.string(), DeviceGroupSchema])))
// })

// extract the inferred type
type DeviceGroup = z.infer<typeof DeviceGroupSchema>;

export type { DeviceGroup }
