
This app allows you to convert objects into fixed width records.

In version 0.1.0 we introduce an entirely new (albeit similar) interface
that breaks all dependency on Django and removes the necessity of
manually setting the order of fields. We call it 'fixedwidth'.

Usage:

  from djcopybook.fixedwidth import Record
  from djcopybook.fixedwidth import fields  

  class Person(Record):
      first_name = fields.StringField(length=20)
      last_name = fields.StringField(length=30)
      siblings = fields.IntegerField(length=2)
      birth_date = fields.DateField(length=10, format="%Y-%m-%d")

  >>> p = Person(first_name="Joe", last_name="Smith", siblings=3, birth_date="1982-09-11")
  >>> p.birth_date
  datetime.date(1982, 9, 11)
  >>> p.to_record()
  'Joe                 Smith                         031982-09-11'

You can also set attributes after a record has been instantiated, give
fields default values, and other fun stuff.

When you have a record instance, the data values will always be their
python value, and when you do a to_record on the Record as a whole or
an individual field it will have the fixedwidth format.

New in version 0.1.2:
  Convert records from a fixed width format back into record objects

  USAGE:
    class Person(Record):
        first_name = fields.StringField(length=20)
        last_name = fields.StringField(length=30)
        siblings = fields.IntegerField(length=2)
        birth_date = fields.DateField(length=10, format="%Y-%m-%d")

    >>> fixedwidth_record = 'Joe                 Smith                         031982-09-11'
    >>> person = Person.from_record(fixedwidth_record)
    >>> person.first_name
    'Joe'
    >>> person.last_name
    'Smith'
    >>> person.siblings
    3
    >>> person.birth_date
    datetime.date(1982, 9, 11)

New in version 0.1.1:
  ListField: lets you have one field whose values are made of another
  complete record. Similar to COBOL's OCCURS functionality. Declaring
  length on the ListField tells how many times that record repeats.

  USAGE:
    class PhoneNumber(Record):
        identifier = fields.StringField(length=10, default="Mobile")
        area_code = fields.IntegerField(length=3)
        prefix = fields.IntegerField(length=3)
        line_number = fields.IntegerField(length=4)

    class Person(Record):
        first_name = fields.StringField(length=20)
        last_name = fields.StringField(length=30)
        siblings = fields.IntegerField(length=2)
        birth_date = fields.DateField(length=10, format="%Y-%m-%d")
        phone_numbers = fields.ListField(record=PhoneNumber, length=3)

    >>> phone_one = PhoneNumber(area_code=515, prefix=555, line_number=2222)
    >>> person = Person(first_name="Joe", last_name="Smith", siblings=3,
                   birth_date="1982-09-11", phone_numbers=[phone_one])

    >>> person.to_record()
    'Joe                 Smith                         031982-09-11Mobile    5155552222Mobile    0000000000Mobile    0000000000'


New in version 0.1.6:
  FragmentField: Similar to the ListField, but only occurring one time.
  Useful if you have a common element included in multiple Records.

  USAGE:
    class Phone(Record):
        area_code = fields.IntegerField(length=3)
        prefix = fields.IntegerField(length=3)
        line_number = fields.IntegerField(length=4)

    class Contact(Record):
        name = fields.StringField(length=30)
        phone_number = fields.FragmentField(record=Phone)
        email = fields.StringField(length=30)

    >>> phone = PhoneNumber(area_code=515, prefix=555, line_number=2222)
    >>> contact = Contact(name="Joe", phone_number=phone, email="joe@example.com")
    >>> contact.to_record()
    'Joe                 5155552222joe@example.com               '


    or:

    >>> contact = Contact(name="Joe", email="joe@example.com")
    >>> contact.phone_number.area_code = 515
    >>> contact.phone_number.prefix = 555
    >>> contact.phone_number.line_number = 2222
    >>> contact.to_record()
    'Joe                 5155552222joe@example.com               '


New in version 0.1.7:
You can now populate a record object with a dictionary containing more items
than the record has fields. The record will use the values if it has the
associated fields, but will ignore extra data.

This is useful when populating records from a form's cleaned_data for instance
if the form has more data than that specific record wants.


Notes:
  Because we are using OrderedDict, the new fixedwidth implementation
  will only work on Python 2.7 and above. (you can copy the OrderdDict
  class yourself if you need < 2.7)

  The previous Django model implementation is pending deprecation.
