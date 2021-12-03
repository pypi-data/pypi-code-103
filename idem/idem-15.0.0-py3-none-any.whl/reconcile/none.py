async def loop(
    hub,
    name,
    sls_sources,
    render,
    runtime,
    cache_dir,
    sls,
    test,
    acct_file,
    acct_key,
    acct_profile,
):
    # This is the default reconciler
    # Reconciliation loop is skipped for backward compatibility
    return {
        "re_runs_count": 0,
        "require_re_run": False,
    }
