from datetime import timedelta, time, datetime

# --> Time functions <--
def now() -> datetime:
    return datetime.today()

def current_time() -> str:
    return now().strftime("%Y %m %d %H %M %S")

def get_time(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%Y %m %d %H %M %S")

def set_time(time_obj: datetime) -> str:
    return time_obj.strftime("%Y %m %d %H %M %S")

def format_time_delta(time_obj: timedelta) -> str:
    days = time_obj.seconds // (60 * 60 * 24)
    hours = time_obj.seconds // (60 * 60) - days * 24
    minutes = time_obj.seconds // 60 - days * 24 - hours * 60
    seconds = time_obj.seconds - days * 24 - hours * 60 - minutes * 60
    return " ".join([
        f"{days}d" if time_obj.seconds >= 60 * 60 * 24 else "",
        f"{hours}h" if time_obj.seconds >= 60 * 60 else "",
        f"{minutes}m" if time_obj.seconds >= 60 else "",
        f"{seconds}s" if time_obj.seconds > 1 else ""]
    )

def format_time_delta_str(days = 0, hours = 0, minutes = 0, seconds = 0) -> str:
    return format_time_delta(timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds))

# --> Event class <--
class Event:
    def __init__(self, name, event_type = "", counter = 0, days = 0, hours = 0, minutes = 0, seconds = 0):
        self.name = name # Event name
        self.event_type = event_type # Event type (eg. resouces or construction)
        self.counter = counter # Not time related, eventually contains a number who give reward at the event end
        self.starting_time = now() # Don't change once is initialized
        self.timedelta = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds) # Event duration

    def set_starting_time(self, starting_time):
        if isinstance(starting_time, str):
            self.starting_time = get_time(starting_time)
        elif isinstance(starting_time, datetime):
            self.starting_time = starting_time

    def set_timedelta(self, timedelta_seconds: str):
        if timedelta_seconds.isdigit():
            self.timedelta = timedelta(seconds = int(timedelta_seconds))

    def ending_time(self) -> time:
        return self.starting_time + self.timedelta

    def is_event_passed(self) -> bool:
        return now() >= self.ending_time() - timedelta(seconds = 1)

    def lasting_time(self) -> time:
        return self.ending_time() - now()

    def format_lasting_time(self) -> str:
        return format_time_delta(self.lasting_time())

    def subtract_time(self, days = 0, hours = 0, minutes = 0, seconds = 0):
        delta = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
        self.timedelta = max(self.timedelta - delta, timedelta(days = 0, hours = 0, minutes = 0, seconds = 0))

    def add_counter(self, value):
        self.counter += value

    def serialize_event(self) -> dict:
        return {
            "name": self.name,
            "event_type": self.event_type,
            "counter": str(self.counter),
            "starting_time": set_time(self.starting_time),
            "timedelta": str(self.timedelta.seconds)
        }

class EventList:
    def __init__(self, event_list = []):
        self.event_list = event_list

    def load_from_dict(self, event_dict_list):
        for event_dict in event_dict_list:
            event = Event(name = event_dict["name"],
                          event_type = event_dict["event_type"],
                          counter = float(event_dict["counter"])
                        )
            event.set_starting_time(event_dict["starting_time"])
            event.set_timedelta(event_dict["timedelta"])
            self.push(event)
    
    def serialize_event_list(self):
        return [event.serialize_event() for event in self.event_list]
                    
    def push(self, event: Event):
        if self.event_exist(event.name):
            self.remove(event.name)
        self.event_list.append(event)

    def remove_event(self, event: Event):
        self.event_list.remove(event)

    def remove(self, event_name: str):
        for event in self.event_list:
            if event.name == event_name:
                self.remove_event(event)
    
    def check_expired(self) -> list:
        return [event for event in self.event_list if event.is_event_passed()]

    def remove_expired(self):
        for event in self.check_expired():
            self.remove_event(event)

    def event_exist(self, event_name: str) -> bool:
        return len([event for event in self.event_list if event.name == event_name]) >= 1

    def select_event(self, event_name: str) -> Event:
        if not self.event_exist(event_name):
            return Event("")
        return [event for event in self.event_list if event.name == event_name][0]