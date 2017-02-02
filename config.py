INTERVAL = 3


class Config(object):
    DEBUG = True
    SECRET_KEY = 'insecurekeyfordev'

    JOBS = [
        {
            'id': 'job1',
            'func': 'iot:stabilize2',
            # 'args': (1, 2),
            'trigger': 'interval',
            'seconds': 500
        }
    ]

    SCHEDULER_API_ENABLED = True