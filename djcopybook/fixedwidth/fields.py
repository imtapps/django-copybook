
import datetime

__all__ = (
    'StringField',
    'IntegerField',
    'DateField',
    'DecimalField',
)

class NOT_PROVIDED(object):
    pass

class FieldLengthError(Exception):
    pass

def str_padding(length, val):
    "Formats value giving it a right space padding up to a total length of 'length'"
    return '{:<{fill}}'.format(val, fill=length)

def int_padding(length, val):
    "Formats value giving it left zeros padding up to a total length of 'length'"
    return '{:0>{fill}}'.format(val, fill=length)

def float_padding(length, val, decimals=2):
    "Pads zeros to left and right to assure proper length and precision"
    return '{:0>{fill}.{precision}f}'.format(float(val), fill=length, precision=decimals)


class FixedWidthField(object):
    # set a default validators?
    attname = '' # will get set to the name of the field this descriptor is being used as

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, length, default=NOT_PROVIDED):
        self.length = length
        self.default = default

        # Increase the creation counter, and save our local copy.
        self.creation_counter = FixedWidthField.creation_counter
        FixedWidthField.creation_counter += 1

    def __get__(self, instance, txpe):
        try:
            return getattr(instance, self._get_instance_field())
        except AttributeError:
            return self.get_default()

    def __set__(self, instance, val):
        setattr(instance, self._get_instance_field(), self.to_python(val))

    def _get_instance_field(self):
        return "%s_%s" % (self.attname, self.creation_counter)

    def has_default(self):
        return self.default is not NOT_PROVIDED

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default

    def to_python(self, val):
        if val is None:
            return val
        return str(val)

    def to_record(self, val):
        if val is None:
            val = ''
        return str_padding(self.length, val)
    
    def get_record_value(self, val):
        record_val = self.to_record(val)
        if len(record_val) > self.length:
            err = "'{attname}' value '{}' is longer than {length} chars.".format(record_val, **self.__dict__)
            raise FieldLengthError(err)
        return record_val

class StringField(FixedWidthField):
    pass

class IntegerField(FixedWidthField):

    def to_python(self, val):
        if val is None:
            return val
        return int(val)

    def to_record(self, val):
        if val is None:
            val = 0
        return int_padding(self.length, val)

class DecimalField(FixedWidthField):

    def __init__(self, length, default=NOT_PROVIDED, decimals=2):
        self.decimals = decimals
        super(DecimalField, self).__init__(length, default)

    def to_python(self, val):
        if val is None:
            return val
        return float(val)

    def to_record(self, val):
        if val is None:
            val = 0
        return float_padding(self.length, val, decimals=self.decimals)

class DateField(FixedWidthField):

    def __init__(self, length, default=NOT_PROVIDED, format="%Y-%m-%d"):
        self.format = format
        super(DateField, self).__init__(length, default)

    def to_python(self, val):
        if val is None:
            return val
        if isinstance(val, datetime.datetime):
            return val.date()
        if isinstance(val, datetime.date):
            return val

        return datetime.datetime.strptime(val, self.format).date()

    def to_record(self, val):
        if not val:
            return str_padding(self.length, '')
        return val.strftime(self.format)

#Todo: fields needed: ListField