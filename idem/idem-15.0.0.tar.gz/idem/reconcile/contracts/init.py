async def sig_loop(
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
    """
    Validate the signature of the reconciliation loop function
    """
    ...


def post_loop(self, hub):
    """
    Conform the return structure of every loop function to this format.
    """
    try:
        assert isinstance(hub.ret["re_runs_count"], int)
        assert isinstance(hub.ret["require_re_run"], bool)
    except KeyError:
        hub.log.error("Improperly formatted loop() returned value")
