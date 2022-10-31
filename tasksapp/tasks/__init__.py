from tasksapp.tasks.resource import TasksResource


def todos_routes(api):
    api.add_resource(TasksResource, '/api/todos', '/api/tasks/<int:tasks_id>')