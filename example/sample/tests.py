
import datetime
from django import test
from django.utils.unittest import TestCase
from djcopybook import models, fields
from sample import models as sample_models
from sample import copybooks

class DictToolsTests(test.TestCase):

    def test_be_able_to_merge_two_dicts_into_single_one(self):
        d1 = { 'first_field': {'second_field': {'third_field': 1, }}}
        d2 = { 'first_field': {'second_field': {'fourth_field':2, }, 'fifth_field':3, }, 'sixth_field':4,}

        self.assertEqual({'first_field':
                            {'second_field':
                                {'fourth_field':2,
                                 'third_field':1, },
                             'fifth_field':3, },
                          'sixth_field':4, },
                         models.DictTools.merge(d1, d2))

    def test_be_able_to_fold_a_list_of_dicts_into_a_single_one(self):
        d1 = {'first_field':{'second_field':{'third_field':1, }}}
        d2 = {'first_field':{'second_field':{'fourth_field':2, }, 'fifth_field':3, }, 'sixth_field':4, }
        d3 = {'second_field':{'third_field':84848}}
        d4 = {'second_field':{'first_field':{'third_field':'XXXX'}}}
        d5 = {'first_field':{'second_field':{'tenth_field':200}}}

        self.assertEqual({'first_field':
                            {'second_field':
                                {'fourth_field':2,
                                 'third_field':1,
                                 'tenth_field':200, },
                             'fifth_field':3, },
                          'sixth_field':4,
                          'second_field':{
                              'third_field':84848,
                              'first_field':{'third_field':'XXXX'},
                          }},
                         models.DictTools.fold((d1, d2, d3, d4, d5)))

    def test_handle_lists(self):
        d1 = { 'first_field': {'second_field': {'third_field': 1, 'x':['1', '2', '3', '4', '5']}}}
        d2 = { 'first_field': {'second_field': {'fourth_field':2, }, 'fifth_field':3, }, 'sixth_field':4, }

        self.assertEqual({'first_field':
                            {'second_field':
                                {'fourth_field':2,
                                 'third_field':1,
                                 'x':['1', '2', '3', '4', '5', ], },
                             'fifth_field':3, },
                          'sixth_field':4, },
                         models.DictTools.merge(d1, d2))

    def test_handle_dicts_nested_in_lists(self):
        d1 = { 'first_field': {'second_field': {'third_field': 1, 'x':[
                {'one':1, 'two':2}, {'one':'I', 'two':'II'}, {'one':'One', 'two':'Two'}, ]}}}
        d2 = { 'first_field': {'second_field': {'fourth_field':2, }, 'fifth_field':3, }, 'sixth_field':4, }

        self.assertEqual({'first_field':
                            {'second_field':
                                {'fourth_field':2,
                                 'third_field':1,
                                 'x':[{'one':1, 'two':2}, {'one':'I', 'two':'II'}, {'one':'One', 'two':'Two'}, ], },
                             'fifth_field':3, },
                          'sixth_field':4, },
                         models.DictTools.merge(d1, d2))

class ModelToDictTests(test.TestCase):
    def test_convert_model_into_dict(self):
        model_dict = models.model_to_dict(sample_models.First(first_field='asdf', second_field="xxx"))
        self.assertEqual(model_dict, {'first_field':'asdf', 'id':None, 'second_field':'xxx'})

    def test_include_inherited_model_fields(self):
        eleventh = sample_models.Eleventh(first_field='123', second_field='456', third_field='789')

        self.assertEqual(models.model_to_dict(eleventh),
                         {'id':None,
                          'first_field':'123',
                          'second_field':'456',
                          'third_field':'789'})

class RedefinedFieldTests(test.TestCase):

    def test_resolve_to_a_nested_copybook(self):
        class Dummy(models.Copybook):
            field = fields.RedefinedField(length=60, order=1, select_func='select_func')

            def select_func(self, record):
                return copybooks.SecondCopybook

        dummy = Dummy.from_record("x" * 20 + "y" * 20 + "z" * 20)
        dummy.to_model = False
        self.assertEqual(type(dummy.field), fields.NestedCopybook)

    def test_call_select_method_to_determine_which_copybook_to_use(self):
        class Dummy(models.Copybook):
            field = fields.RedefinedField(length=60, order=1, select_func='select_copybook_for_field')

            def select_copybook_for_field(self, redefined_record):
                return copybooks.SecondCopybook

        data = "x" * 20 + "y" * 20 + "z" * 20
        dummy = Dummy.from_record(data)
        dummy.to_model = False
        self.assertEqual(type(dummy.field.value), copybooks.SecondCopybook)
        self.assertEqual(dummy.field.value.one, "x" * 20)
        self.assertEqual(dummy.field.value.two, "y" * 20)
        self.assertEqual(dummy.field.value.three, "z" * 20)
        dummy.to_copybook = True
        self.assertEqual(str(dummy.field), data)

    def test_create_dict_according_to_logic_for_redefined_copybook(self):
        class Dummy(models.Copybook):
            x = fields.StringField(length=10, order=2, path="something")
            field = fields.RedefinedField(length=60, order=1, select_func='select_copybook_for_field')

            def select_copybook_for_field(self, redefined_record):
                return copybooks.SecondCopybook

        data = "x" * 20 + "y" * 20 + "z" * 20 + '1' * 10
        dummy = Dummy.from_record(data)
        self.assertEqual({'something':'1111111111',
                         'fourth_field': 'xxxxxxxxxxxxxxxxxxxx',
                          'fifth_field': {'first_field': 'yyyyyyyyyyyyyyyyyyyy',
                                          'second_field': 'zzzzzzzzzzzzzzzzzzzz'}}, dummy.to_dict())

class ListFieldTests(test.TestCase):
    def test_accept_copybook_and_occurances(self):
        fields.ListField(length=2, copybook=copybooks.FirstCopybook)

    def test_allow_values_to_be_set_as_list_and_returned_as_string(self):
        class DummyCopybookOne(models.Copybook):
            string_field = fields.StringField(length=1, order=1)
            int_field = fields.IntegerField(length=3, order=2)

        class DummyCopybookTwo(models.Copybook):
            list_field = fields.ListField(length=5, copybook=DummyCopybookOne)

        one = DummyCopybookOne(to_copybook=True)
        one.string_field = 'X'
        one.int_field = 123
        two = DummyCopybookOne(to_copybook=True)
        two.string_field = 'Y'
        two.int_field = 999
        three = DummyCopybookOne(to_copybook=True)
        three.string_field = 'Z'
        three.int_field = 4

        other = DummyCopybookTwo(to_copybook=True)
        other.list_field = [one, two, three]

        self.assertEqual(other.list_field, 'X123Y999Z004 000 000')

    def test_populate_list_field_given_model(self):
        one = sample_models.First(first_field="asdf", second_field="xxxx")
        two = sample_models.First(first_field="1111", second_field="2222")
        three = sample_models.First(first_field="aaaaa", second_field="hhhhh")

        class NineCopybook(models.Copybook):
            char_one = fields.StringField(length=3, path="first_field", order=1)
            char_two = fields.StringField(length=3, path="second_field", order=2)

        class Dummy(models.Copybook):
            nines = fields.ListField(length=5, copybook=NineCopybook, order=1)

        dummy = Dummy(to_copybook=True)
        dummy.nines = (NineCopybook.from_model(one), NineCopybook.from_model(two), NineCopybook.from_model(three))
        self.assertEqual(dummy.to_record(), "asdxxx111222aaahhh            ")

    def test_populate_list_field_given_dict(self):

        class NineCopybook(models.Copybook):
            char_one = fields.StringField(length=3, path="first_field", order=1)
            char_two = fields.StringField(length=3, path="second_field", order=2)

        class Dummy(models.Copybook):
            nines = fields.ListField(length=5, copybook=NineCopybook, order=1)

        dummy = Dummy(to_copybook=True)
        dummy.nines = [NineCopybook.from_dict(dict(first_field=str(i))) for i in range(5)]
        self.assertEqual(dummy.to_record(), "0     1     2     3     4     ")

    def test_be_able_to_populate_a_list_of_models_from_string(self):
        class Dummy(models.Copybook):
            field = fields.ListField(length=5, copybook=copybooks.SixthCopybook, order=1)

        dummy = Dummy(to_model=True)
        dummy.to_model = False
        dummy.field.strip_self_from_record("112223344455666")
        self.assertEqual(dummy.field.value[0].one, "11")
        self.assertEqual(dummy.field.value[0].two, "222")
        self.assertEqual(dummy.field.value[1].one, "33")
        self.assertEqual(dummy.field.value[1].two, "444")
        self.assertEqual(dummy.field.value[2].one, "55")
        self.assertEqual(dummy.field.value[2].two, "666")

    def test_call_fields_strip_from_record_when_copybook_is_reading_record(self):

        class MockList(fields.List):
            counter = 0
            def strip_self_from_record(self, record):
                self.counter += 1

        class MockListField(fields.ListField):
            default_class = MockList

        class DummyCopybook(models.Copybook):
            field = MockListField(length=5, copybook=copybooks.SixthCopybook, order=1)

        dummy = DummyCopybook(to_model=True)
        dummy.to_model = False
        dummy.populate_from_record("xxzzzaabbb")

        self.assertEqual(dummy.field.counter, 1)

    def test_be_able_to_turn_occuring_record_into_model(self):

        class NineCopybook(models.Copybook):
            char_one = fields.StringField(length=3, path="fourth_field", order=1)

        class Dummy(models.Copybook):
            nines = fields.ListField(length=5, copybook=NineCopybook, path="twelfth_set", order=1)

        copybook = Dummy.from_record("asdxxx111222aaahhh")
        model = copybook.build_model(sample_models.First)
        self.assertEqual(model.twelfth_set.all()[0].fourth_field, 'asd')
        self.assertEqual(model.twelfth_set.all()[1].fourth_field, 'xxx')
        self.assertEqual(model.twelfth_set.all()[2].fourth_field, '111')
        self.assertEqual(model.twelfth_set.all()[3].fourth_field, '222')
        self.assertEqual(model.twelfth_set.all()[4].fourth_field, 'aaa')

    def test_populate_related_models(self):
        model = models.PopulateModel(None).populate_related_models(sample_models.First(first_field='abc', second_field='xyz'),
            'twelfth_set', [
                {'fourth_field':'xxx'},
                {'fourth_field':'yyy'},
                {'fourth_field':'zzz'},
            ]
        )
        self.assertEqual(model.twelfth_set.count(), 3)

class StringCopybookFieldTests(test.TestCase):
    def test_accept_length_argument(self):
        string_field = fields.StringField(length=10)
        self.assertEqual(string_field.length, 10)

    def test_truncate_data_overflow(self):
        class Dummy(models.Copybook):
            string = fields.StringField(length=1)

        dummy = Dummy.from_model(sample_models.First)
        dummy.string = "ABC"
        self.assertEqual(str(dummy.string), "A")

    def test_pad_with_spaces_to_the_right(self):

        class Dummy(models.Copybook):
            string = fields.StringField(length=10)

        dummy = Dummy.from_model(sample_models.First)
        dummy.string = "X"
        self.assertEqual(str(dummy.string), "X         ")

    def test_be_able_to_set_default_value(self):
        class Dummy(models.Copybook):
            string = fields.StringField(length=10, default='xxx')

        dummy = Dummy.from_model(sample_models.First)
        self.assertEqual(str(dummy.string), "xxx       ")

class SignedIntegerCopybookFieldTests(test.TestCase):

    def setUp(self):
        class Dummy(models.Copybook):
            field = fields.SignedIntegerField(length=10)
        self.copybook_class = Dummy

    def test_add_plus_sign_to_positive_number(self):
        dummy = self.copybook_class(to_copybook=True)
        dummy.field = 123
        self.assertEqual("+000000123", str(dummy.field))

    def test_add_minus_sign_to_negative_number(self):
        dummy = self.copybook_class(to_copybook=True)
        dummy.field = -123
        self.assertEqual("-000000123", str(dummy.field))

    def test_stay_within_size_when_larger_negative_number_is_given(self):
        dummy = self.copybook_class(to_copybook=True)
        dummy.field = -123456789
        self.assertEqual("-123456789", str(dummy.field))

    def test_add_sign_to_zero(self):
        dummy = self.copybook_class(to_copybook=True)
        dummy.field = 0
        self.assertEqual("+000000000", str(dummy.field))

    def test_limit_string_size(self):
        dummy = self.copybook_class(to_copybook=True)
        dummy.field = 99999999999
        self.assertEqual("+999999999", str(dummy.field))

class SignedDecimalCopybookFieldTests(TestCase):

    def setUp(self):
        class SignedDecimalDummy(models.Copybook):
            field = fields.SignedDecimalField(length=9)
        self.copybook = SignedDecimalDummy(to_copybook=True)
        self.copybook.field = float('99999.99')

    def test_return_float_as_string_with_decimal(self):
        self.assertEqual("+99999.99", str(self.copybook.field))

    def test_add_minus_sign_if_negative(self):
        self.copybook.field = float('-99999.99')
        self.assertEqual("-99999.99", str(self.copybook.field))

    def test_add_sign_to_zero(self):
        self.copybook.field = 0
        self.assertEqual("+00000.00", str(self.copybook.field))

    def test_limit_size_of_field(self):
        self.copybook.field = float('9999999999.99')
        self.assertEqual("+99999.99", str(self.copybook.field))

    def test_pad_with_zeros(self):
        self.copybook.field = float('50.00')
        self.assertEqual("+00050.00", str(self.copybook.field))

    def test_be_empty_string_if_value_is_none(self):
        self.copybook.field = None
        self.assertEqual(' ' * 9, str(self.copybook.field))

    def test_add_cents_for_non_floats(self):
        self.copybook.field = 123
        self.assertEqual('+00123.00', str(self.copybook.field))

    def test_add_decimals_and_pad(self):
        self.copybook.field = 110.10
        self.assertEqual('+00110.10', str(self.copybook.field))

class IntegerCopybookFieldTests(test.TestCase):
    def test_accept_length_argument(self):
        integer_field = fields.IntegerField(length=10)
        self.assertEqual(integer_field.length, 10)

    def test_truncate_overflow(self):
        class Dummy(models.Copybook):
            integer = fields.IntegerField(length=1)

        dummy = Dummy.from_model(sample_models.First)
        dummy.integer = 12345
        self.assertEqual(str(dummy.integer), '1')

    def test_pad_with_zeros_to_the_left(self):
        class Dummy(models.Copybook):
            integer = fields.IntegerField(length=10)

        dummy = Dummy.from_model(sample_models.First)
        dummy.integer = 1
        self.assertEqual(str(dummy.integer), '0000000001')

    def test_be_able_to_set_default_value(self):
        class Dummy(models.Copybook):
            integer = fields.IntegerField(length=10, default=9)

        dummy = Dummy.from_model(sample_models.First)
        self.assertEqual(str(dummy.integer), '0000000009')

    def test_default_to_zero_if_receive_spaces(self):
        class Dummy(models.Copybook):
            integer = fields.IntegerField(length=10)

        dummy = Dummy.from_record('          ')
        self.assertEqual(dummy.integer, 0)


class DateCopybookFieldTests(test.TestCase):

    def test_accept_date_format(self):
        fields.DateField(length=6, format="%m%d%y")

    def test_convert_datestring_into_dateobject(self):
        date = fields.Date(value='101010', length=6, order=1, path='asdf', format="%m%d%y")
        self.assertEqual(datetime.datetime(2010, 10, 10, 0, 0), date.to_model())

    def test_convert_datetime_into_datestring_for_copybook(self):
        date = fields.Date(value=datetime.datetime(2010, 10, 10, 0, 0), length=6, order=1, path='asdf', format="%m%d%y")
        self.assertEqual('101010', date.to_copybook())

    def test_convert_date_into_datestring_for_copybook(self):
        date = fields.Date(value=datetime.date(2010, 10, 10), length=6, order=1, path='asdf', format="%m%d%y")
        self.assertEqual('101010', date.to_copybook())

    def test_return_string_of_spaces_when_no_value_in_to_copybook(self):
        date = fields.Date(value=None, length=6, order=1, path='asdf', format="%m%d%y")
        self.assertEqual('      ', date.to_copybook())

class ModelToCopybookTests(test.TestCase):
    def setUp(self):
        self.instance = sample_models.First(first_field="asdf", second_field="xyz")

    def test_force_instance_to_be_created_for_either_copybook_or_model(self):
        self.assertRaises(ValueError, models.Copybook)
        self.assertTrue(models.Copybook(to_copybook=True))
        self.assertTrue(models.Copybook(to_model=True))

class PopulateModelTests(test.TestCase):

    def test_populate_related_models_with_data(self):
        model = models.CascadeModel.populate(sample_models.Twelfth, {
                'fourth_field':'asdf',
                'fifth_field':{'first_field':'xxx999',
                'second_field':'zzz123', }
            },
        )

        self.assertEqual(model.fourth_field, 'asdf')
        self.assertEqual(model.fifth_field.first_field, 'xxx999')
        self.assertEqual(model.fifth_field.second_field, 'zzz123')

    def test_save_all_related_models(self):
        model = models.CascadeModel.populate(sample_models.Twelfth, {
            'fourth_field':'asdf',
            'fifth_field': {'first_field':'xxx999', 'second_field':'zzz123'},
            }
        )

        models.CascadeModel.save(model)

        self.assertEqual(model.fifth_field.pk, 1)
        self.assertEqual(model.pk, 1)

    def test_populate_indefinately_deeply_nested_models_with_data(self):
        model = models.CascadeModel.populate(sample_models.Sixth,
            {'fifth':{
                'fourth':{
                    'third':{
                        'second':{
                            'third_field':'asdf'
                        }
                    }
                }
            }},
        )

        self.assertEqual(model.fifth.fourth.third.second.third_field, 'asdf')

    def test_save_indefinately_deeplly_nested_model_instances(self):
        model = models.CascadeModel.populate(sample_models.Sixth,
            {'fifth':{
                'fourth':{
                    'third':{
                        'second':{
                            'third_field':'asdf'
                        }
                    }
                }
            }},
        )

        models.CascadeModel.save(model)

        self.assertEqual(model.fifth.fourth.third.second.pk, 1)
        self.assertEqual(model.fifth.fourth.third.pk, 1)
        self.assertEqual(model.fifth.fourth.pk, 1)
        self.assertEqual(model.fifth.pk, 1)
        self.assertEqual(model.pk, 1)

class CopybookTests(test.TestCase):

    def setUp(self):
        self.copybook = copybooks.TestCopybook.from_model(sample_models.First())
        self.copybook.first_field = "X"
        self.copybook.second_field = 1
        self.copybook.third_field = "V"
        self.copybook.fourth_field = 3
        self.copybook.fifth_field = "D"

    def test_convert_copybook_into_dict(self):
        copybook = copybooks.SecondCopybook(to_copybook=True)
        copybook.one = "1"
        copybook.two = "2"
        copybook.three = "3"

        self.assertEqual(copybook.to_dict(), {
            'fourth_field':'1',
            'fifth_field': {
                'first_field':'2',
                'second_field':'3',
            },
        })

    def test_be_able_to_get_fields_back_in_order(self):
        self.copybook.to_model = False
        self.copybook.to_copybook = False
        copybook_fields = [self.copybook.fifth_field, self.copybook.fourth_field,
                  self.copybook.third_field, self.copybook.second_field, self.copybook.first_field]

        self.assertEqual(self.copybook.get_fields(), copybook_fields)

    def test_turn_all_fields_into_single_string(self):
        self.assertEqual(self.copybook.to_record(), "D         0003V  01X ")

    def test_turn_a_single_string_record_into_a_copybook_object(self):
        new_copybook = copybooks.TestCopybook.from_record("D         0003V  01X ")

        self.assertEqual(new_copybook.first_field, "X ")
        self.assertEqual(new_copybook.second_field, 1)
        self.assertEqual(new_copybook.third_field, "V  ")
        self.assertEqual(new_copybook.fourth_field, 3)
        self.assertEqual(new_copybook.fifth_field, "D         ")

    def test_populate_copybook_given_a_model(self):
        model = sample_models.First(first_field="asdf", second_field="xyz")
        self.assertEqual(model.first_field, "asdf")
        self.assertEqual(model.second_field, "xyz")

        new_copybook = copybooks.FirstCopybook.from_model(model)
        new_copybook.to_model = False
        new_copybook.to_copybook = False
        self.assertEqual(new_copybook.first_name.value, "asdf")
        self.assertEqual(new_copybook.last_name.value, "xyz")

    def test_allow_multiple_models_to_be_passed(self):
        first = sample_models.First(first_field="asdf", second_field="xyz")
        twelfth = sample_models.Twelfth(fourth_field="XX", fifth_field=first)

        copybook = copybooks.ThirdCopybook.from_model_list((first, twelfth))
        copybook.to_model = False
        copybook.to_copybook = False
        self.assertEqual(copybook.one.value, "asdf")
        self.assertEqual(copybook.two.value, "xyz")
        self.assertEqual(copybook.three.value, "XX")

    def test_allow_multiple_models_to_be_passed_in_dict(self):
        first_one = sample_models.First(first_field="asdf", second_field="xyz")
        first_two = sample_models.First(first_field="1234", second_field="789")

        copybook = copybooks.FourthCopybook.from_model_dict({'one': first_one, 'two': first_two})
        copybook.to_model = False
        copybook.to_copybook = False
        self.assertEqual(copybook.one.value, "asdf")
        self.assertEqual(copybook.two.value, "1234")

    def test_return_a_model_instance_given_a_string(self):
        copybook = copybooks.FifthCopybook.from_record("XXXXXXXXXXAAAAAAAAAA")
        model = copybook.build_model(sample_models.First)
        self.assertEqual(model.first_field, "XXXXXXXXXX")
        self.assertEqual(model.second_field, "AAAAAAAAAA")
        self.assertEqual(model.pk, None)

    def test_return_a_saved_model_instance_given_a_string_and_save_flag(self):
        copybook = copybooks.FifthCopybook.from_record("XXXXXXXXXXAAAAAAAAAA")
        model = copybook.build_model(sample_models.First, save=True)
        self.assertEqual(model.first_field, "XXXXXXXXXX")
        self.assertEqual(model.second_field, "AAAAAAAAAA")
        self.assertEqual(model.pk, 1)

    def test_populate_multiple_models_if_requested(self):
        copybook = copybooks.ThirdCopybook.from_record("111111111111111111112222222222222222222233333333333333333333")
        first = copybook.build_model(sample_models.First)
        seventh = copybook.build_model(sample_models.Seventh)

        self.assertEqual(first.first_field, '11111111111111111111')
        self.assertEqual(first.second_field, '22222222222222222222')
        self.assertEqual(seventh.fourth_field, '33333333333333333333')

class DecimalFieldTests(test.TestCase):

    def test_return_positive_decimal_from_string(self):
        number = fields.Decimal(value="+0001544.00", length=11, order=1, path=None)
        self.assertEqual(number.to_model(), 1544.0)

    def test_return_negative_decimal_from_string(self):
        number = fields.Decimal(value="-9001544.87", length=11, order=1, path=None)
        self.assertEqual(number.to_model(), -9001544.87)

    def test_return_positive_integer_from_string(self):
        number = fields.Decimal(value="+9001544", length=11, order=1, path=None)
        self.assertEqual(number.to_model(), 9001544)

    def test_return_negative_integer_from_string(self):
        number = fields.Decimal(value="-9001544", length=11, order=1, path=None)
        self.assertEqual(number.to_model(), -9001544)

class NumberOrStringFieldTests(test.TestCase):

    def setUp(self):
        class Dummy(models.Copybook):
            field = fields.NumberOrStringField(length=10, order=1)
        self.copybook_class = Dummy

    def test_default_to_question_marks(self):
        dummy = self.copybook_class(to_copybook=True)
        self.assertEqual('??????????', dummy.field)
