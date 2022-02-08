from datetime import timedelta, datetime

# ----------> Time functions <----------------------------------------

TIME_FORMATTING = "%Y-%m-%dT%H:%M:%S"

def now() -> datetime:
    """ Return a datetime with current date and time """
    return datetime.today()

def current_time() -> str:
    """ Return a formatted string with current date and time """
    return now().strftime(TIME_FORMATTING)

def get_time(time_str: str) -> datetime:
    """ Return a datetime form a formatted string """
    return datetime.strptime(time_str, TIME_FORMATTING)

def set_time(time_obj: datetime) -> str:
    """ Return a formatted string form a datetime """
    if time_obj == None: return ""
    return time_obj.strftime(TIME_FORMATTING)

def format_time_delta(time_obj: timedelta) -> str:
    """ Return a formatted string from a time delta object """
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

def format_time_delta_str(days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> str:
    """ Return a formatted string from a time delta as days, hours, minutes, seconds """
    return format_time_delta(timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds))

def offline_time(time: str) -> int:
    """ Return the number of seconds from last online time """
    return int((get_time(current_time()) - (get_time(time))).seconds)

# ----------> Event class <----------------------------------------

class Event:
    def __init__(self, name: str, type: str = "", counter: float = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> None:
        self.name = name # Event name
        self.type = type # Event type (eg. Resources or Building)
        self.counter = counter # Not time related, eventually contains a number who give reward at the event end
        self.starting_time = now() # Don't change once is initialized except when loading game
        self.timedelta = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds) # Event duration

    def set_starting_time(self, starting_time: str or datetime) -> None:
        """ Take a string o a datetime object and set it as current starting time """
        if isinstance(starting_time, str):
            if starting_time == "":
                self.starting_time = None
            else:
                self.starting_time = get_time(starting_time)
        elif isinstance(starting_time, datetime):
            self.starting_time = starting_time

    def set_timedelta(self, timedelta_seconds: int) -> None:
        """ Set a new time delta to event """
        self.timedelta = timedelta(seconds = timedelta_seconds)

    def ending_time(self) -> datetime:
        """ Return ending time of event """
        return (self.starting_time if self.starting_time != None else now()) + self.timedelta

    def is_event_passed(self) -> bool:
        """ Return True if ending time of event is passed """
        return self.starting_time != None and now() >= self.ending_time() - timedelta(seconds = 1)

    def lasting_time(self) -> timedelta:
        """ Return remaining time to end of event """
        return self.ending_time() - now()

    def format_lasting_time(self) -> str:
        """ Return remaining time to end formatted for displaying """
        if self.starting_time == None:
            return format_time_delta(self.timedelta)
        return format_time_delta(max(self.lasting_time(), timedelta(seconds=0)))

    def add_time(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> None:
        """ Add time to remaining time of event """
        self.timedelta = min(self.timedelta + timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds), timedelta(days = 10))

    def subtract_time(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> None:
        """ Remove time from remaining time of event """
        self.timedelta = max(self.timedelta - timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds), timedelta(seconds = 0))

    def add_counter(self, value: float) -> None:
        """ Add a value to counter """
        self.counter += value

    def serialize_event(self) -> dict:
        """ Serialize event as a dictionary for saving it """
        return {
            "name": self.name,
            "type": self.type,
            "counter": str(self.counter),
            "starting_time": set_time(self.starting_time),
            "timedelta": str(self.timedelta.seconds)
        }

class EventQueue:
    def __init__(self, event_list: list = []) -> None:
        self.event_list = event_list

    def deserialize_event_list(self, event_dict_list: list) -> None:
        """ Load a list of event from a list of dictionary """
        for event_dict in event_dict_list:
            event = Event(name = event_dict["name"],
                          type = event_dict["type"],
                          counter = float(event_dict["counter"])
                        )
            event.set_starting_time(event_dict["starting_time"])
            event.set_timedelta(int(event_dict["timedelta"]))
            self.push(event)
    
    def serialize_event_list(self) -> None:
        """ Serialize event list as a list of dictionary """
        return [event.serialize_event() for event in self.event_list]

    def push(self, event: Event) -> None:
        """ Insert an event in list """
        if event.type == "Building":
            event.counter = self.count_event_type("Building")
            if event.counter > 0: # Block building if there is another one in construction
                event.starting_time = None
        self.event_list.append(event)

    def remove_event(self, event: Event) -> None:
        """ Given an event remove that from list """
        self.event_list.remove(event)
        if event.type == "Building":
            for evt in self.event_list:
                if evt.type == "Building":
                    evt.counter -= 1
                    if evt.counter == 0: # Start next building
                        evt.starting_time = now()

    def remove(self, event_name: str) -> None:
        """ Given a name remove the first event with that name from list """
        for event in self.event_list:
            if event.name == event_name:
                self.remove_event(event)
    
    def expired_event(self) -> list:
        """ Return a list of event with ending time more or equal of current time """
        return [event for event in self.event_list if event.is_event_passed()]

    def remove_expired(self) -> None:
        """ Remove all expired event from list """
        for event in self.expired_event():
            self.remove_event(event)

    def event_exist(self, event_name: str) -> bool:
        """ Given a name return True if exist an event with that name """
        return self.count_event_name(event_name) > 0

    def event_type_exist(self, event_type: str) -> bool:
        """ Given a type return True if exist an event with that type """
        return self.count_event_type(event_type) > 0

    def count_event_type(self, event_type: str) -> bool:
        """ Given a type return the number of event with that type """
        return len([1 for event in self.event_list if event.type == event_type])

    def count_event_name(self, event_name: str) -> bool:
        """ Given a name return the number of event with that name """
        return len([1 for event in self.event_list if event.name == event_name])

    def select_event(self, event_name: str) -> Event:
        """ Given a name return first event with that name """
        return next((event for event in self.event_list if event.name == event_name), None)

    def building_queue(self) -> list:
        """ Return a list of all building events in order """
        building_queue = [event for event in self.event_list if event.type == "Building"]
        building_queue.sort(key=lambda event: event.counter)
        return building_queue