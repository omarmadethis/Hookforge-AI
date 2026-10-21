from hookforge import omar_gates_f100 as g

def test_card_timing():
    sh=[dict(gen="H",t0=0,t1=2),dict(gen="B",t0=2,t1=4)]
    assert not g.card_timing(sh,[dict(text="x",t0=2,t1=4)])
    assert g.card_timing(sh,[dict(text="x",t0=2.5,t1=4)])

def test_coherence():
    assert g.card_coherence([dict(text="Vs...",shows="install",why="")])
    assert not g.card_coherence([dict(text="Cheap knockoffs..",shows="dim blurry knockoff projection",why="the shot literally shows a dim blurry knockoff projection")])

def test_hook():
    assert g.hook_gate(dict(format="nope",first_second_action="a",conflict="c"))
    assert g.hook_gate(dict(format="problem-solution",first_second_action="",conflict="c"))
    assert not g.hook_gate(dict(format="problem-solution",first_second_action="yanks door",conflict="knockoff dies",conflict_t_s=0.5))
    assert not g.hook_gate(dict(scroll_stopper=True,why_relevant="the badge lands on the car that nearly hit him",first_second_action="a",conflict="c"))

def test_payoff():
    one=[dict(gen="B3",t0=6,t1=10,role="payoff")]
    assert g.payoff_gate(one)
    ok=[dict(gen="B3",t0=6,t1=7.4,role="payoff"),dict(gen="H",t0=7.4,t1=8.8,role="payoff"),dict(gen="B3",t0=8.8,t1=10.2,role="payoff")]
    assert not g.payoff_gate(ok)
