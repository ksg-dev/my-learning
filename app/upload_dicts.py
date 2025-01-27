course_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string',
        'unique': True
    },
    {
        'col': 2,
        'name': 'platform',
        'optional': False,
        'input': 'string',
        'unique': False
    },
    {
        'col': 3,
        'name': 'url',
        'optional': True,
        'input': 'url string',
        'unique': False
    },
    {
        'col': 4,
        'name': 'instructor',
        'optional': False,
        'input': 'string',
        'unique': False
    },
    {
        'col': 5,
        'name': 'start',
        'optional': True,
        'input': 'date m/dd/YYYY',
        'unique': False
    },
    {
        'col': 6,
        'name': 'complete',
        'optional': True,
        'input': 'date m/dd/YYYY',
        'unique': False
    },
    {
        'col': 7,
        'name': 'content_hours',
        'optional': True,
        'input': 'float',
        'unique': False
    },
    {
        'col': 8,
        'name': 'has_cert',
        'optional': False,
        'input': 'True/False case insensitive',
        'unique': False
    },
]

project_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string',
        'unique': False
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string',
        'unique': False
    },
    {
        'col': 3,
        'name': 'assignment_link',
        'optional': True,
        'input': 'url string',
        'unique': False
    },
    {
        'col': 4,
        'name': 'start',
        'optional': True,
        'input': 'date m/dd/YYYY',
        'unique': False
    },
    {
        'col': 5,
        'name': 'complete',
        'optional': True,
        'input': 'date m/dd/YYYY',
        'unique': False
    },
    {
        'col': 6,
        'name': 'section',
        'optional': True,
        'input': 'string',
        'unique': False
    },
    {
        'col': 7,
        'name': 'lecture',
        'optional': True,
        'input': 'string',
        'unique': False
    },
    {
        'col': 8,
        'name': 'repo',
        'optional': False,
        'input': 'string matching existing repo name',
        'unique': False
    },
    {
        'col': 9,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"',
        'unique': False
    },
    {
        'col': 10,
        'name': 'course',
        'optional': False,
        'input': 'string matching existing course name',
        'unique': False
    },
]

library_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string',
        'unique': False
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string',
        'unique': False
    },
    {
        'col': 3,
        'name': 'doc_link',
        'optional': True,
        'input': 'url string to reference docs',
        'unique': False
    },
    {
        'col': 4,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"',
        'unique': False
    },
]

api_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string',
        'unique': False
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string',
        'unique': False
    },
    {
        'col': 3,
        'name': 'url',
        'optional': True,
        'input': 'url string',
        'unique': False
    },
    {
        'col': 4,
        'name': 'doc_link',
        'optional': True,
        'input': 'url string to reference docs',
        'unique': False
    },
    {
        'col': 5,
        'name': 'requires_login',
        'optional': True,
        'input': 'True/False case insensitive',
        'unique': False
    },
    {
        'col': 6,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"',
        'unique': False
    },
]

tool_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string',
        'unique': False
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string',
        'unique': False
    },
    {
        'col': 3,
        'name': 'url',
        'optional': True,
        'input': 'url string',
        'unique': False
    },
    {
        'col': 4,
        'name': 'doc_link',
        'optional': True,
        'input': 'url string to reference docs',
        'unique': False
    },
    {
        'col': 5,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"',
        'unique': False
    },
]

resource_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string',
        'unique': False
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string',
        'unique': False
    },
    {
        'col': 3,
        'name': 'type',
        'optional': True,
        'input': 'choose one: cheatsheet, diagram, quickref, template, other',
        'unique': False
    },
    {
        'col': 4,
        'name': 'resource_url',
        'optional': True,
        'input': 'url string',
        'unique': False
    },
    {
        'col': 5,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"',
        'unique': False
    },
]

codelink_params = [
    {
        'col': 1,
        'name': 'name',
        'optional': False,
        'input': 'string',
        'unique': False
    },
    {
        'col': 2,
        'name': 'description',
        'optional': True,
        'input': 'string',
        'unique': False
    },
    {
        'col': 3,
        'name': 'link',
        'optional': False,
        'input': 'url permalink from GitHub',
        'unique': False
    },
    {
        'col': 4,
        'name': 'project',
        'optional': False,
        'input': 'string matching existing project name',
        'unique': False
    },
    {
        'col': 5,
        'name': 'concepts',
        'optional': True,
        'input': 'string separated by +, ex: "tkinter+gui+try block+random"',
        'unique': False
    },
]
