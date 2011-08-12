"""
This module handles converting Django models into objects that can be easily ported to other formats (ie: copybooks)

NOTE:  there is a lot of code in here that heavily relies on Django's internals - this could be proplematic when
updating to different versions of Django

"""

import re
from django.db.models.fields.related import RelatedField, ForeignKey

class DictTools(object):

    @staticmethod
    def merge(d_1, d_2):
        result = d_1
        for k, v in d_2.items():
            if k in result:
                if type(v) == dict:
                    result[k] = DictTools.merge(result[k], v)
                else:
                    result[k] = v
            else:
                result[k] = v
        return result

    @staticmethod
    def fold(dict_list):
        d_1 = dict_list[0]
        for d_2 in dict_list[1:]:
            DictTools.merge(d_1, d_2)
        return d_1

def model_to_dict(instance):
    "Returns a dictionary containing field names and values for the given django model instance"
    data = {}

    for field in instance._meta.fields:
        if not isinstance(field, RelatedField):
            value = getattr(instance, field.name, None)
            data[field.name] = value

    return data

def turn_off_flags(func):
    "This allows the copybook to get around the normal rules of accessing it's fields"
    def wrapper(self, *args, **kwargs):
        "wrapper func"
        tmp_to_model = self.to_model
        tmp_to_copybook = self.to_copybook
        self.to_model = False
        self.to_copybook = False
        return_value = func(self, *args, **kwargs)
        self.to_model = tmp_to_model
        self.to_copybook = tmp_to_copybook
        return return_value
    return wrapper

class Copybook(object):
    """
    this class will take care of formatting django models into cobol copybook friendly strings
    """
    def __init__(self, to_copybook=False, to_model=False):
        self.to_model = to_model
        self.to_copybook = to_copybook
        self._fields = []

        if not any((self.to_copybook, self.to_model)):
            raise ValueError("must choose!!!")

    def get_record_length(self):
        "get the total length of all fields"
        fields = self.get_fields()
        length = 0
        for field in fields:
            length += field.length
        return length

    def populate_from_record(self, record):
        "populate this copybook's fields with the given record"
        fields = self.get_fields()
        tmp_record = record
        for field in fields:
            tmp_record = field.strip_self_from_record(tmp_record)

    def populate_from_dict(self, model_dict):
        "populate this copybook's fields from a given dictionary"
        fields = self.get_fields()
        for field in fields:
            field.populate_from_dict(model_dict)

    def populate_from_model(self, model):
        "populate this copybook's fields from a given model - by first converting the model to a dictionary"
        self.populate_from_dict(model_to_dict(model))

    def populate_from_model_list(self, instance_list):
        "populate this copybook's fields from a given list of models - by calling populate_from_model for each model"
        for model in instance_list:
            self.populate_from_model(model)

    def populate_from_model_dict(self, instance_dict):
        """
        populate this copybook's fields from a passed in dictionary of models by converting the dictionary of models
        into a single diconary by converting each model into a diconary and replacing the model instance with a
        dictionary.

        tmp_dict is used so the original instance_dict is left unchanged
        """
        tmp_dict = {}
        for key in instance_dict:
            tmp_dict[key] = model_to_dict(instance_dict[key])
        self.populate_from_dict(tmp_dict)

    def to_record(self):
        "convert this copybook instance into a single record string"
        fields = self.get_fields()
        record = []
        for field in fields:
            record.append(field.to_copybook())
        return ''.join(record)

    def get_fields(self):
        "return the list of fields in this coypbook"
        if not self._fields:
            self._fields = self._build_field_list()
        return self._fields

    def to_dict(self):
        "returns a dictionary for each field with correct paths in the dictionary for each field"
        def other(path, last_value):
            nodes = path.split('.')
            value = nodes.pop(0)
            if value:
                return {value: other('.'.join(nodes), last_value)}
            else:
                return last_value

        def build_field_paths(copybook):
            field_paths = []
            for field in copybook.get_fields():
                if isinstance(field.value, list):
                    values = []
                    for value in field.value:
                        values.append(build_field_paths(value)[0])
                    field_paths.append(other(field.path, values))
                elif isinstance(field.value, Copybook):
                    field_paths += build_field_paths(field.value)
                else:
                    field_paths.append(other(field.path, field.value))
            return field_paths

        paths = build_field_paths(self)
        return DictTools.fold(paths)

    def build_model(self, model_class, save=False):
        "return a new instance of a model populated with data from this Copybook instance"
        model = CascadeModel.populate(model_class, self)
        if save:
            CascadeModel.save(model)
        return model

    @turn_off_flags
    def _build_field_list(self):
        "build a list of fields in this copybook"
        fields = []
        for field_name in dir(self):
            if not re.match(r'^__', field_name):
                field = getattr(self, field_name)
                if hasattr(field, 'order'):
                    fields.append(field)
        return sorted(fields, key=lambda field: field.order)

    @classmethod
    def from_dict(cls, dictionary):
        """
        this will create an instance of a copybook object from a given dictionary
        """
        copybook = cls(to_copybook=True)
        copybook.populate_from_dict(dictionary)
        return copybook

    @classmethod
    def from_model(cls, instance):
        """
        this will populate a copybook object with data from a given model
        """
        copybook = cls(to_copybook=True)
        copybook.populate_from_model(instance)
        return copybook

    @classmethod
    def from_model_list(cls, instance_list):
        """
        this will populate a copybook object with data from the passed in list of models
        this will work like 'first come first serve', so if the same field is defined in multiple
        models, the model first in the list will win and set the value
        """
        copybook = cls(to_copybook=True)
        copybook.populate_from_model_list(instance_list)
        return copybook

    @classmethod
    def from_model_dict(cls, instance_dict):
        """
        this will populate a copybook object with data from a dictionary of models
        if this is used, then the field mappings on the coypbook's fields should specify which model
        to retrieve the fields from by adding a node to the beginning of the mapping that matches
        the model's key passed into this function
        """
        copybook = cls(to_copybook=True)
        copybook.populate_from_model_dict(instance_dict)
        return copybook

    @classmethod
    def from_record(cls, record):
        """
        this will populate a copybook object with data from a passed in, single line record string
        """
        copybook = cls(to_model=True)
        copybook.populate_from_record(record)
        return copybook

class PopulateModel(object):

    def __init__(self, copybook):
        self.copybook = copybook

    def __call__(self, model):
        model_fields = dict([(field.name, field) for field in model._meta.fields])
        data = self.copybook.to_dict() if isinstance(self.copybook, Copybook) else self.copybook
        for name, value in data.items():
            self.set_field(model, model_fields, name, value)
        return model

    def populate_related_models(self, model, name, value):
        "in order for related models to work, the current model and each related model must be saved"
        model.save()
        related_manager = getattr(model, name)
        for item in value:
            new_model = CascadeModel.populate(related_manager.create(), item)
            new_model.save()
        return model

    def set_field(self, model, model_fields, name, value):
        if name in model_fields:
            field = model_fields[name]
            if isinstance(field, ForeignKey):
                try:
                    CascadeModel.populate(getattr(model, name), value)
                except field.rel.to.DoesNotExist:
                    CascadeModel.populate(field.rel.to, value)
            else:
                setattr(model, name, value)
        elif name in dir(model) and type(value) == list:
            self.populate_related_models(model, name, value)

class CascadeModel(object):
    """
    This class can be used to traverse a django model's relationships and do 'something' to an entire django
    model structure and all related models
    """

    @staticmethod
    def save(model):
        "save a model and all related models"
        return CascadeModel(lambda model_inst: model_inst.save())._cascade(model)

    @staticmethod
    def populate(main_model, copybook):
        "populate a model and related models given a copybook"
        main_model = main_model if type(main_model).__class__.__name__ != 'type' else main_model()
        return CascadeModel(PopulateModel(copybook))._cascade(main_model)

    def __init__(self, model_operation=lambda model:None, field_operation=lambda model, field_name:None):
        "operation is something that needs to be done to a model"
        self.model_operation = model_operation
        self.field_operation = field_operation

    def _get_foreign_keys(self, model, model_fields):
        "return a list of foreign keys for a given model"
        foreign_keys = []
        for name, field in model_fields:
            if isinstance(field, ForeignKey):
                try:
                    foreign_keys.append((name, getattr(model, name)))
                except field.rel.to.DoesNotExist:
                    foreign_keys.append((name, field.rel.to()))
            else:
                self.field_operation(model, name)
        return foreign_keys

    def _cascade_nested_foreign_keys(self, foreign_keys):
        "cascade all foreign keys and follow their relationships as well"
        for _, model in foreign_keys:
            self._cascade(model)

    def _operate_on_related_models(self, model, related_models):
        "perofrm the given operation on each foreign key object"
        for name, foreign_key in related_models:
            self.model_operation(foreign_key)
            setattr(model, name, foreign_key) #this is a hack, needed by Django for some dumb reason

    def _cascade(self, model):
        "this will perform a given operation on a model as well as all related models"
        instance_fields = [(field.name, field) for field in model._meta.fields]

        foreign_keys = self._get_foreign_keys(model, instance_fields)
        if foreign_keys:
            self._cascade_nested_foreign_keys(foreign_keys)
            self._operate_on_related_models(model, foreign_keys)

        self.model_operation(model)
        return model
