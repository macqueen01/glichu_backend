import datetime

from main.Models.ScrollsModel import Scrolls

class TimelineStamp:
    
    def __init__(self, datetime, index):
        self.datetime = datetime
        self.index = index

        print(datetime)

    def set_next(self, next):
        self.next = next
    
    def has_next(self):
        return self.next != None
    
    # method that retuns the time difference between this stamp and the next stamp
    def execute_time(self):
        return self.datetime

    
class IndexTimeline:

    def __init__(self, timeline_json, length):
        self.sentinel = self._parse_timeline_from_json(timeline_json)
        self.length = length
    
    def _parse_timeline_from_json(self, timeline_json):

        if timeline_json == 'null' or timeline_json == None:
            return None

        if timeline_json['next'] == 'null':
            timestamp = TimelineStamp(
                datetime.datetime.strptime(timeline_json['time'], '%Y-%m-%d %H:%M:%S.%f'),
                timeline_json['index']
            )
            timestamp.set_next(None)
            return timestamp
        
        current_stamp = TimelineStamp(
            datetime.datetime.strptime(
                timeline_json['time'], '%Y-%m-%d %H:%M:%S.%f'),
            timeline_json['index']
            )
        
        current_stamp.set_next(self._parse_timeline_from_json(timeline_json['next']))

        return current_stamp

class Remix:

    def __init__(self, title, timeline, scrolls_id):
        self._timeline = self.timeline
        self._title = title
        self._scrolls = Scrolls.objects.get(id=scrolls_id)

    def get_title(self):
        return self._title
    
    def get_length(self):
        return self._timeline.length
    
    def get_scrolls(self):
        scrolls = Scrolls.objects.get(id=self._scrolls)
        return scrolls

    def get_timeline(self):
        return self._timeline

    def has_remix_video(self):
        pass




