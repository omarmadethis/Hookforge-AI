"""D162 test markers for CI. Tests that read assets excluded from git (docs/MANIFEST_EXCLUDED.md) carry the
`needs_data` marker. CI runs `pytest -m "not needs_data"`, while local runs on the box still run everything.
The list below was found by running the suite on a clean clone, bound over /workspace/hookforge."""
import os
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HAVE_DATA = os.path.exists(os.path.join(REPO, "private", "corpus", "corpus.csv")) and os.path.isdir(os.path.join(REPO, "out"))

# These modules load excluded data at import, so they are skipped at collection when the data is absent.
DATA_MODULES = ["test_gates.py", "test_mock_source_nan.py", "test_d128_recovery.py",
                "test_recreate_logic.py", "test_audience_fit.py", "test_edit_rules.py", "test_omar_style.py"]
collect_ignore = [] if HAVE_DATA else DATA_MODULES

NEEDS_DATA = {
 "test_backend_d91.py::test_capcut_learn", "test_d104_d108.py::test_concept_and_redo_queue",
 "test_d109_d112.py::test_new_products_plan_clean", "test_d109_d112.py::test_blockers_fixed_in_planner_not_gates",
 "test_d109_d112.py::test_rank_and_rationale", "test_d121_d124.py::test_digest",
 "test_d134_d136.py::test_ref_miner_transfer", "test_d134_d136.py::test_weekly_batch_min_videos",
 "test_d137_d140.py::test_weekly_clean_distinct", "test_d137_d140.py::test_price_and_lean",
 "test_d141_d145.py::test_p2_stays_archived", "test_d141_d145.py::test_lean_1080p_only_and_no_near_dupes",
 "test_d141_d145.py::test_daily_recommends_lean", "test_d141_d145.py::test_jolly_caption",
 "test_d145_d148.py::test_lean_calls_hook_only", "test_d145_d148.py::test_jolly_hook_and_say",
 "test_d149_d151.py::test_jolly_f06_hook_8_words", "test_d153_d155.py::test_weekly_all_pass",
 "test_d153_d155.py::test_regen_one_command", "test_d75_realism.py::test_g13_in_run_all_and_planner_applies_rules",
 "test_d75_realism.py::test_g13_block", "test_d94_d96.py::test_prepare_fb_all_and_swap",
 "test_fb_caption_d93.py::test_generate_all_products_fb_rules", "test_proof_guard.py::test_emoji_proven_passes",
 "test_proof_guard.py::test_store_ban_flagged", "test_proof_guard.py::test_jollyglow_clean",
 "test_proof_guard.py::test_same_product_block", "test_results_feed.py::test_sales_attribution_readonly",
 "test_results_feed.py::test_ly_season_prior_never_beats_own", "test_d99_d102.py::test_meta_csv_ingest",
}

def pytest_collection_modifyitems(config, items):
    import pytest
    for it in items:
        mod = os.path.basename(str(it.fspath))
        if f"{mod}::{it.name.split('[')[0]}" in NEEDS_DATA or mod in DATA_MODULES: it.add_marker(pytest.mark.needs_data)
