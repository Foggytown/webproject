#coding=utf-8
from flask_restful import reqparse, abort, Api, Resource
class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        global session
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('name', 'about', 'created_date', 'news'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        global session
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def abort_if_user_not_found(user_id):
        global session
        user = session.query(User).get(user_id)
        if not user:
            abort(404, message=f"User {user_id} not found")


class UserListResource(Resource):
    def get(self):
        global session
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('name', 'email', 'news')) for item in user]})

    def post(self):
        args = parser.parse_args()
        global session
        if session.query(User).filter(User.email == args['email']).first():
            abort(404, message=f"Такой пользователь уже есть")
        user = User(
            name=args['name'],
            email=args['email'],
            about=args['about']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})

parser = reqparse.RequestParser()
parser.add_argument('name', required=True, type=str)
parser.add_argument('about', required=False)
parser.add_argument('email', required=True, type=str)
parser.add_argument('password', required=True, type=str)
