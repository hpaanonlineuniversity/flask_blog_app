from datetime import datetime
from bson import ObjectId
import re

class Post:
    def __init__(self, user_id, content, title, slug, image=None, category=None, _id=None, created_at=None, updated_at=None, post_model=None):
        self._id = _id
        self.user_id = user_id
        self.content = content
        self.title = title
        self.image = image or 'https://www.hostinger.com/tutorials/wp-content/uploads/sites/2/2021/09/how-to-write-a-blog-post.png'
        self.category = category or 'uncategorized'
        self.slug = slug
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self._post_model = post_model  # Reference to PostModel for database operations
    
    @property
    def id(self):
        return str(self._id) if self._id else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'content': self.content,
            'title': self.title,
            'image': self.image,
            'category': self.category,
            'slug': self.slug,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updatedAt': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @staticmethod
    def from_dict(data, post_model=None):
        return Post(
            _id=data.get('_id'),
            user_id=data['user_id'],
            content=data['content'],
            title=data['title'],
            image=data.get('image'),
            category=data.get('category'),
            slug=data['slug'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            post_model=post_model
        )

class PostModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.posts
    
    def _to_object_id(self, id_str):
        """Convert string ID to ObjectId"""
        try:
            return ObjectId(id_str)
        except:
            return None
    
    def create_indexes(self):
        self.collection.create_index([('title', 1)], unique=True)
        self.collection.create_index([('slug', 1)], unique=True)
        self.collection.create_index([('user_id', 1)])
        self.collection.create_index([('category', 1)])
        self.collection.create_index([('created_at', -1)])
        self.collection.create_index([('updated_at', -1)])
    
    def find_by_slug(self, slug):
        post_data = self.collection.find_one({'slug': slug})
        if post_data:
            return Post.from_dict(post_data, self)
        return None
    
    def find_by_id(self, post_id):
        object_id = self._to_object_id(post_id)
        if not object_id:
            return None
        post_data = self.collection.find_one({'_id': object_id})
        if post_data:
            return Post.from_dict(post_data, self)
        return None
    
    def find_by_user_id(self, user_id):
        posts_cursor = self.collection.find({'user_id': user_id})
        return [Post.from_dict(post, self) for post in posts_cursor]
    
    def create_post(self, post):
        post_data = {
            'user_id': post.user_id,
            'content': post.content,
            'title': post.title,
            'image': post.image,
            'category': post.category,
            'slug': post.slug,
            'created_at': post.created_at,
            'updated_at': post.updated_at
        }
        
        result = self.collection.insert_one(post_data)
        post._id = result.inserted_id
        post._post_model = self
        return post
    
    def update_post(self, post_id, update_data):
        object_id = self._to_object_id(post_id)
        if not object_id:
            raise ValueError("Invalid post ID")
        
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': object_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_post(self, post_id):
        object_id = self._to_object_id(post_id)
        if not object_id:
            raise ValueError("Invalid post ID")
        
        result = self.collection.delete_one({'_id': object_id})
        return result.deleted_count > 0
    
    def search_posts(self, query_filter, sort_field='updated_at', sort_direction=-1, skip=0, limit=9):
        """Search posts with filters, sorting and pagination"""
        posts_cursor = self.collection.find(query_filter).sort(sort_field, sort_direction).skip(skip).limit(limit)
        return [Post.from_dict(post, self) for post in posts_cursor]
    
    def count_posts(self, query_filter=None):
        """Count posts with optional filter"""
        if query_filter:
            return self.collection.count_documents(query_filter)
        return self.collection.count_documents({})