
"""
Borrowed extensively from django's forms for the setup and base
functionality of the 'Record' class. Django's forms do a nice
job of conveniently remembering the order of fields which is
a necessity for a properly formatted fixed-width record.
"""

# using django's SortedDict to preserve python 2.6 compatibility
from django.utils.datastructures import SortedDict as OrderedDict

from copy import deepcopy

from djcopybook.fixedwidth import fields

__all__ = ('Record',)

def get_declared_fields(bases, attrs):
    """
    Create a list of fixedwidth field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases').
    """
    fw_fields = [(field_name, obj) for field_name, obj in attrs.items() if isinstance(obj, fields.FixedWidthField)]
    fw_fields.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Record, add that Record's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    for base in bases[::-1]:
        if hasattr(base, 'base_fields'):
            fw_fields = base.base_fields.items() + fw_fields
    return OrderedDict(fw_fields)

class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = get_declared_fields(bases, attrs)
        new_class = super(DeclarativeFieldsMetaclass,
                     cls).__new__(cls, name, bases, attrs)

        # useful to let each FixedWidthField field know its attribute name
        for field_name, field in new_class.base_fields.items():
            setattr(field, 'attname', field_name)

        return new_class

    def __len__(cls):
        """
        Total length this record will be in a fixed width format.
        """
        return sum(get_field_length(f) for f in cls.base_fields.values())

class BaseRecord(object):

    # This is the main implementation of all the record logic. Note that this
    # class is different than Record. See the comments by the Record class for more
    # information. Any improvements to the fixedwidth API should be made to *this*
    # class, not to the Record class.

    def __init__(self, **kwargs):
        # The base_fields class attribute is the *class-wide* definition of
        # fields. Because a particular *instance* of the class might want to
        # alter self.fields, we create self.fields here by copying base_fields.
        # Instances should always modify self.fields; they should not modify
        # self.base_fields.
        self.fields = deepcopy(self.base_fields)

        # populate the fixedwidth fields from the keyword arguments passed in.
        fields_iter = iter(self.fields.values())
        for field in fields_iter:
            if kwargs:
                try:
                    val = kwargs.pop(field.attname)
                except KeyError:
                    # This is done with an exception rather than the
                    # default argument on pop because we don't want
                    # get_default() to be evaluated, and then not used.
                    val = field.get_default()
            else:
                val = field.get_default()

            setattr(self, field.attname, val)

        if kwargs:
            raise TypeError("'{}' is an invalid keyword argument for this function".format(kwargs.keys()[0]))

    def __len__(self):
        """
        Total length this record will be in a fixed width format.
        """
        return len(self.__class__)

    def __str__(self):
        return self.to_record()

    def get_record_value(self, fieldname):
        """
        Allows you to obtain the fixedwidth value for a particular fieldname
        """
        field_class = self.fields[fieldname]
        return field_class.get_record_value(getattr(self, fieldname))

    def to_record(self):
        """
        Strings together all fields as one combined record value.
        """
        return ''.join(self.get_record_value(fn) for fn in self.fields)

    @classmethod
    def from_record(cls, record):
        """
        Takes an existing fixed width record and breaks it into it's
        python Record object.
        """
        if len(record) != len(cls):
            raise ValueError("Fixed width record length is {} but should be {}.".format(len(record), len(cls)))

        new_record = cls()

        pos = 0
        for attrname, field_class in cls.base_fields.items():
            field_length = get_field_length(field_class)
            field_value = field_class.to_python(record[pos:pos + field_length])
            setattr(new_record, attrname, field_value)

            pos += field_length
        return new_record

class Record(BaseRecord):
    "A collection of FixedWidthFields, plus their associated data."
    # This is a separate class from BaseRecord in order to abstract the way
    # self.fields is specified. This class (Record) is the one that does the
    # fancy metaclass stuff purely for the semantic sugar -- it allows one
    # to define a fixedwidth using declarative syntax.
    # BaseCopybook itself has no way of designating self.fields.
    __metaclass__ = DeclarativeFieldsMetaclass

def get_field_length(f):
    """
    Normally field length is the length attribute of a FixedWidthField
    class. However, on ListField classes the length attribute represents
    how many times the record is repeated, so we need the total.
    """
    if isinstance(f, fields.ListField):
        return f.length * len(f.record_class)
    return f.length