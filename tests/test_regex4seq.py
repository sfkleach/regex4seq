from regex4seq import NONE, Item, TestItem, MatchGroup


def test_item():
    # Arrange
    p1 = Item("abc")

    # Act/Assert
    assert not p1.match([])
    assert p1.match(['abc'])
    assert not p1.match(['abc', 'pqr'])
    assert not p1.match(['abxc'])

def test_NIL():
    # Act/Assert
    assert NONE.match([])
    assert not NONE.match(['abc'])
    assert not NONE.match(['abc', 'pqr'])

def test_concatenate():
    # Arrange
    p1 = Item("abc")
    p2 = p1.concatenate(p1)

    # Act/Assert
    assert not p2.match([])
    assert not p2.match(['abc'])
    assert p2.match(['abc', 'abc'])
    assert not p2.match(['abc', 'abc', 'pqr'])

def test_testitem():
    # Arrange
    p_int = TestItem(lambda x: isinstance(x, int))

    # Act/Assert
    assert p_int.match([5])
    assert not p_int.match(["foo"])
    assert not p_int.match([5, 6])

def test_alternate():
    # Arrange
    p_int = TestItem(lambda x: isinstance(x, int))
    p_one_or_two = p_int.concatenate(p_int).alternate(p_int)

    # Act/Assert
    assert not p_one_or_two.match([])
    assert p_one_or_two.match([5])
    assert p_one_or_two.match([5, 6])
    assert not p_one_or_two.match([5, 6, 7])

def test_repeat():
    # Arrange
    p_int = TestItem(lambda x: isinstance(x, int))
    p_many = p_int.repeat()

    # Act/Assert
    assert p_many.match([])
    assert p_many.match([5])
    assert p_many.match([5, 6])
    assert p_many.match([5, 6, 7])
    assert not p_many.match([5, '6', 7])

def test_matchgroup():
    # Arrange
    p_int = TestItem(lambda x: isinstance(x, int))
    p_many = p_int.repeat()
    p_group = MatchGroup("foo", p_many).concatenate(Item("bar"))

    # Act
    ns = p_group.match([1, 2, 3, "bar"], namespace=True)

    # Assert
    assert ns.foo == [1, 2, 3]
