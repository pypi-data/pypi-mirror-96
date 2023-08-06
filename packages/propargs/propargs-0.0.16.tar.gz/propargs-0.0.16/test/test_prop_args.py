#!/usr/bin/env python3
"""
This is a simple test script. It can be cloned to
create new run scripts, and should be run to test
the system after library changes.
"""
import os
import sys
import pytest
import json

from unittest import mock
from unittest.mock import patch
from propargs import propargs as pa, data_store, env, property_dict, command_line, user
from propargs.constants import *
from propargs.type import try_type_val

DUMMY_PROP_NM = "dummy_prop"
ANSWERS_FOR_INPUT_PROMPTS = [1]


@pytest.fixture
def prop_args():
    """
    A bare-bones propargs object. To use - make `propargs` a test argument.
    """
    return pa.PropArgs.create_props("test_pa", ds_file=None, prop_dict=None, skip_user_questions=True)


@pytest.mark.parametrize('lowval, test_val, hival, expected', [
        (None,  7, None, True),
        (None, -5,   10, True),
        (0,    99, None, True),
        (0,     7,   10, True),
        (0,    77,   10, False),
        (0,    -5,   10, False)
        ])
def test_int_bounds(lowval, test_val, hival, expected, prop_args):
    prop_args.props[DUMMY_PROP_NM] = pa.Prop(lowval=lowval,
                                             hival=hival,
                                             atype=pa.INT)

    assert prop_args._answer_within_bounds(prop_nm=DUMMY_PROP_NM,
                                           typed_answer=test_val) \
           == expected


def test_set_props_from_ds(prop_args):
    with mock.patch('propargs.data_store._open_file_as_json') as mock_open_file_as_json:
        mock_open_file_as_json.return_value = json.loads('{{ "{prop_name}": {{"val": 7}} }}'.format(prop_name=DUMMY_PROP_NM))
        prop_args.ds_file = "some_file"
        data_store.set_props_from_ds(prop_args)
        assert prop_args[DUMMY_PROP_NM] == 7


@pytest.mark.parametrize('environment_variables, ds_file, expected_file_path',
                          [({PROPS_DIR: '/path/to/'}, 'ds_file', '/path/to/ds_file'),
                           (dict(), 'ds_file', os.path.join(os.getcwd(), 'ds_file'))])
def test_path_to_ds_file(environment_variables, ds_file, expected_file_path):

    with mock.patch.dict(os.environ, environment_variables):
        file_path = data_store._path_to_file(ds_file)

    assert file_path == expected_file_path


@mock.patch('propargs.env.ENV_AUTO_LOAD_PROPS', [AutoLoadProp(prop_name="iautoload", default="iamdefault")])
def test_set_props_from_env(prop_args):
    prop_args["prop_also_in_env"] = "imavalue"
    with mock.patch.dict(os.environ,
                         {"prop_also_in_env": "imavalue",
                          "prop_not_yet_loaded": "imanothervalue"}):
        env.set_props_from_env(prop_args)

    assert prop_args["prop_also_in_env"] == "imavalue"
    assert "prop_not_yet_loaded" not in prop_args
    assert prop_args["iautoload"] == "iamdefault"


def test_set_os_in_set_props_from_env(prop_args):
    with mock.patch('platform.system') as mock_platform_system:
        mock_platform_system.return_value = 'Mac'
        env.set_props_from_env(prop_args)

    assert prop_args['OS'] == 'Mac'


def test_props_set_through_prop_dict(prop_args):
    prop_dict = {DUMMY_PROP_NM: {"val": 7} }
    prop_args[DUMMY_PROP_NM] = 100
    property_dict.set_props_from_dict(prop_args, prop_dict)

    assert prop_args[DUMMY_PROP_NM] == 7


def test_type_bool_val():
    assert try_type_val('TRUE', BOOL) is True
    assert try_type_val('yes', BOOL) is True
    assert try_type_val(1, BOOL) is True
    assert try_type_val(1.0, BOOL) is True

    assert try_type_val('false', BOOL) is False
    assert try_type_val('no', BOOL) is False
    assert try_type_val(0, BOOL) is False
    assert try_type_val(0.1, BOOL) is False
    assert try_type_val('abona;a;lnsbaioh', BOOL) is False


def test_type_int_val():
    assert try_type_val('2', INT) == 2


def test_type_flt_val():
    assert try_type_val('2.3', FLT) == 2.3


def test_type_cmplx_val():
    assert try_type_val('3+9j', CMPLX) == 3 + 9j


def test_type_null_val():
    bool_none = try_type_val(None, BOOL)
    float_none = try_type_val(None, FLT)
    int_none = try_type_val(None, INT)
    string_none = try_type_val(None, STR)
    complex_none = try_type_val(None, CMPLX)

    assert isinstance(bool_none, bool)
    assert bool_none is False

    assert isinstance(float_none, float)
    assert float_none == 0.0

    assert isinstance(int_none, int)
    assert int_none == 0

    assert isinstance(string_none, str)
    assert string_none == ''

    assert isinstance(complex_none, complex)
    assert complex_none == 0j


def test_props_set_null_dict(prop_args):
    property_dict.set_props_from_dict(prop_args, None)


def test_prop_set_from_cl(prop_args):
    prop_args.props['existing_prop'] = pa.Prop(atype=pa.INT,
                                               val=-1)

    with patch.object(sys, 'argv', ["file.py", "--irrelevant-switch",
                                    "--props", "existing_prop=7,new_prop=4",
                                    "--other-irrelevant-switch"]):
        command_line.set_props_from_cl(prop_args)

    assert prop_args['existing_prop'] == 7
    assert prop_args['new_prop'] == '4'


def test_user_input(prop_args):
    prop_args.props[DUMMY_PROP_NM] = pa.Prop(atype=pa.INT,
                                             question="Enter Integer: ",
                                             val=-1)

    with patch('builtins.input', side_effect=ANSWERS_FOR_INPUT_PROMPTS):
        user.ask_user_through_cl(prop_args)

    assert prop_args[DUMMY_PROP_NM] == ANSWERS_FOR_INPUT_PROMPTS[0]


def test_get_questions(prop_args):
    prop_args.props['question_prop'] = pa.Prop(question="Enter Integer: ")

    prop_args.props['no_question_prop'] = pa.Prop()

    qs = prop_args.get_questions()

    assert 'question_prop' in qs
    assert 'no_question_prop' not in qs


def test_singleton():
    pa.PropArgs('props1', prop_dict={'i like': {'val': 'turtles'}})

    assert pa.get_prop('i like') == 'turtles'

    pa.PropArgs('props2', prop_dict={'i like': {'val': 'tests that pass'}})

    assert pa.get_prop('i like') == 'tests that pass'


def test_set_prop():
    pa.PropArgs('props1', prop_dict={'i like': {'val': 'turtles'}})

    assert pa.get_prop('i like') == 'turtles'

    pa.set_prop('i like', 'tests that pass')

    assert pa.get_prop('i like') == 'tests that pass'

