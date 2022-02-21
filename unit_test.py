import unittest

from common import EventDispatcher
from ground_handling import GroundHandling
from utils.reader import generate_instances
from utils.log import export_log


def one_day_data_test():
    """The unit of time is minute and simulation starts at 0 time."""
    gate_position_list, aircraft_list, vehicle_list = generate_instances('./data/one_day_test_data_including_delay.csv')
    ground_handling = GroundHandling(aircraft_list, vehicle_list)
    event_dispatcher = EventDispatcher(aircraft_list, vehicle_list, ground_handling)

    event_list = []
    while not event_dispatcher.is_finished():
        first_event = None
        for aircraft in aircraft_list:
            event = aircraft.get_current_event()
            if event is None:
                continue
            event.update()
            if first_event is None:
                first_event = event
            # there is no difference between > and >=
            elif first_event.get_triggering_timestamp() > event.get_triggering_timestamp():
                first_event = event

        for veh in vehicle_list:
            event = veh.get_current_event()
            if event is None or veh.get_trip() is None:
                continue
            event.update()
            if first_event is None:
                first_event = event
            # there is no difference between > and >=
            elif first_event.get_triggering_timestamp() > event.get_triggering_timestamp():
                first_event = event

        event = ground_handling.get_current_event()
        if event is None:
            continue
        event.update()
        if first_event is None:
            first_event = event
        # the event generated by ground handling is always the last to execute
        # when the triggering times of events are the same, so > has to be used rather than >=
        elif first_event.get_triggering_timestamp() > event.get_triggering_timestamp():
            first_event = event

        first_event.update()
        first_event.execute()
        event_list.append(first_event)

    events_info_list = []
    for event in event_list:
        events_info_list.append(event.get_log_info())

    trips_info_list = []
    for veh in vehicle_list:
        for trip in veh.get_trip_list():
            log_info = trip.get_log_info()
            log_info['vehicle_id'] = veh.get_id()
            trips_info_list.append(log_info)
    export_log(events_info_list, trips_info_list)
    print('One day data test pass.')
    return True


class MyTestCase(unittest.TestCase):
    def test_one_day_data(self):
        self.assertEqual(True, one_day_data_test())


if __name__ == '__main__':
    unittest.main()
