__all__ = [
    'use_job_namespace',
    'put_job',
    'put_jobs',
    'get_job',
    'get_jobs',
    'finish_jobs',
    'abandon_jobs',
    'peek_job',
]


from .importtypes import *
from .sql import *


_uuid = None

def _get_id():
    global _uuid
    if _uuid is None:
        _uuid = query(None, 'select uuid_short()')
    return _uuid


_ns = None

def use_job_namespace(namespace: str):
    """Claim the job queue namespace of this process
    Must be called before any other job queue APIs.
    """
    assert len(namespace) <= 32, namespace
    global _ns
    _ns = namespace


def put_job(job: str):
    """Put a job into the job queue"""
    put_jobs([ job ])


def put_jobs(jobs: Iterable[str]):
    """Put multiple jobs into the job queue"""
    sql = 'insert ignore into mq (namespace, message) values (%s, %s)'
    commit_multi('mq', sql, [ (_ns, job.encode('utf8')) for job in jobs ])


def get_job():
    """Take a job from the job queue
    This will mark all previously taken jobs as successfully completed.
    """
    ret = get_jobs(1)
    return ret[0] if ret else None


def get_jobs(num: int):
    """Take multiple jobs from the job queue
    This will mark all previously taken jobs as successfully completed.
    """
    finish_jobs()
    sql = 'update mq set worker=%s where namespace=%s and worker is null limit %s'
    commit('mq', sql, (_get_id(), _ns, num))
    sql = 'select message from mq where namespace=%s and worker=%s'
    jobs = query('mq', sql, (_ns, _get_id()), multi = True)
    return [ job.decode('utf8') for job in jobs ]


def finish_jobs():
    """Mark all taken jobs as successfully completed"""
    sql = 'delete from mq where namespace=%s and worker is not null and worker=%s'
    commit('mq', sql, (_ns, _get_id()))


def abandon_jobs():
    """Mark all taken jobs as failed"""
    sql = 'update mq set worker=0 where namespace=%s and worker=%s'
    commit('mq', sql, (_ns, _get_id()))


def peek_job(namespace = None):
    """Peek the next job of job queue without modifying it
    Mainly for debuging purpose.
    """
    if namespace is None:
        namespace = _ns
    sql = 'select message from mq where namespace=%s and worker is null order by id asc limit 1'
    ret = query('mq', sql, namespace)
    return ret.decode('utf8') if ret is not None else None
