import json
import jwt
import math
import tornado.web
from sqlalchemy import sql
from app.storage import db


class RequestHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.database_engine

    def get_current_user(self):
        uid = self.get_secure_cookie('uid')
        if not uid:
            return None
        select = sql.select([db.users]).where(db.users.c.id == int(uid))
        result = self.db.execute(select).first()
        if result is None:
            return None
        return dict(result)

    @property
    def current_user_id(self):
        user = self.current_user
        if user:
            return user['id']
        return None

    def create_jwt(payload):
        encoded = jwt.encode(payload, 'cookie_secret', algorithm='HS256')
        return encoded

    def decode_jwt(encoded):
        payload = jwt.decode(encoded, verify=False)
        return payload

    def create_hash(password):
        derived_key = hashlib.pbkdf2_hmac('sha256', password, b'salt', 100000)
        derived_key = binascii.hexlify(derived_key)
        return derived_key

    def calculate_elo_rank(winner_rank, loser_rank, penalize_loser=True):
        rank_diff = winner_rank - loser_rank
        exp = (rank_diff * -1) / 400
        odds = 1 / (1 + math.pow(10, exp))
        if winner_rank < 2100:
            k = 32
        elif winner_rank >= 2100 and winner_rank < 2400:
            k = 24
        else:
            k = 16
        new_winner_rank = round(winner_rank + (k * (1 - odds)))
        if penalize_loser:
            new_rank_diff = new_winner_rank - winner_rank
            new_loser_rank = loser_rank - new_rank_diff
        else:
            new_loser_rank = loser_rank
        if new_loser_rank < 1:
            new_loser_rank = 1
        return (new_winner_rank, new_loser_rank)


'''
class JsonAPIHandler(RequestHandler):
    def finish_json(self, status, content=None):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_status(status)

        def prepare_json(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return obj

        if content:
            self.finish(json.dumps(content, default=prepare_json))
        else:
            self.finish()
    def json_body(self):
        return json.loads(self.request.body.decode('utf8'))
'''