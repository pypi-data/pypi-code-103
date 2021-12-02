from copili import Pipeline
import schedule
import docker
import os
import sys
import logging

logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
log = logging.getLogger(__name__)


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )

    sys.path.append(os.path.normpath(SCRIPT_DIR))


d = docker.DockerClient(base_url="unix://var/run/docker.sock")

yaml = """
ExmaplePipeline:
    - name: test01
      image_repo: registry-gl.connect.dzd-ev.de:443/dzdtools/pubmedsucker
      sidecars:
        - name: redis01
          image_repo: redis
    - name: dataloader_02
      image_repo: registry-gl.connect.dzd-ev.de:443/dzdconnectpipeline/dataloading_debug_image
      tag: latest
      dependencies:
        - dataloader_01
      env_vars:
        MY_CONTAINER_ENV_VAL: VALUE02
        MY_CONTAINER_ENV_DICT: "{'KEY01':'VALUE01'}"
        RAISE_EXIT: "fehler"
    - name: dataloader_01
      image_repo: registry-gl.connect.dzd-ev.de:443/dzdconnectpipeline/dataloading_debug_image
      tag: latest
      volumes: {"${PWD}/logs": {"bind": "/tmp", "mode": "rw"}}
    - name: dataloader_03
      image_repo: stakater/exit-container
      dependencies: 
        - dataloader_02
        - dataloader_01
    - name: servicecontainer01
      image_repo: hello-world
      is_service_container: true
      dependencies: 
        - dataloader_02
"""


'''
yaml = """
CovidGraphPipeline:
    - name: CREATE_FULL_TEXT_INDEXES
      image_repo: covidgraph/graph-processing-fulltext-indexes
    - name: LENS_PATENT_DATA
      image_repo: covidgraph/data-lens-org-covid19-patents
    - name: CORD19
      image_repo: covidgraph/data-cord19
      env_vars:
        CONFIGS_PAPER_BATCH_SIZE: 300
        CONFIGS_NO_OF_PROCESSES: 25
    - name: TEXT_FRAGGER
      image_repo: covidgraph/graph-processing_fragmentize_text
      dependencies:
        - CORD19
        - LENS_PATENT_DATA
    - name: TEXT_GENE_MATCH
      image_repo: covidgraph/graph-processing_text_gene_match
      dependencies:
        - CORD19
        - LENS_PATENT_DATA
        - BIOBASE
        - TEXT_FRAGGER
    - name: CLINICAL_TRIALS_GOV
      image_repo: covidgraph/data-clinical_trials_gov
    - name: HELOMICS_HETIONET
      image_repo: helomics/data_hetionet
    - name: BIOBERT
      image_repo: tomasonjo/biobert-covidgraph
      dependencies:
        - CORD19
"""
'''
p = Pipeline(description=yaml, docker_client=d, dot_env_path="pipeline.env")
p.add_global_env_var("MY_VAR", "IN_ALL_CONTAINERS")
p.add_global_env_var("MY_JSON", {"my_crazy_dict": "in_all_containers"})
# run all containers once
p.run()

# Optional define custom service schedule (https://schedule.readthedocs.io)
# default is once a day at 00:00
p.service_schedule = schedule.every(30).seconds.do(p.run_service_containers)

# Step into service mode
p.start_service_mode()

# now servicecontainer01 will run every 30 seconds
