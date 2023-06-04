import 'reflect-metadata'
import { container } from 'tsyringe'
import ActionFactory from './js/action/action_factory'
import ScriptClient from './js/script_client/script_client'
import DB from './js/service/db'
import ProfileListeners from './js/domain/profile/profile_listeners'

$SD.on('connected', async (event: object) => {
    await initApplication(event)
})

async function initApplication (event: any) {
    container.resolve(DB).deviceId = event.applicationInfo.devices[0].id

    container.resolve(ActionFactory).createActions()
    container.resolve(ProfileListeners).setup()

    await container.resolve(ScriptClient).connect()
}
