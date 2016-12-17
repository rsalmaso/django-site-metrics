from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.utils.encoding import force_text
from django.utils.functional import Promise
import datetime


class JSONEncoder(DjangoJSONEncoder):
    def default(self, obj):  # noqa
        if isinstance(obj, datetime.timedelta):
            return str(obj.total_seconds())
        ####
        elif isinstance(obj, QuerySet):
            return tuple(obj)
        elif hasattr(obj, 'tolist'):
            # Numpy arrays and array scalars.
            return obj.tolist()
        elif hasattr(obj, '__getitem__'):
            try:
                return dict(obj)
            except:
                pass
        elif hasattr(obj, '__iter__'):
            return tuple(item for item in obj)
        elif isinstance(obj, Promise):
            # added in django 1.10
            return force_text(obj)
        return super().default(obj)
