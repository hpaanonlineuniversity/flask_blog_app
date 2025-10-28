from datetime import datetime
from bson import ObjectId

class Comment:
    def __init__(self, content, post_id, user_id, likes=None, number_of_likes=0, _id=None, created_at=None, updated_at=None, comment_model=None):
        self._id = _id
        self.content = content
        self.post_id = post_id
        self.user_id = user_id
        self.likes = likes or []
        self.number_of_likes = number_of_likes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self._comment_model = comment_model  # Reference to CommentModel for database operations
    
    @property
    def id(self):
        return str(self._id) if self._id else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'postId': self.post_id,
            'userId': self.user_id,
            'likes': self.likes,
            'numberOfLikes': self.number_of_likes,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updatedAt': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @staticmethod
    def from_dict(data, comment_model=None):
        return Comment(
            _id=data.get('_id'),
            content=data['content'],
            post_id=data['post_id'],
            user_id=data['user_id'],
            likes=data.get('likes', []),
            number_of_likes=data.get('number_of_likes', 0),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            comment_model=comment_model
        )

class CommentModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.comments
    
    def _to_object_id(self, id_str):
        """Convert string ID to ObjectId"""
        try:
            return ObjectId(id_str)
        except:
            return None
    
    def create_indexes(self):
        self.collection.create_index([('post_id', 1)])
        self.collection.create_index([('user_id', 1)])
        self.collection.create_index([('created_at', -1)])
    
    def find_by_id(self, comment_id):
        object_id = self._to_object_id(comment_id)
        if not object_id:
            return None
        comment_data = self.collection.find_one({'_id': object_id})
        if comment_data:
            return Comment.from_dict(comment_data, self)
        return None
    
    def find_by_post_id(self, post_id, sort_field='created_at', sort_direction=-1):
        """Find all comments for a post"""
        comments_cursor = self.collection.find({'post_id': post_id}).sort(sort_field, sort_direction)
        return [Comment.from_dict(comment, self) for comment in comments_cursor]
    
    def find_by_user_id(self, user_id):
        """Find all comments by a user"""
        comments_cursor = self.collection.find({'user_id': user_id})
        return [Comment.from_dict(comment, self) for comment in comments_cursor]
    
    def create_comment(self, comment):
        comment_data = {
            'content': comment.content,
            'post_id': comment.post_id,
            'user_id': comment.user_id,
            'likes': comment.likes,
            'number_of_likes': comment.number_of_likes,
            'created_at': comment.created_at,
            'updated_at': comment.updated_at
        }
        
        result = self.collection.insert_one(comment_data)
        comment._id = result.inserted_id
        comment._comment_model = self
        return comment
    
    def update_comment(self, comment_id, update_data):
        object_id = self._to_object_id(comment_id)
        if not object_id:
            raise ValueError("Invalid comment ID")
        
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': object_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_comment(self, comment_id):
        object_id = self._to_object_id(comment_id)
        if not object_id:
            raise ValueError("Invalid comment ID")
        
        result = self.collection.delete_one({'_id': object_id})
        return result.deleted_count > 0
    
    def get_all_comments(self, sort_field='created_at', sort_direction=-1, skip=0, limit=9):
        """Get all comments with pagination and sorting"""
        comments_cursor = self.collection.find().sort(sort_field, sort_direction).skip(skip).limit(limit)
        return [Comment.from_dict(comment, self) for comment in comments_cursor]
    
    def count_comments(self, query_filter=None):
        """Count comments with optional filter"""
        if query_filter:
            return self.collection.count_documents(query_filter)
        return self.collection.count_documents({})
    
    def toggle_like(self, comment_id, user_id):
        """Toggle like for a comment"""
        object_id = self._to_object_id(comment_id)
        if not object_id:
            raise ValueError("Invalid comment ID")
        
        comment = self.find_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found")
        
        if user_id in comment.likes:
            # Unlike
            comment.likes.remove(user_id)
            comment.number_of_likes -= 1
        else:
            # Like
            comment.likes.append(user_id)
            comment.number_of_likes += 1
        
        # Update in database
        self.collection.update_one(
            {'_id': object_id},
            {
                '$set': {
                    'likes': comment.likes,
                    'number_of_likes': comment.number_of_likes,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return comment