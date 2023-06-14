import pytest

from argumento.namespace_dict import NamespaceDict


def test_set_get_simple():
    ns_dict = NamespaceDict()
    ns_dict['item'] = 1
    assert ns_dict['item'] == 1
    assert ns_dict.item == 1


def test_init_from_dict():
    ns_dict = NamespaceDict({'item1': 1,
                             'item2': 2,
                             'item3': {
                                 'subitem31': {'subitem311': 311, 'subitem312': 312},
                                 'subitem32': {'subitem321': 321, 'subitem322': 322}}})
    assert ns_dict['item1'] == 1
    assert ns_dict['item2'] == 2
    assert ns_dict.item1 == 1
    assert ns_dict.item2 == 2

    assert ns_dict['item3']['subitem31']['subitem311'] == 311
    assert ns_dict['item3']['subitem31']['subitem312'] == 312
    assert ns_dict['item3']['subitem32']['subitem321'] == 321
    assert ns_dict['item3']['subitem32']['subitem322'] == 322
    #
    assert ns_dict.item3['subitem31']['subitem311'] == 311
    assert ns_dict.item3['subitem31']['subitem312'] == 312
    assert ns_dict.item3['subitem32']['subitem321'] == 321
    assert ns_dict.item3['subitem32']['subitem322'] == 322
    #
    assert ns_dict.item3.subitem31['subitem311'] == 311
    assert ns_dict.item3.subitem31['subitem312'] == 312
    assert ns_dict.item3.subitem32['subitem321'] == 321
    assert ns_dict.item3.subitem32['subitem322'] == 322
    #
    assert ns_dict.item3.subitem31.subitem311 == 311
    assert ns_dict.item3.subitem31.subitem312 == 312
    assert ns_dict.item3.subitem32.subitem321 == 321
    assert ns_dict.item3.subitem32.subitem322 == 322

def test_set_recursive():
    ns_dict = NamespaceDict()
    ns_dict['item1.subitem1'] = 11
    assert ns_dict.item1.subitem1 == 11
    assert ns_dict['item1.subitem1'] == 11

    ns_dict['item1']['subitem2'] = 12
    assert ns_dict['item1']['subitem2'] == 12
    assert ns_dict['item1.subitem2'] == 12
    assert ns_dict.item1.subitem2 == 12

    with pytest.raises(TypeError):
        ns_dict['item2']['subitem2'] = 22

    ns_dict['item2'] = {'subitem2': 22}
    assert ns_dict['item2']['subitem2'] == 22
    assert ns_dict['item2.subitem2'] == 22
    assert ns_dict.item2.subitem2 == 22

    ns_dict['item3'] = {'subitem31': {'subitem311': 311, 'subitem312': 312},
                        'subitem32': {'subitem321': 321, 'subitem322': 322}}
    assert ns_dict['item3']['subitem31']['subitem311'] == 311
    assert ns_dict['item3']['subitem31']['subitem312'] == 312
    assert ns_dict['item3']['subitem32']['subitem321'] == 321
    assert ns_dict['item3']['subitem32']['subitem322'] == 322
    #
    assert ns_dict.item3['subitem31']['subitem311'] == 311
    assert ns_dict.item3['subitem31']['subitem312'] == 312
    assert ns_dict.item3['subitem32']['subitem321'] == 321
    assert ns_dict.item3['subitem32']['subitem322'] == 322
    #
    assert ns_dict.item3.subitem31['subitem311'] == 311
    assert ns_dict.item3.subitem31['subitem312'] == 312
    assert ns_dict.item3.subitem32['subitem321'] == 321
    assert ns_dict.item3.subitem32['subitem322'] == 322
    #
    assert ns_dict.item3.subitem31.subitem311 == 311
    assert ns_dict.item3.subitem31.subitem312 == 312
    assert ns_dict.item3.subitem32.subitem321 == 321
    assert ns_dict.item3.subitem32.subitem322 == 322