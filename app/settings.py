import os


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Configuration:
    project_root = PROJECT_ROOT
    application_root = os.path.join(PROJECT_ROOT, 'app')

    debug = os.getenv('DEBUG', None) in ['yes', '1']
    database = 'postgresql://odoo:odoodb@localhost/pong'

    def as_dict(self):
        conf = {}
        for name in dir(self):
            if name.startswith('_'):
                continue
            value = getattr(self, name)
            if value is NotImplemented:
                continue
            chunks = name.split('__')
            node = conf
            for chunk in chunks[:-1]:
                node = node[chunk] = {}
            node[chunks[-1]] = value
        return conf


class Development(Configuration):
    debug = True
    http_server_port = 7878
    http_server_address = '127.0.0.1'
