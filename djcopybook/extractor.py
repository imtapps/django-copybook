import re


class CopybookExtractor(object):

    def build_data_structure_from_copybook(self):
        for field_name in dir(self.copybook):
            if not re.match(r'^__', field_name):
                field = getattr(self.copybook, field_name)
                if hasattr(field, 'order'):
                    self._append_field_value_to_data_structure(field, field_name)
        return self.fields

    def _append_field_value_to_data_structure(self, field, field_name):
        raise NotImplementedError("please implement append field value to data structure")


class ListExtractor(CopybookExtractor):
    def __init__(self, copybook):
        self.fields = []
        self.copybook = copybook

    def _append_field_value_to_data_structure(self, field, field_name):
        if isinstance(field.value, list):
            self.fields.append(field)
        else:
            self.fields.append(field)


class DictExtractor(CopybookExtractor):
    def __init__(self, copybook):
        self.fields = {}
        self.copybook = copybook

    def _append_field_value_to_data_structure(self, field, field_name):
        if isinstance(field.value, list):
            self.fields[field_name] = field.to_json_friendly_dict()
        else:
            self.fields[field_name] = field.to_model()
