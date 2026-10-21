import pytest
from hookforge import unique_footage as u, runner

def test_distinct_ok():
    assert u.gate([dict(id="A", gens=[dict(id="H", gen_id="a1"), dict(id="B1", gen_id="a2")]),
                   dict(id="B", gens=[dict(id="H", gen_id="b1"), dict(id="B1", gen_id="b2")])])

def test_shared_clip_blocks():
    with pytest.raises(u.SharedFootage):
        u.gate([dict(id="A", gens=[dict(id="B3", gen_id="x")]), dict(id="B", gens=[dict(id="B3", gen_id="x")])])

def test_declared_reuse_blocks():
    with pytest.raises(u.SharedFootage): u.gate([dict(id="B", anchor="A", gens=[])])

def test_lean_runner_banned():
    with pytest.raises(u.SharedFootage): runner.build_calls_lean({"gens": []}, "extra")
    with pytest.raises(u.SharedFootage): runner.assemble_lean("h", {}, {}, "o")
