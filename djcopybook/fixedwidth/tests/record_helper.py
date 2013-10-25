from djcopybook import fixedwidth
from djcopybook.fixedwidth import fields


class RecordOne(fixedwidth.Record):
    field_one = fields.StringField(length=5, default="AA")
    field_two = fields.IntegerField(length=7)


class RecordTwo(RecordOne):
    auto_truncate = True

    field_three = fields.DecimalField(length=9)
    field_four = fields.DateField(length=2)


class RecordThree(fixedwidth.Record):
    frag = fields.FragmentField(record=RecordOne)
    other_field = fields.StringField(length=3, default="BBB")


class RecordFour(fixedwidth.Record):
    frag = fields.FragmentWithNewlineField(record=RecordOne)
    other_field = fields.StringField(length=3, default="EEE")


class RecordFive(fixedwidth.Record):
    garf = fields.FragmentWithNewlineField(RecordFour)
    threeve = fields.ListField(record=RecordThree, length=2)
