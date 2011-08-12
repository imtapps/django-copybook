from djcopybook import models, fields

__all__ = (
    "TestCopybook", "FirstCopybook", "SecondCopybook",
    "ThirdCopybook", "FourthCopybook", "FifthCopybook",
    "SixthCopybook"
)

class TestCopybook(models.Copybook):
    first_field = fields.StringField(length=2, order=5)
    second_field = fields.IntegerField(length=2, order=4)
    third_field = fields.StringField(length=3, order=3)
    fourth_field = fields.IntegerField(length=4, order=2)
    fifth_field = fields.StringField(length=10, order=1)

class FirstCopybook(models.Copybook):
    first_name = fields.StringField(length=40, order=1, path="first_field")
    last_name = fields.StringField(length=50, order=2, path="second_field")

class SecondCopybook(models.Copybook):
    one = fields.StringField(length=20, order=1, path="fourth_field")
    two = fields.StringField(length=20, order=2, path="fifth_field.first_field")
    three = fields.StringField(length=20, order=3, path="fifth_field.second_field")

class ThirdCopybook(models.Copybook):
    one = fields.StringField(length=20, order=1, path="first_field")
    two = fields.StringField(length=20, order=2, path="second_field")
    three = fields.StringField(length=20, order=3, path="fourth_field")

class FourthCopybook(models.Copybook):
    one = fields.StringField(length=20, order=1, path="one.first_field")
    two = fields.StringField(length=20, order=2, path="two.first_field")

class FifthCopybook(models.Copybook):
    one = fields.StringField(length=10, order=1, path="first_field")
    two = fields.StringField(length=10, order=2, path="second_field")

class SixthCopybook(models.Copybook):
    one = fields.StringField(length=2, order=1, path="first_field")
    two = fields.StringField(length=3, order=2, path="second_field")