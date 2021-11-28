from yawl.workflows.bigquery_workflow import BigQueryWorkflowStep
from yawl.workflows.queue import queue

if __name__ == "__main__":
    step_1 = BigQueryWorkflowStep(
        sql="./sql_files/example.sql",
        dest_table="beaming-ring-330423.transfer_test.table_1",
        squeduled_query_name="test_query101",
        schedule="every mon,wed 09:00",
    )
    step_2 = BigQueryWorkflowStep(
        sql="./sql_files/example.sql",
        dest_table="beaming-ring-330423.transfer_test.table_2",
        squeduled_query_name="test_query_102",
        schedule="every tue,thu 10:00",
    )
    with queue() as q:
        q.add(step_1).add(step_2).process()
