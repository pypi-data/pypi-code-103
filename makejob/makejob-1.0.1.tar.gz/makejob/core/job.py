import os
from pathlib import Path
import textwrap

from .parse import parse_conf


def make_part_job(jobname, cmd, memory='1G', status='waiting', scheds='-V -cwd'):
    job = textwrap.dedent(f'''
        job_begin
            name {jobname}
            memory {memory}
            status {status}
            sched_options {scheds}
            cmd_begin
                {cmd}
            cmd_end
        job_end
    ''').strip()
    return job


def make_job(configfile, base_scheds):
    order_list = []
    job_list = []
    for line in parse_conf(configfile):
        script, memory, depend_scripts, thread = line
        jobname = os.path.basename(script)
        cmd = 'sh ' + str(Path(script).resolve())
        scheds = base_scheds
        if thread:
            scheds = f'{base_scheds} -l p={thread}'
        job = make_part_job(jobname, cmd, memory=memory, scheds=scheds)
        job_list.append(job)

        # deal with orders
        if depend_scripts:
            for depend_script in depend_scripts.split(','):
                depend_name = os.path.basename(depend_script)
                order = f'order {jobname} after {depend_name}'
                order_list.append(order)
    return job_list, order_list


if __name__ == "__main__":
    job = make_part_job('QC', 'sh run_qc.sh')
    print(job)
    job = make_part_job('Mapping', 'sh run_mapping.sh', '2G')
    print(job)
