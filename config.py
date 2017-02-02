

class Config(object):
    DEBUG = True
    SECRET_KEY = 'insecurekeyfordev'

    JOBS = [
        {
            'id': 'job1',
            'func': 'iot:stabilize',
            # 'args': (1, 2),
            'trigger': 'interval',
            'seconds': 60
        }
    ]

    SCHEDULER_API_ENABLED = True