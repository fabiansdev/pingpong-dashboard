import json

import tornado.auth
import tornado.gen
import tornado.httpclient

from app.handlers.base import RequestHandler
from app.storage import db


class PlayerHandler(RequestHandler):
    def get(self):
        
        if self.get_argument('all'):
            users = cursor.query(UserUser).all()
            result = [{'player': x.username, 'score': x.score}for x in users]
            self.write(json_encode(result))
          
        try:
            token = self.get_argument('token')
        except:
            self.set_status(400)
            error_message = "Error 400: Missing one or more parameters."
            self.finish(error_message)
        else:

            payload = self.decode_jwt(token)
            cursor = self.db()
            user = cursor.query(UserUser).filter(UserUser.email == payload['email']).first()
            if user is None:
                result = {'message': 'Email is not registered'}
                self.set_status(404)
                self.finish(result)
            if user.token != token:
                result = {'message': 'Operation not allowed'}
                self.set_status(401)
                self.finish(result)

            result = [{'player': user.username, 'score': user.score}]             
            self.write(json_encode(result))

    def post(self):
        try:
            email = self.get_argument('email')
            username = self.get_argument('username')
            password = self.get_argument('password')
        except:
            self.set_status(400)
            error_message = "Error 400: Missing one or more parameters."
            self.finish(error_message)
        else:
            cursor = self.db()
            user = cursor.query(UserUser).filter(UserUser.username == username).filter(UserUser.email == email).first()
            if user:
                self.send_error(404, exc_info="user already exist")
            else:
                pass_hash = self.create_hash(password)
                new_user = UserUser(username=username, email=email, score = 1200, password_crypt=pass_hash, token='')
                cursor.add(new_user)
                cursor.commit()


class PlayerGameHandler(RequestHandler):
    def get(self):
        try:
            token = self.get_argument('token')
        except:
            self.set_status(400)
            error_message = "Error 400: Missing one or more parameters."
            self.finish(error_message)
        else:

            payload = self.decode_jwt(token)
            cursor = self.db()
            user = cursor.query(UserUser).filter(UserUser.email == payload['email']).first()
            if user is None:
                result = {'message': 'Email is not registered'}
                self.set_status(404)
                self.finish(result)
            if user.token != token:
                result = {'message': 'Operation not allowed'}
                self.set_status(401)
                self.finish(result)

            games = cursor.query(UserGame).filter(UserGame.player_one_id == user.id).filter(UserGame.player_two_id == user.id).all()

            result = [{'player_one': x.player_one.username, 'player_two': x.player_two.username, 'score': x.get_score()} for x in games]             
            self.write(json_encode(result))

    def post(self):
        try:
            player_one = self.get_argument('player_one')
            player_two = self.get_argument('player_two')
            score_one = int(self.get_argument('password'))
            score_two = int(self.get_argument('password'))
        except:
            self.set_status(400)
            error_message = "Error 400: Missing one or more parameters."
            self.finish(error_message)
        else:
            cursor = self.db()
            user_one = cursor.query(UserUser).filter(UserUser.username == player_one).first()
            user_two = cursor.query(UserUser).filter(UserUser.username == player_two).first()
            if player_two is None or player_one is None:
                self.send_error(404, exc_info="Player/s Doen't exist in our database.")
            else:
                new_game = UserGame(player_one_id=user_one.id, player_two_id=user_two.id, score_one = score_one, score_two = score_two)
                cursor.add(new_game)
                new_elos = self.calculate_elo_rank(player_one.score, player_two.score)
                player_one.score = new_elos[0]
                player_two.score = new_elos[1]
                cursor.commit()
                result = [{'response': 'Game register sucessfully'}]
                self.write(json_encode(result))       