from datetime import datetime
from tasksapp.models import Task
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse

from tasksapp.schemas.app_schemas import TasksSchema

Tasks_schema = TasksSchema()
Taskss_schema = TasksSchema(many=True)

# Taskss Resource
class TasksResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()

    @jwt_required()
    def post(self):
        self.parser.add_argument('title', type=str, required=True, help='Title cannot be blank')
        self.parser.add_argument('description', type=str, required=True, help='Description cannot be blank')
        self.parser.add_argument('due_date', type=str, required=True, help='Due date cannot be blank')

        data = self.parser.parse_args()

        # create date object from string => needed by sqlite db
        data['due_date'] = datetime.strptime(data['due_date'], '%Y-%m-%d')

        user_id = get_jwt_identity()

        new_Tasks = Task(**data, created_by=user_id)
        new_Tasks.save()
        return {'message': 'Tasks created successfully'}, 201

    @jwt_required()
    def get(self, Tasks_id=None):
        if Tasks_id:
            Tasks = Task.get_Tasks_by_id(Tasks_id)
            if Tasks:
                return Tasks_schema.dump(Tasks), 200
            return {'message': 'Tasks not found'}, 404

        user_id = get_jwt_identity()
        user_Tasks = Tasks.get_user_Tasks(user_id)
        return Taskss_schema.dump(user_Tasks), 200

    
    @jwt_required()
    def put(self, Tasks_id):
        # While updating a Tasks, all fields are optional
        self.parser.add_argument('title', type=str)
        self.parser.add_argument('description', type=str)
        self.parser.add_argument('due_date', type=str)
        self.parser.add_argument('complete', type=bool)
        
        Tasks = Tasks.get_Tasks_by_id(Tasks_id)

        if not Tasks:
            return {'message': 'Tasks not found'}, 404

        # check for ownership
        if Tasks.created_by != get_jwt_identity():
            return {'message': 'You are not authorized to update this Tasks'}, 401

        data = self.parser.parse_args()

        # update Tasks if there is new data else keep the old data
        Tasks.title = data['title'] if data['title'] else Tasks.title
        Tasks.description = data['description'] if data['description'] else Tasks.description
        Tasks.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d') if data['due_date'] else Tasks.due_date
        Tasks.complete = data['complete'] if data['complete'] else Tasks.complete
        Tasks.update()

        # return updated Tasks
        return Tasks_schema.dump(Tasks), 200


    @jwt_required()
    def delete(self, Tasks_id):
        Tasks = Tasks.get_Tasks_by_id(Tasks_id)

        if not Tasks:
            return {'message': 'Tasks not found'}, 404

        # check for ownership
        if Tasks.created_by != get_jwt_identity():
            return {'message': 'You are not authorized to delete this Tasks'}, 401

        Tasks.delete()
        return {'message': 'Tasks deleted successfully'}, 200
