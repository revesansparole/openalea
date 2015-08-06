from nose.tools import assert_raises

from openalea.core.pkgdict import PackageDict, protect, is_protected


def test_is_protected():
    p = protect("toto")
    assert is_protected(p)
    assert_raises(TypeError, lambda: protect(0))
    assert not is_protected(0)


def test_pkg_dict_init():
    d = PackageDict()

    assert len(d) == 0


def test_pkg_dict_get_item():
    d = PackageDict()

    d['a'] = 0
    d[protect('b')] = 1

    assert d['a'] == 0
    assert d['A'] == 0
    assert d['b'] == 1
    assert d['B'] == 1
    assert d[protect('b')] == 1
    assert d[protect('B')] == 1

    assert_raises(KeyError, lambda: d['c'])


def test_pkg_dict_set_item():
    d = PackageDict()

    d['a'] = 0
    assert_raises(KeyError, lambda: d.__setitem__(1, 0))


def test_pkg_dict_contains():
    d = PackageDict()

    d['a'] = 0
    d[protect('b')] = 1

    assert 'a' in d
    assert 'A' in d
    assert 0 not in d
    assert 'b' in d
    assert 'B' in d
    assert protect('b') in d


def test_pkg_dict_delitem():
    d = PackageDict()

    d['a'] = 0
    d[protect('b')] = 1

    del d['a']
    assert 'a' not in d
    assert 'A' not in d
    assert 'b' in d

    d['a'] = 0
    del d['A']
    assert 'a' not in d
    assert 'A' not in d
    assert 'b' in d

    for k in ['c', 'C', protect('c'), protect('C')]:
        d[k] = 1
        del d[k]
        assert 'c' not in d
        assert 'C' not in d
        assert protect('c') not in d


def test_pkg_dict_get():
    d = PackageDict()

    d['a'] = 0
    d[protect('b')] = 1

    assert d.get('a') == 0
    assert d.get('A') == 0
    assert d.get('c') is None
    assert d.get('c', 1) == 1
    assert_raises(TypeError, lambda: d.get(0))

    assert d.get('b') == 1
    assert d.get('B') == 1
    assert d.get(protect('b')) == 1


def test_pkg_public_values():
    d = PackageDict()

    d['a'] = 0
    d[protect('b')] = 1

    assert tuple(d.public_values()) == (0,)


def test_pkg_nb_public_values():
    d = PackageDict()

    d['a'] = 0
    d[protect('b')] = 1

    assert d.nb_public_values() == 1



