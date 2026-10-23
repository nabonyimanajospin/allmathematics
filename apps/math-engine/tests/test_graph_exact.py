from allmaths_engine.graph_exact import exact_points


def one(lines, cands, params=None):
    return exact_points({"lines": lines, "params": params or {}, "candidates": cands})["points"]


def test_roots_of_a_quadratic_are_exact_radicals():
    pts = one({"1": "x^2-2"}, [{"lines": [1], "x": 2 ** 0.5}, {"lines": [1], "x": -(2 ** 0.5)}])
    assert sorted(p["x_text"] for p in pts) == ["-sqrt(2)", "sqrt(2)"]
    assert all(p["y_text"] == "0" for p in pts)


def test_intersection_of_a_parabola_and_a_line_has_exact_coordinates():
    pts = one({"1": "x^2-4", "2": "x-2"}, [{"lines": [1, 2], "x": -1.0}, {"lines": [1, 2], "x": 2.0}])
    got = sorted((p["x_text"], p["y_text"]) for p in pts)
    assert got == [("-1", "-3"), ("2", "0")]


def test_periodic_roots_are_recognised_as_multiples_of_pi():
    import math

    pts = one({"1": "sin(x)"}, [{"lines": [1], "x": math.pi}, {"lines": [1], "x": -2 * math.pi}])
    assert sorted(p["x_text"] for p in pts) == ["-2*pi", "pi"]


def test_cosine_meets_a_line_exactly_only_when_it_can_be_proved():
    import math

    # cos(x) = 1/2 at pi/3
    pts = one({"1": "cos(x)", "2": "1/2"}, [{"lines": [1, 2], "x": math.pi / 3}])
    assert [p["x_text"] for p in pts] == ["pi/3"]
    assert pts[0]["y_text"] == "1/2"
    # x = 0.7391... (cos x = x) has no closed form, so it stays approximate
    assert one({"1": "cos(x)", "2": "x"}, [{"lines": [1, 2], "x": 0.7390851332151607}]) == []


def test_sliders_are_substituted_as_exact_rationals():
    pts = one({"1": "x-a"}, [{"lines": [1], "x": 1.5}], {"a": "3/2"})
    assert [p["x_text"] for p in pts] == ["3/2"]


def test_a_false_candidate_is_never_made_exact():
    assert one({"1": "x^2-4"}, [{"lines": [1], "x": 2.3}]) == []


def test_bad_or_unknown_input_is_ignored():
    assert one({"1": "__import__('os')"}, [{"lines": [1], "x": 0.0}]) == []
    assert one({"1": "q*x"}, [{"lines": [1], "x": 0.0}]) == []
