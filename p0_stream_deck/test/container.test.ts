import 'reflect-metadata';
import { container } from 'tsyringe';

import ActionFactory from "../com.thibault.p0.sdPlugin/js/action/action_factory";

test('container', function() {
    container.resolve(ActionFactory).createActions();
});
