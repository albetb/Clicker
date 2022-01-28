import utils
import time
from datetime import timedelta

# --> Time functions <--
def current_time() -> str:
    return time.strftime("%Y %m %d %H %M %S", time.localtime())

def get_time(time_str: str) -> time.struct_time:
    return time.strptime(time_str, "%Y %m %d %H %M %S")

def set_time(time_obj: time.struct_time) -> str:
    return time.strftime("%Y %m %d %H %M %S", time_obj)

def get_future_time(timedelta: timedelta, starting_time_str = "") -> time.struct_time:
    return (time.localtime()() if starting_time_str == "" else get_time(starting_time_str)) + timedelta

def get_time_delta(time_str1: str, time_str2 = "") -> timedelta:
    return (time.localtime()() if time_str2 == "" else get_time(time_str2)) - get_time(time_str1)

def is_time_passed(time_str: str) -> bool:
    return get_time(time_str) >= time.localtime()()

def format_time(time_obj: time.struct_time) -> str:
    return " ".join(
        f"{time_obj.days}d" if time_obj.days > 0 else "",
        f"{time_obj.hours}h" if time_obj.minutes > 0 else "",
        f"{time_obj.minutes}m" if time_obj.minutes > 0 else "",
        f"{time_obj.seconds}s" if time_obj.seconds > 0 else ""
    )

DELTA_ZERO = timedelta(days = 0, hours = 0, minutes = 0, seconds = 0)

# --> Event class <--
class Event:
    def __init__(self, name, event_type = "", counter = 0, days = 0, hours = 0, minutes = 0, seconds = 0):
        self.name = name # Event name
        self.event_type = event_type # Event type (eg. resouces or construction)
        self.counter = counter # Not time related, eventually contains a number who give reward at the event end
        self.starting_time = time.localtime() # Don't change once is initialized
        self.timedelta = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds) # Event duration

        def ending_time(self) -> time.struct_time:
            return self.starting_time + self.timedelta

        def is_event_passed(self) -> bool:
            return time.localtime() >= ending_time()

        def lasting_time(self) -> time.time.struct_time:
            return ending_time() - time.localtime()

        def subtract_time(self, days = 0, hours = 0, minutes = 0, seconds = 0):
            delta = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
            self.timedelta = max(self.timedelta - delta, DELTA_ZERO)

class EventList:
    def __init__(self, event_list = []):
        self.event_list = event_list

        def __add__(self, other):
            self.event_list.append(other.event_list)

        def push(self, event):
            self.event_list.append(event)

        def remove_event(self, event):
            self.event_list.remove(event)

        def remove(self, event_name):
            for event in self.event_list:
                if event.name == event_name:
                    remove_event(event)
        
        def check_expired(self) -> list:
            return [event for event in self.event_list if event.is_event_passed()]


print(current_time())


        

    