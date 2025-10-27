from ..models.person import Person
from bson import ObjectId

class PersonController:
    @staticmethod
    def get_all_people():
        """Get all people"""
        return Person.get_all()
    
    @staticmethod
    def get_person_by_id(pid):
        """Get person by ID"""
        return Person.get_by_id(pid)
    
    @staticmethod
    def create_person(name, age, job):
        """Create new person"""
        person = Person(name=name, age=age, job=job)
        result = person.save()
        return result
    
    @staticmethod
    def delete_person(pid):
        """Delete person by ID"""
        return Person.delete_by_id(pid)
    
    @staticmethod
    def update_person(pid, name=None, age=None, job=None):
        """Update person details"""
        update_data = {}
        if name: update_data['name'] = name
        if age: update_data['age'] = age
        if job: update_data['job'] = job
        
        if update_data:
            return Person.update_by_id(pid, update_data)
        return None