from regex4seq import NONE, Item, IfItem, MatchGroup


def test_item():
    # Arrange
    p1 = Item("abc")

    # Act/Assert
    assert not p1.matches([])
    assert p1.matches(['abc'])
    assert not p1.matches(['abc', 'pqr'])
    assert not p1.matches(['abxc'])

def test_NIL():
    # Act/Assert
    assert NONE.matches([])
    assert not NONE.matches(['abc'])
    assert not NONE.matches(['abc', 'pqr'])

def test_concatenate():
    # Arrange
    p1 = Item("abc")
    p2 = p1.then(p1)

    # Act/Assert
    assert not p2.matches([])
    assert not p2.matches(['abc'])
    assert p2.matches(['abc', 'abc'])
    assert not p2.matches(['abc', 'abc', 'pqr'])

def test_testitem():
    # Arrange
    p_int = IfItem(lambda x: isinstance(x, int))

    # Act/Assert
    assert p_int.matches([5])
    assert not p_int.matches(["foo"])
    assert not p_int.matches([5, 6])

def test_alternate():
    # Arrange
    p_int = IfItem(lambda x: isinstance(x, int))
    p_one_or_two = p_int.then(p_int).otherwise(p_int)

    # Act/Assert
    assert not p_one_or_two.matches([])
    assert p_one_or_two.matches([5])
    assert p_one_or_two.matches([5, 6])
    assert not p_one_or_two.matches([5, 6, 7])

def test_repeat():
    # Arrange
    p_int = IfItem(lambda x: isinstance(x, int))
    p_many = p_int.repeat()

    # Act/Assert
    assert p_many.matches([])
    assert p_many.matches([5])
    assert p_many.matches([5, 6])
    assert p_many.matches([5, 6, 7])
    assert not p_many.matches([5, '6', 7])

def test_matchgroup():
    # Arrange
    p_int = IfItem(lambda x: isinstance(x, int))
    p_many = p_int.repeat()
    p_group = MatchGroup("foo", p_many).then(Item("bar"))

    # Act
    ns = p_group.matches([1, 2, 3, "bar"], namespace=True)

    # Assert
    assert ns.foo == [1, 2, 3]
