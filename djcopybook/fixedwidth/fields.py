
import datetime

__all__ = (
    'StringField',
    'IntegerField',
    'DateField',
    'DecimalField',
    'FragmentField',
    'ListField',
)

class NOT_PROVIDED(object):
    pass


class FieldLengthError(Exception):
    pass


def str_padding(length, val):
    "Formats value giving it a right space padding up to a total length of 'length'"
    return '{0:<{fill}}'.format(val, fill=length)


def int_padding(length, val):
    "Formats value giving it left zeros padding up to a total length of 'length'"
    return '{0:0>{fill}}'.format(val, fill=length)


def float_padding(length, val, decimals=2):
    "Pads zeros to left and right to assure proper length and precision"
    return '{0:0>{fill}.{precision}f}'.format(float(val), fill=length, precision=decimals)


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
        return "{attname}_{creation_counter}".format(**self.__dict__)

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
        return str(val).rstrip()

    def to_record(self, val):
        if val is None:
            val = ''
        return str_padding(self.length, val)

    def get_record_value(self, val):
        record_val = self.to_record(val)
        self._check_record_length(record_val)
        return record_val

    def _check_record_length(self, record_val):
        if len(record_val) > self.length:
            err = "'{attname}' value '{0}' is longer than {length} chars.".format(record_val, **self.__dict__)
            raise FieldLengthError(err)


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


class FragmentField(FixedWidthField):
    """
    Allows you to create a field on a record that is itself a complete
    record. Similar to a ``ListField`` except it only occurs once.


    class Phone(Record):
      area_code = fields.IntegerField(length=3)
      prefix = fields.IntegerField(length=3)
      line_number = fields.IntegerField(length=4)

    class Contact(Record):
      name = fields.StringField(length=100)
      phone_number = fields.FragmentField(record=Phone)
      email = fields.StringField(length=100)

    """

    def __init__(self, record):
        self.record_class = record
        super(FragmentField, self).__init__(len(record))

    def to_python(self, val):
        """
        :returns:
            Always returns an instance of the record class.
        """
        if val is None:
            return self.record_class()
        if isinstance(val, basestring):
            return self.record_class.from_record(val)
        elif isinstance(val, self.record_class):
            return val
        else:
            msg = "Redefined field must be a string or {record} instance.".format(
                record=self.record_class.__name__)
            raise TypeError(msg)

    def to_record(self, val):
        """
        :param val:
            val will either be None or an instance of ``self.record_class``
        :returns:
            Always returns a string spaced properly for self.record_class.
        """
        if val is None:
            return self.record_class().to_record()
        return val.to_record()


class ListField(FixedWidthField):
    """
    ListField allows you to have a field made up of a number of
    other records. Similar to COBOL's OCCURS.

    parameters:
      - record: which Record the field is made up of
      - length: how many times that record occurs

    """

    def __init__(self, record, length=1):
        self.record_class = record
        super(ListField, self).__init__(length)

    def _get_records_from_string(self, val):
        records = []
        record_len = len(self.record_class)
        for _ in range(self.length):
            records.append(self.record_class.from_record(val[:record_len]))
            val = val[record_len:]
        return records

    def to_python(self, val):
        """
        the python representation should be a list of instantiated
        Record classes.
        """
        if isinstance(val, basestring):
            return self._get_records_from_string(val)
        elif not all([isinstance(r, self.record_class) for r in val]):
            msg = "List field must contain instances of '{0}'.".format(self.record_class.__name__)
            raise TypeError(msg)
        return list(val)

    def get_default(self):
        return []

    def to_record(self, val):
        """
        We receive a list of Record classes and must make sure
        we have a complete record we're giving back.
        """
        while len(val) < self.length:
            val.append(self.record_class())
        return ''.join([v.to_record() for v in val])

    def _check_record_length(self, record_val):
        max_record_length = len(self.record_class)
        record_length = len(record_val)
        if record_length > (self.length * max_record_length):
            record_count = record_length / max_record_length
            msg = "'{attname}' contains {cnt} records but can only have {length}.".format(cnt=record_count,
                                                                                          **self.__dict__)
            raise FieldLengthError(msg)