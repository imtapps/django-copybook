from django import db

__all__ = ('First', 'Second', 'Third', 'Fourth', 'Fifth',
           'Sixth', 'Seventh', 'Eights', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth')

class First(db.models.Model):
    first_field = db.models.CharField(max_length=10)
    second_field = db.models.CharField(max_length=10)

class Second(db.models.Model):
    third_field = db.models.CharField(max_length=10)

class Third(db.models.Model):
    second = db.models.ForeignKey(Second)

class Fourth(db.models.Model):
    third = db.models.ForeignKey(Third)

class Fifth(db.models.Model):
    fourth = db.models.ForeignKey(Fourth)

class Sixth(db.models.Model):
    fifth = db.models.ForeignKey(Fifth)

class Seventh(db.models.Model):
    fourth_field = db.models.CharField(max_length=10)

class Eights(db.models.Model):
    sevenths = db.models.ManyToManyField(Seventh)

class Ninth(db.models.Model):
    first = db.models.ForeignKey(First)

class Tenth(db.models.Model):
    ninths = db.models.ManyToManyField(Ninth)

class Eleventh(First):
    third_field = db.models.CharField(max_length=10)

class Twelfth(db.models.Model):
    fourth_field = db.models.CharField(max_length=10)
    fifth_field = db.models.ForeignKey(First)
