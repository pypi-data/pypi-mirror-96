"""The AWS Lambda emmaa-model-test definition.

This file contains the function that will be run when Lambda is triggered. It
must be placed on s3, which can either be done manually (not recommended) or
by running:

$ python update_lambda.py model_tests.py emmaa-model-test

in this directory.
"""

import boto3
from datetime import datetime

JOB_DEF = 'emmaa_jobdef'
QUEUE = 'emmaa-models-update-test'
PROJECT = 'aske'
PURPOSE = 'update-emmaa-results'
BRANCH = 'origin/master'


def lambda_handler(event, context):
    """Create a batch job to run model tests.

    This function is designed to be placed on lambda, taking the event and
    context arguments that are passed. Event parameter is used here to pass
    names of the model and of the test corpus.

    This Lambda function is configured to be invoked by emmaa-test-pipeline
    Lambda function.

    Parameters
    ----------
    event : dict
        A dictionary containing metadata regarding the triggering event. In
        this case the dictionary contains 'model' and 'tests' keys.
    context : object
        This is an object containing potentially useful context provided by
        Lambda. See the documentation cited above for details.

    Returns
    -------
    ret : dict
        A dict containing 'statusCode', with a valid HTTP status code, and any
        other data to be returned to Lambda.
    """
    batch = boto3.client('batch')
    model_name = event['model']
    test_corpus = event['tests']
    core_command = 'bash scripts/git_and_run.sh'
    if BRANCH is not None:
        core_command += f' --branch {BRANCH}'
    core_command += (' python scripts/run_model_tests_from_s3.py'
                     f' --model {model_name} --tests {test_corpus}')
    print(core_command)
    cont_overrides = {
        'command': ['python', '-m', 'indra.util.aws', 'run_in_batch',
                    '--project', PROJECT, '--purpose', PURPOSE,
                    core_command]
        }
    now_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    ret = batch.submit_job(
        jobName=f'{model_name}_{test_corpus}_tests_{now_str}',
        jobQueue=QUEUE, jobDefinition=JOB_DEF,
        containerOverrides=cont_overrides)
    job_id = ret['jobId']

    return {'statusCode': 200, 'result': 'SUCCESS', 'job_id': job_id}
