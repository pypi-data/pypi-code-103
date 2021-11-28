"""
任務寫在此 並利用 @celery.task修飾
"""

from main.extension import celery


@celery.task
def ping():
    print('ping...')
