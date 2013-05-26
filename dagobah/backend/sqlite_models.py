""" SQLite model definitions. """

from collections import defaultdict

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

STREAM_LOG_SIZE = 1000000

class Dagobah(Base):

    id = Column(Integer, primary_key=True)
    created_jobs = Column(Integer, nullable=False)

    jobs = relationship('DagobahJob', backref='parent')

    def __init__(self):
        self.created_jobs = 0


    def __repr__(self):
        return "<SQLite:Dagobah (%d)>" % self.id


    @property
    def json(self):
        return {'dagobah_id': self.id,
                'created_jobs': self.created_jobs,
                'jobs': [job.json for job in self.jobs]}


class DagobahJob(Base):

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('dagobah.id'), index=True)
    status = Column(String(30), nullable=False)
    cron_schedule = Column(String(100))
    next_run = Column(DateTime)

    tasks = relationship('DagobahTask', backref='job')
    dependencies = relationship('DagobahDependency', backref='job')
    logs = relationship('DagobahLog', backref='job')

    def __init__(self):
        self.status = 'waiting'


    def __repr__(self):
        return "<SQLite:DagobahJob (%d)>" % self.id


    @property
    def json(self):
        return {'job_id': self.id,
                'name': self.name,
                'parent_id': self.parent.id
                'status': self.status,
                'cron_schedule': self.cron_schedule,
                'next_run': self.next_run,
                'tasks': [task.json for task in self.tasks],
                'dependencies': self._gather_dependencies()}


    def _gather_dependencies(self):
        result = defaultdict(list)
        for dep in self.dependencies:
            result[dep.from_task.name].append(dep.to_task.name)
        return result


class DagobahTask(Base):

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('dagobah_job.id'), index=True)
    name = Column(String(1000), nullable=False)
    command = Column(String(1000), nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    success = Column(String(30))

    def __init__(self, name, command):
        self.name = name
        self.command = command


    def __repr__(self):
        return "<SQLite:DagobahTask (%d)>" % self.id


    @property
    def json(self):
        return {'name': self.name,
                'command': self.command,
                'started_at': self.started_at,
                'completed_at': self.completed_at,
                'success': self.success}


class DagobahDependency(Base):

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('dagobah_job.id'), index=True)
    from_task_id = Column(Integer, ForeignKey('dagobah_task.id'), index=True)
    to_task_id = Column(Integer, ForeignKey('dagobah_task.id'), index=True)

    from_task = relationship(DagobahTask, foreign_keys=[from_task_id])
    to_task = relationship(DagobahTask, foreign_keys=[to_task_id])

    def __init__(self, from_task_id, to_task_id):
        self.from_task_id = from_task_id
        self.to_task_id = to_task_id


    def __repr__(self):
        return "<SQLite:DagobahDependency (%d)>" % self.id


class DagobahLog(Base):

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('dagobah_job.id'), index=True)
    start_time = Column(DateTime)
    last_retry_time = Column(DateTime)

    tasks = relationship('DagobahLogTask', backref='log')

    def __init__(self):
        pass


    def __repr__(self):
        return "<SQLite:DagobahLog (%d)>" % self.id


    @property
    def json(self):
        return {}


class DagobahLogTask(Base):

    id = Column(Integer, primary_key=True)
    log_id = Column(Integer, ForeignKey('dagobah_log.id'), index=True)
    name = Column(String(1000), nullable=False)
    start_time = Column(DateTime)
    complete_time = Column(DateTime)
    success = Column(String(30))
    return_code = Column(Integer)
    stdout = Column(String(STREAM_LOG_SIZE))
    stderr = Column(String(STREAM_LOG_SIZE))

    def __init__(self):
        pass


    def __repr__(self):
        return "<SQLite:DagobahLogTask (%d)>" % self.id


    @property
    def json(self):
        return {}