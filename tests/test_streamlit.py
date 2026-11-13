"""Headless test of the Streamlit app.  Run:  python tests/test_streamlit.py"""
import os, sys, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ["VLAB_OBS_PATH"] = os.path.join(tempfile.gettempdir(), "vlab_obs_test.json")
if os.path.exists(os.environ["VLAB_OBS_PATH"]):
    os.remove(os.environ["VLAB_OBS_PATH"])
from streamlit.testing.v1 import AppTest
from lab import ml_core as core

PAGES = ["📘 Aim & Theory", "🧭 Procedure", "🗂️ Dataset Explorer", "🧪 Run Experiment", "📒 Observations"]


def fresh():
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    return at


# every page renders
for pg in PAGES:
    at = fresh()
    at.sidebar.radio[0].set_value(pg).run()
    assert not at.exception, (pg, at.exception)
    print(f"[PASS] page renders: {pg}")

# dataset page for each dataset
for ds in core.DATASETS:
    at = fresh(); at.sidebar.radio[0].set_value(PAGES[2]).run()
    at.selectbox(key="ds_page").set_value(ds).run()
    assert not at.exception, (ds, at.exception)
print("[PASS] dataset explorer: all datasets")

# run experiment for every dataset x model
for ds in core.DATASETS:
    for mk in core.MODELS:
        at = fresh(); at.sidebar.radio[0].set_value(PAGES[3]).run()
        at.selectbox(key="exp_dataset").set_value(ds)
        at.selectbox(key="exp_model").set_value(mk)
        at.button[0].click().run()
        assert not at.exception, (ds, mk, at.exception)
        assert not at.error, (ds, mk, [e.value for e in at.error])
        assert "res" in at.session_state
        r = at.session_state["res"]
        assert 0.5 < r["metrics"]["accuracy"] <= 1
    print(f"[PASS] run experiment: {ds} x {len(core.MODELS)} models")
# observations: runs were logged, page shows them, clear works
rows = core.obs_load()
assert len(rows) == len(core.DATASETS) * len(core.MODELS), len(rows)
at = fresh(); at.sidebar.radio[0].set_value(PAGES[4]).run()
assert not at.exception and not at.info, at.exception
print(f"[PASS] observations page shows {len(rows)} logged runs")
core.obs_clear()
at = fresh(); at.sidebar.radio[0].set_value(PAGES[4]).run()
assert not at.exception and len(at.info) == 1
print("[PASS] observations: empty state")
print("ALL STREAMLIT TESTS PASSED")
