#!/usr/bin/env python
'''
MIT License

Copyright (c) 2018 Tenable Network Security, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import click, logging, time
from tenable.io import TenableIO
from .cscc import SecurityCommandCenter
from .transform import GoogleSCCIngest
from . import __version__

@click.command()
@click.option('--tio-access-key',
    envvar='TIO_ACCESS_KEY', help='Tenable.io Access Key')
@click.option('--tio-secret-key',
    envvar='TIO_SECRET_KEY', help='Tenable.io Secret Key')
@click.option('--batch-size', '-b', envvar='BATCH_SIZE', default=100,
    type=click.INT, help='Export/Import Batch Sizing')
@click.option('--verbose', '-v', envvar='VERBOSITY', default=0,
    count=True, help='Logging Verbosity')
@click.option('--observed-since', '-s', envvar='SINCE', default=0,
    type=click.INT, help='The unix timestamp of the age threshold')
@click.option('--run-every', '-r', envvar='RUN_EVERY',
    type=click.INT, help='How many hours between recurring imports')
@click.option('--threads', '-t', envvar='THREADS', default=2,
    type=click.INT, help='How many concurrent threads to run for the import.')
@click.option('--service-account-file', '-S', envvar='CSCC_ACCOUNT_FILE',
    type=click.Path(exists=True),
    help='The JSON file for the service account.')
@click.option('--source-id', '-i', envvar='CSCC_SOURCE_ID',
    help='The GCP CSCC Source ID')
def cli(tio_access_key, tio_secret_key, batch_size, verbose, observed_since,
        run_every, threads, service_account_file, source_id):
    '''
    Tenable.io -> Google Cloud Security Command Center Transformer & Ingester
    '''
    # Setup the logging verbosity.
    if verbose == 0:
        logging.basicConfig(level=logging.WARNING)
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    if verbose > 1:
        logging.basicConfig(level=logging.DEBUG)

    # Initiate the Tenable.io API model, the Ingester model, and start the
    # ingestion and data transformation.
    tio = TenableIO(tio_access_key, tio_secret_key,
        vendor='Tenable',
        product='Google CSCC',
        build=__version__)
    gcp = SecurityCommandCenter(service_account_file, source_id)
    ingest = GoogleSCCIngest(tio, gcp)
    ingest.ingest(observed_since, batch_size, threads)

    # If we are expected to continually re-run the transformer, then we will
    # need to track the passage of time and run every X hours, where X is
    # defined by the user.
    if run_every and run_every > 0:
        while True:
            sleeper = run_every * 3600
            last_run = int(time.time())
            logging.info(
                'Sleeping for {}s before next iteration'.format(sleeper))
            time.sleep(sleeper)
            logging.info(
                'Initiating ingest with observed_since={}'.format(last_run))
            ingest.ingest(last_run, batch_size, threads)