from pype import cli


def test_pipeline_can_run(pipeline_config, pipeline_dir):
    cli.run_(pipeline_config, log=False, tag=None)


def test_pipeline_only_runs_tags(pipeline_config, pipeline_dir):
    cli.run_(pipeline_config, log=False, tag='a')
    __import__("pdb").set_trace() #TODO delme



