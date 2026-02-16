default time_manager = TimeManager()

init 10 python:
    class TimeManager(object):
        def __init__(self, hour=8, minute=0, day=1):
            self.hour, self.minute = hour, minute
            self.day = day
        
        @property
        def time_string(self): return "{:02d}:{:02d} (Day {})".format(self.hour, self.minute, self.day)
        
        @property
        def time_of_day(self):
            if 5 <= self.hour < 12: return "Morning"
            elif 12 <= self.hour < 17: return "Afternoon"
            elif 17 <= self.hour < 21: return "Evening"
            else: return "Night"
        
        @property
        def total_minutes(self):
            return self.day * 1440 + self.hour * 60 + self.minute

        def advance(self, mins):
            self.minute += mins
            while self.minute >= 60:
                self.minute -= 60
                self.hour += 1
            while self.hour >= 24:
                self.hour -= 24
                self.day += 1
            
            # notify world of time change
            world.update_schedules()
            # tick timed effects
            try:
                character.tick_effects()
            except Exception:
                pass
    
    def reload_time_manager(data):
        time_manager.hour = data.get("time", {}).get("hour", 8)
        time_manager.minute = data.get("time", {}).get("minute", 0)
        time_manager.day = data.get("time", {}).get("day", 1)