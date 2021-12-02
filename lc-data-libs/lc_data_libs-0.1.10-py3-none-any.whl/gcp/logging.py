import os
import google.cloud.logging
from google.cloud.logging_v2.resource import Resource
from google.cloud.logging_v2.logger import _GLOBAL_RESOURCE
from google.cloud import dataproc_v1


def get_execution_id_from_request(request):
    return request.headers.get("Function-Execution-Id")

def get_execution_id_from_context(context):
    return context.event_id

def get_gcp_handler(type, labels):

    client = google.cloud.logging.Client()
    name, resource, labels = _get_name_resource_labels(client,type,labels)
    handler = client.get_default_handler(name=type, resource=resource,labels=labels)
    return handler

def _get_name_resource_labels(logclient,type,labels):

    if type == 'cloud_dataproc_job':

        # Get step_id and job_id
        job_id = os.environ['PWD'].split('/')[-1]
        step_id = job_id.rsplit('-',1)[0]

        # Get job_uuid
        client = dataproc_v1.JobControllerClient(
            client_options={'api_endpoint': 'europe-west1-dataproc.googleapis.com:443'})
        job = client.get_job(project_id=logclient.project, region=os.environ['DATAPROC_REGION'], job_id=job_id)
        job_uuid = job.job_uuid

        # For unknown reason, logging to Stackdriver doesnt work if cluster_name or resource_name not in labels
        labels['step_id'] = step_id
        labels["dataproc.googleapis.com/cluster_name"] = os.environ['DATAPROC_CLUSTER_NAME']
        labels["dataproc.googleapis.com/cluster_uuid"] = os.environ['DATAPROC_CLUSTER_UUID']

        # Name and resource
        name = "dataproc.job.driver"
        resource = Resource(
            type='cloud_dataproc_job',
            labels={
              'job_id': job_id,
              'job_uuid': job_uuid,
              'region': os.environ['DATAPROC_REGION'],
           }
        )

    elif type == 'cloud_function':
        name = "cloudfunctions.googleapis.com%2Fcloud-functions"
        resource = Resource(
            type='cloud_function',
            labels={
                'function_name': os.environ['FUNCTION_NAME'],
                'region': os.environ['FUNCTION_REGION']
            }
        )
    else:
        name=type
        resource=_GLOBAL_RESOURCE
    return name, resource, labels


def add_labels(logger, labels):
    for h in logger.handlers:
        if hasattr(h,'labels'):
            h.labels.update(labels)

def add_gcp_handler(logger, type, labels):
    gcp_handler = get_gcp_handler(type, labels)
    logger.addHandler(gcp_handler)
    return logger