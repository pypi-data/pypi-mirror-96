from lxml import etree
import dateutil.parser

from .point import Point
from .detail import Detail
from . import geochat

class Event:
    def __init__(self, uid=None, etype=None, how=None,
                    time=None, start=None, stale=None,
                    version="2.0"):
        self.version = version
        self.uid = uid
        self.etype = etype
        self.how = how
        self.time = time
        self.start = start
        self.stale = stale

        self.point = Point()
        self.detail = None

    def __repr__(self):
        return '<Event uid="%s" etype="%s" time="%s">' % (self.uid, self.etype, self.time)

    @staticmethod
    def from_elm(elm):
        if not etree.iselement(elm):
            raise TypeError('Cannot create Event from %s' % type(elm))
        if elm.tag != 'event':
            raise ValueError('Cannot create Event from %s' % elm.tag)

        time = dateutil.parser.isoparse(elm.get('time')).replace(tzinfo=None)
        start = dateutil.parser.isoparse(elm.get('start')).replace(tzinfo=None)
        stale = dateutil.parser.isoparse(elm.get('stale')).replace(tzinfo=None)

        ret = Event(
            version=elm.get('version'),
            uid=elm.get('uid'),
            etype=elm.get('type'),
            how=elm.get('how'),
            time=time,
            start=start,
            stale=stale
        )

        for child in elm.iterchildren():
            if child.tag == 'point':
                ret.point = Point.from_elm(child)
            elif child.tag == 'detail':
                if ret.etype == 'b-t-f':
                    ret.detail = geochat.GeoChat.from_elm(child, event=ret)
                else:
                    ret.detail = Detail.from_elm(child, event=ret)

        return ret

    @property
    def as_element(self):
        ret = etree.Element('event')
        ret.set('version', self.version)
        ret.set('uid', self.uid)
        ret.set('type', self.etype)
        ret.set('how', self.how)
        ret.set('time', self.time.isoformat(timespec='milliseconds') + 'Z')
        ret.set('start', self.start.isoformat(timespec='milliseconds') + 'Z')
        ret.set('stale', self.stale.isoformat(timespec='milliseconds') + 'Z')
        ret.append(self.point.as_element)
        if self.detail is not None:
            ret.append(self.detail.as_element)

        return ret
