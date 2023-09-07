from regex4seq import NONE, ANY, Item, IfItem, MatchGroup, OneOf, Items, FAIL, MANY, IfNext, IfItems

def test_matches_option_namespace():
    # Arrange
    p1 = Item( "abc" ).var( "foo" )

    # Act
    ns0 = p1.matches( [ 'abc' ] )
    ns1 = p1.matches( [ 'abc' ], namespace=False )
    
    # Assert
    assert ns0.foo == ['abc']
    assert ns1 is True

def test_matches_two_groups():
    # Arrange
    pattern = Item( "abc" ).var( "lhs" ).then( Item( "def" ).var( "rhs" ) )

    # Act - this exercises CaptureTrail.add
    ns = pattern.matches( [ 'abc', 'def' ] )

    # Assert
    assert ns.lhs == ['abc']
    assert ns.rhs == ['def']

def test_matches_history():
    # Arrange
    pattern = ANY.var( "it" ).repeat()

    # Act - this exercises CaptureTrail.add
    ns = pattern.matches( [ 'abc', 'def' ], history=dict(it='all') )

    # Assert
    assert len(ns.all) == 2
    assert [*ns.all] == [['abc'], ['def']]

def test_findAllMatches():
    # Arrange
    pattern = ANY.var( "it" )

    # Act - this exercises CaptureTrail.add
    matches = tuple( map(lambda ns: ns.it, pattern.findAllMatches( [ 'abc', 'def', 'ghi' ], start=False, end=False ) ) )

    # Assert
    assert len(matches) == 3
    for m in matches:
        assert m in [ ['abc'], ['def'], ['ghi'] ]
    for m in range(0, len(matches)):
        assert matches[m % 3] != matches[(m+1) % 3]

def test_matches_matchgroup_with_extraction():
    # Arrange
    pattern = Item( "abc" ).var( "foo", extract=lambda s, lo, hi: s[lo] )

    # Act/Assert
    assert pattern.matches( [ 'abc' ] ).foo == 'abc'

def test_item():
    # Arrange
    p1 = Item( "abc" )

    # Act/Assert
    assert not p1.matches( [ ] )
    assert p1.matches( [ 'abc' ] )
    assert not p1.matches( [ 'abc', 'pqr' ] )
    assert not p1.matches( [ 'abxc' ] )


def test_NONE():
    # Act/Assert
    assert NONE.matches( [ ] )
    assert not NONE.matches( [ 'abc' ] )
    assert not NONE.matches( [ 'abc', 'pqr' ] )


def test_concatenate():
    # Arrange
    p1 = Item( "abc" )
    p2 = p1.then( p1 )

    # Act/Assert
    assert not p2.matches( [ ] )
    assert not p2.matches( [ 'abc' ] )
    assert p2.matches( [ 'abc', 'abc' ] )
    assert not p2.matches( [ 'abc', 'abc', 'pqr' ] )


def test_testitem():
    # Arrange
    p_int = IfItem( lambda x: isinstance( x, int ) )

    # Act/Assert
    assert p_int.matches( [ 5 ] )
    assert not p_int.matches( [ "foo" ] )
    assert not p_int.matches( [ 5, 6 ] )


def test_alternate():
    # Arrange
    p_int = IfItem( lambda x: isinstance( x, int ) )
    p_one_or_two = p_int.then( p_int ).otherwise( p_int )

    # Act/Assert
    assert not p_one_or_two.matches( [ ] )
    assert p_one_or_two.matches( [ 5 ] )
    assert p_one_or_two.matches( [ 5, 6 ] )
    assert not p_one_or_two.matches( [ 5, 6, 7 ] )


def test_repeat():
    # Arrange
    p_int = IfItem( lambda x: isinstance( x, int ) )
    p_many = p_int.repeat()

    # Act/Assert
    assert p_many.matches( [ ] )
    assert p_many.matches( [ 5 ] )
    assert p_many.matches( [ 5, 6 ] )
    assert p_many.matches( [ 5, 6, 7 ] )
    assert not p_many.matches( [ 5, '6', 7 ] )


def test_matchgroup():
    # Arrange
    p_int = IfItem( lambda x: isinstance( x, int ) )
    p_many = p_int.repeat()
    p_group = MatchGroup( "foo", p_many ).then( Item( "bar" ) )

    # Act
    ns = p_group.matches( [ 1, 2, 3, "bar" ] )

    # Assert
    assert ns.foo == [ 1, 2, 3 ]

def test_then_one_of():
    # Arrange
    p_one_of = OneOf( "foo", "bar", "baz")
    
    # Act/Assert
    assert not p_one_of.matches( [] )
    assert p_one_of.matches( [ "foo" ] )
    assert p_one_of.matches( [ "bar" ] )
    assert p_one_of.matches( [ "baz" ] )
    assert not p_one_of.matches( [ "bar", "baz" ] )

def test_FAIL():
    # Act/Assert
    assert not FAIL.matches( [] )    
    assert not FAIL.matches( [''] )    
    assert not FAIL.matches( ['', ''] )

def test_MANY():
    # Act/Assert
    assert MANY.matches( [] )    
    assert MANY.matches( [''] )    
    assert MANY.matches( ['', 1, False] )

def test_MANY_is_greedy():
    # Arrange
    p = MANY.var("lhs").then( Item( 'a' ) ).then( MANY )

    # Act/Assert
    assert not p.matches( [] )
    assert [*p.matches( ['a'] ).lhs] == []
    assert [*p.matches( ['a', 'a'] ).lhs] == ['a']
    assert [*p.matches( ['a', 'a', 'a'] ).lhs] == ['a', 'a']

def test_optional():
    # Arrange
    p = Item('a').optional()

    # Act/Assert
    assert p.matches( [] )
    assert p.matches( ['a'] )
    assert not p.matches( ['b'] )
    assert not p.matches( ['a', 'a'] )

def test_IfNext():
    # Arrange
    p = IfNext( lambda x, y: x[0] == y[0] and x != y )

    # Act/Assert
    assert not p.matches( [], start=False, end=False )
    assert not p.matches( ['a'], start=False, end=False )
    assert not p.matches( ['a', 'b'], start=False, end=False )
    assert p.matches( ['a', 'ac'], start=False, end=False )
    assert not p.matches( ['a', 'x', 'ac'], start=False, end=False )
    assert not p.matches( ['a', 'a'], start=False, end=False )

def test_IfItems():
    # Arrange
    p = IfItems( lambda x: isinstance(x, int), lambda x: isinstance(x, str) )

    # Act/Assert
    assert not p.matches( [] )
    assert not p.matches( ['a'] )
    assert not p.matches( ['a', 'b'] )
    assert p.matches( [22, 'ac'] )
    assert not p.matches( [1, False] )
