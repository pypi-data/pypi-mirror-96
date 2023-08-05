import modelx as mx
import pytest


@pytest.fixture(scope="module")
def testspaces():
    parent = mx.new_space("Parent", formula=lambda i: None)
    child = parent.new_space("Child")
    item = parent[1]

    return parent, child, item


def test_spaces(testspaces):
    parent, child, item = testspaces
    assert list(parent.spaces.keys()) == ["Child"]
    assert list(parent.spaces.values()) == [child]


def test_named_spaces(testspaces):
    parent, child, item = testspaces
    assert list(parent.named_spaces.keys()) == ["Child"]
    assert list(parent.named_spaces.values()) == [child]


def test_all_spaces(testspaces):
    parent, child, item = testspaces
    assert len(parent._all_spaces) == 2
    assert child in parent._all_spaces.values()
    assert item in parent._all_spaces.values()


