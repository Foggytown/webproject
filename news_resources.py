#coding=utf-8
from flask_restful import reqparse, abort, Api, Resource
class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        global session
        news = session.query(News).get(news_id)   
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private', 'categories'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        global session
        news = session.query(News).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})
    
    def abort_if_news_not_found(news_id):
        global session
        news = session.query(News).get(news_id)
        if not news:
            abort(404, message=f"News {news_id} not found")    
            
class NewsListResource(Resource):
    def get(self):
        global session
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in news]})

    def post(self):
        args = parser.parse_args()
        global session
        catrgories=[]
        current_user=session.query(User).get(args['user_id']) 
        for i in args['categories'].lower().split(', '):
            categ=session.query(Category).filter(Category.name == i).first()
            if not categ:
                category=Category()
                category.name=i
                categories.append(category)
            else:
                news.categories.append(categ)                
                
        news = News(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            is_private=args['is_private'],
            categories=categories        
        )
        current_user.news.append(news)
        session.merge(current_user)         
        session.commit()
        return jsonify({'success': 'OK'})
    
    
parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('categories', required=False, type=str)