async def run(
    hub,
    plugin,
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
    ret = await hub.reconcile[plugin].loop(
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
    )

    return ret
