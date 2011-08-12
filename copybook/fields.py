from datetime import datetime, date

__all__ = ("RedefinedField", "ListField", "DecimalField", "IntegerField", "StringField", "DateField")

class Type(object):
    """Type objects will hold onto values that move between cobol copybooks and django models"""

    def __init__(self, value, length, order, path):
        self.value = value
        self.length = length
        self.order = order
        self.path = path
        self.mapped = False

    def strip_self_from_record(self, record):
        """
        strip the value from the beginning of the passed in record and return the new record so the next field
        can strip itself from the beginning of it.
        """
        self.value = record[0:self.length]
        return record[self.length:]

    def populate_from_dict(self, model_dict):
        """
        find the mapping needed for this object in a passed in dictionary
        """
        if self.mapped:
            return

        value = model_dict
        if model_dict and self.path:
            nodes = self.path.split('.')
            for node in nodes:
                if node in value:
                    value = value[node]
                else:
                    value = None
                    break
            else:
                self.mapped = True

            self.value = value

    def number_format(self):
        return "%0" + str(self.length) + "d"

    def char_format(self):
        return "%-" + str(self.length) + "s"

    def trunc_number(self):
        if not self.value:
            self.value = 0
        elif not str(self.value).strip():
            self.value = 0
        try:
            return int(str(self.value)[0:self.trunc_length])
        except ValueError:
            return float(str(self.value)[0:self.trunc_length])

    def trunc_char(self):
        return str(self.value)[0:self.length]

    @property
    def trunc_length(self):
        return self.length

class Date(Type):

    def __init__(self, format, *args, **kwargs):
        super(Date, self).__init__(*args, **kwargs)
        self.format = format
        self.length = kwargs.get('length')

    def to_model(self):
        return datetime.strptime(self.value, self.format)

    def to_copybook(self):
        if isinstance(self.value, (datetime, date)):
            return self.value.strftime(self.format)
        else:
            return self.value or " " * self.length

class Number(Type):
    """Number is used to know when to return a string for COBOL or an actual number for Python"""

    @property
    def format(self):
        return self.number_format()

    def _trunc(self):
        """we need to make sure that we never exceed the max space allowed by the field"""
        return self.trunc_number()

    def __str__(self):
        return self.format % self._trunc()

    def __int__(self):
        return self._trunc()

    def to_model(self):
        return int(self)

    def to_copybook(self):
        return str(self)

class SignedNumber(Number):
    @property
    def format(self):
        return "%+0" + str(self.length) + "d"

    @property
    def trunc_length(self):
        if int(self.value) > 1:
            return self.length - 1
        return self.length

class Decimal(Type):

    def __float__(self):
        if not self.value:
            self.value = 0
        return float(self.value)

    def __str__(self):
        return str(self.value)

    def to_model(self):
        "return an int value to be used by python code"
        return float(self)

    def to_copybook(self):
        "return a string value to be sued by cobol"
        return str(self)

class SignedDecimal(Decimal):

    @property
    def format(self):
        return "%+0" + str(self.length) + ".2f"

    def __str__(self):
        if self.value is None:
            return ' ' * self.length
        return str(self.format % self._trunc())

    @property
    def trunc_length(self):
        if int(self.value) > 1:
            return self.length - 1
        return self.length

    def _trunc(self):
        return float(str(self.value)[-self.trunc_length:])

class Char(Type):
    """Char is used to store character values to pass between python and cobol"""

    @property
    def format(self):
        """format the string padding with spaces to the right"""
        return self.char_format()

    def __str__(self):
        """apply formating and truncate any additional"""
        if not self.value:
            self.value = ""
        return self.format % str(self.value)[0:self.length]

    def to_model(self):
        return str(self)

    def to_copybook(self):
        return str(self)

class NestedCopybook(Type):

    def __init__(self, selector, *args):
        super(NestedCopybook, self).__init__(*args)
        self.selector = selector

    def to_copybook(self):
        return self.value.to_record()

    def strip_self_from_record(self, record):
        """
        strip the value from the beginning of the passed in record and return the new record so the next field
        can strip itself from the beginning of it.
        """
        tmp_rec = record[0:self.length]
        copybook_class = self.selector(tmp_rec)
        self.value = copybook_class.from_record(tmp_rec)
        return record[self.length:]

class List(Type):
    """List is used to store occurances of nested coypbooks"""

    def __init__(self, value, length, order, path, copybook):
        super(List, self).__init__(value, length, order, path)
        self.copybook = copybook

    def populate_from_dict(self, model_list):
        super(List, self).populate_from_dict(model_list)
        values = []
        for model_data in self.value:
            values.append(self.copybook.from_dict(model_data))
        self.value = values

    def to_copybook(self):
        values = [val for val in self.value]
        while len(values) < self.length:
            values.append(self.copybook(to_copybook=True))

        return ''.join([val.to_record() for val in values])

    def to_model(self):
        return self.value

    def strip_self_from_record(self, record):
        """
        strip the value from the beginning of the passed in record and return the new record so the next field
        can strip itself from the beginning of it.
        """
        self.value = []
        for _ in range(self.length):
            copybook = self.copybook(to_model=True)
            record_length = copybook.get_record_length()
            copybook.populate_from_record(record[0:record_length])
            self.value.append(copybook)
            record = record[record_length:]
        return record

class Field(object):
    """
    Field objects are Descriptors that Copybook objects will use to define their fields
    Field objects use the Desciptor interface to add fields like __field_1, __field_2, __field_3
    to the copybook which actually contain the real values that will be passed back and forth from
    python to cobol
    """
    order = 0
    length = 0
    default_value = ''
    default_class = lambda value, length, order, path: None
    to_model = False
    to_copybook = False

    def __init__(self, length=0, order=1, path=None, default=None):
        self.length = length
        self.order = order
        self.path = path
        self.default_value = default or self.default_value

    def build_name(self, order):
        """create hidden name on copybook instance"""
        return "__field_" + str(order)

    def default(self, instance=None):
        """
        return an instance of the default Type class that contains a default value
        for example a Char instance containing an empty string as a value
        """
        return self.default_class(self.default_value, self.length, self.order, self.path)

    def __get__(self, instance, typ):
        field = self.build_name(self.order)
        obj = getattr(instance, field, self.default(instance))
        setattr(instance, field, obj)

        if instance.to_model:
            return obj.to_model()
        elif instance.to_copybook:
            return obj.to_copybook()
        else:
            return obj

    def __set__(self, instance, value):
        field = self.build_name(self.order)
        obj = getattr(instance, field, self.default(instance))
        obj.value = value
        setattr(instance, field, obj)

class DateField(Field):
    default_class = Date
    default_value = ""

    def __init__(self, format, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        self.format = format

    def default(self, instance=None):
        """
        return an instance of the default Type class that contains a default value
        for example a Char instance containing an empty string as a value
        """
        return self.default_class(value=self.default_value, length=self.length, order=self.order,
                                  path=self.path, format=self.format)

class StringField(Field):
    """String field that will format strings to/from cobol copybook and django models"""

    default_class = Char
    default_value = ' '

class IntegerField(Field):

    default_class = Number
    default_value = 0

class SignedIntegerField(Field):
    default_class = SignedNumber
    default_value = 0

class SignedDecimalField(Field):
    default_class = SignedDecimal
    default_value = 0

class DecimalField(Field):
    default_class = Decimal
    default_value = 0

class ListField(Field):
    """
    list field will hold onto a a list of copybook objects - this is to be used for copybook
    fields that 'occur' more than once
    """
    default_class = List
    default_value = []

    def __init__(self, length=0, order=1, path=None, copybook=None):
        super(ListField, self).__init__(length, order, path)
        self.copybook = copybook

    def default(self, instance=None):
        """
        return an instance of the default Type class that contains a default value
        for example a Char instance containing an empty string as a value
        """
        return self.default_class(self.default_value, self.length, self.order, self.path, self.copybook)

class RedefinedField(Field):
    """
    a redefined field is a chunk of a file that can be defined in multiple ways
    """

    default_class = NestedCopybook
    default_value = ""

    def __init__(self, length=0, order=1, path=None, select_func=''):
        super(RedefinedField, self).__init__(length, order, path)
        self.select_copybook_func = select_func

    def default(self, instance):
        """
        return an instance of the default Type class that contains a default value
        for example a Char instance containing an empty string as a value
        """
        selector = getattr(instance, self.select_copybook_func)
        return self.default_class(selector, self.default_value, self.length, self.order, self.path)

class NumberOrChar(Type):
    """NumberOrChar is used when we need to treat numeric values as numbers, but also allow alphabetic values."""

    def __init__(self, value, length, order, path, x):
        self.value = value
        self.length = length
        self.order = order
        self.path = path
        self.mapped = False
        self.x = x

    @property
    def format(self):
        return self.check_numeric(self.number_format, self.char_format)

    def _trunc(self):
        return self.check_numeric(self.trunc_number, self.trunc_char)

    def __str__(self):
        return self.format % self._trunc()

    def __int__(self):
        return self._trunc()

    def to_model(self):
        return self.value

    def to_copybook(self):
        return str(self)

    def check_numeric(self, num_call, alpha_call):
        try:
            float(self.value)
        except ValueError:
            return alpha_call()
        else:
            return num_call()

class NumberOrStringField(Field):
    default_class = NumberOrChar
    default_value = '?'

    def default(self, instance=None):
        """
        return an instance of the default Type class that contains a default value
        for example a Char instance containing an empty string as a value
        """
        return self.default_class(self.default_value * self.length, self.length, self.order, self.path, self)
