course_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 2,
        'name': 'platform',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 3,
        'name': 'url',
        'optional': True,
        'input': 'url string'
    },
    {
        'col': 4,
        'name': 'instructor',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 5,
        'name': 'start',
        'optional': True,
        'input': 'date m/dd/YYYY'
    },
    {
        'col': 6,
        'name': 'complete',
        'optional': True,
        'input': 'date m/dd/YYYY'
    },
    {
        'col': 7,
        'name': 'content_hours',
        'optional': True,
        'input': 'float'
    },
    {
        'col': 8,
        'name': 'has_cert',
        'optional': False,
        'input': 'True/False case insensitive'
    },
]

project_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string'
    },
    {
        'col': 3,
        'name': 'assignment_link',
        'optional': True,
        'input': 'url string'
    },
    {
        'col': 4,
        'name': 'start',
        'optional': True,
        'input': 'date m/dd/YYYY'
    },
    {
        'col': 5,
        'name': 'complete',
        'optional': True,
        'input': 'date m/dd/YYYY'
    },
    {
        'col': 6,
        'name': 'section',
        'optional': True,
        'input': 'string'
    },
    {
        'col': 7,
        'name': 'lecture',
        'optional': True,
        'input': 'string'
    },
    {
        'col': 8,
        'name': 'repo',
        'optional': False,
        'input': 'string matching existing repo name'
    },
    {
        'col': 9,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"'
    },
    {
        'col': 10,
        'name': 'course',
        'optional': False,
        'input': 'string matching existing course name'
    },
]

library_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string'
    },
    {
        'col': 3,
        'name': 'doc_link',
        'optional': True,
        'input': 'url string to reference docs'
    },
    {
        'col': 4,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"'
    },
]

api_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string'
    },
    {
        'col': 3,
        'name': 'url',
        'optional': True,
        'input': 'url string'
    },
    {
        'col': 4,
        'name': 'doc_link',
        'optional': True,
        'input': 'url string to reference docs'
    },
    {
        'col': 5,
        'name': 'requires_login',
        'optional': True,
        'input': 'True/False case insensitive'
    },
    {
        'col': 6,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"'
    },
]

tool_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string'
    },
    {
        'col': 3,
        'name': 'url',
        'optional': True,
        'input': 'url string'
    },
    {
        'col': 4,
        'name': 'doc_link',
        'optional': True,
        'input': 'url string to reference docs'
    },
    {
        'col': 5,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"'
    },
]

resource_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string'
    },
    {
        'col': 3,
        'name': 'type',
        'optional': True,
        'input': 'choose one: cheatsheet, diagram, quickref, template, other'
    },
    {
        'col': 4,
        'name': 'resource_url',
        'optional': True,
        'input': 'url string'
    },
    {
        'col': 5,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"'
    },
]

codelink_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string'
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string'
    },
    {
        'col': 3,
        'name': 'link',
        'optional': False,
        'input': 'url permalink from GitHub'
    },
    {
        'col': 4,
        'name': 'project',
        'optional': False,
        'input': 'string matching existing project name'
    },
    {
        'col': 5,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"'
    },
]