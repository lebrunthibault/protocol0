import EventBus from "../../com.thibault.p0.sdPlugin/js/event_bus";
import ActionGroupAppearedEvent from "../../com.thibault.p0.sdPlugin/js/action/action_group/action_group_appeared_event";
import {actionTypes} from "../../com.thibault.p0.sdPlugin/js/action/action_type";

test('event_bus', function() {
    expect(true).toBe(true);

    let called = false
    const subscriber = () => called = true
    EventBus.subscribe(ActionGroupAppearedEvent, subscriber)
    EventBus.emit(new ActionGroupAppearedEvent(actionTypes.OPEN_SET))
    expect(called).toBe(true);
});