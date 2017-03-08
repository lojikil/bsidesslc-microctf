import kudritza
import os
import re
import uuid
from bottle import route, request, run, hook, redirect, app
from ast import literal_eval
from beaker.middleware import SessionMiddleware


parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_cache = {}
stripusername = re.compile('[^a-zA-Z0-9]*')

@hook('before_request')
def hostcheck():
    val = request.get_header('Host', 'nope')
    session = request.environ.get('beaker.session')

    if request.urlparts.path != '/nope':
        if not val.startswith('slc.punk'):
            redirect('/nope')

    path = request.urlparts.path

    if path != '/login' and path != '/signup' and path != '/nope':
        if 'loggedin' not in session or session['loggedin'] != True:
            redirect('/login')

@route('/login', method=['post', 'get'])
def login():
    if request.method == "POST":
        user = stripusername.sub("", request.POST.get("user", ''))
        pswd = request.POST.get("password", '')
        session = request.environ.get('beaker.session')
        if user == '' or pswd == '':
            return "Login failed"
        try:
            with file('./users/{0}.dat'.format(user)) as fh:
                data = fh.read().strip()
            if pswd != data:
                return "Login failed"
        except:
            return "Login failed"
        session['loggedin'] = True
        session['user'] = user
        return redirect('/')
    else:
        return template_cache['login']

@route('/signup', method=['post', 'get'])
def signup():
    if request.method == "POST":
        user = stripusername.sub("", request.POST.get("user", ''))
        pswd = request.POST.get("password", '')
        cnfm = request.POST.get("confirmp", '')
        session = request.environ.get('beaker.session')
        if user == '' or pswd == '':
            return "Registration failed"
        elif pswd != cnfm:
            return "Password must match confirmation password"
        try:
            filename = './users/{0}.dat'.format(user)
            if os.path.isfile(filename):
                return "User exists"
            with open(filename, 'w') as fh:
                fh.write(pswd)
            with open('./keys/{0}.dat'.format(user), 'w') as fh:
                key = uuid.uuid4().hex
                fh.write(key)
        except Exception as e:
            print e
            return "Registration failed foo"
        session['loggedin'] = True
        session['user'] = user
        session['key'] = key.encode('base64').encode('rot13')
        return redirect('/')
    else:
        return template_cache['signup']


@route('/lol', method=['post', 'get'])
@route('/lol/', method=['post', 'get'])
def lolhome():
    if request.method == "POST":
        prgm = kudritza.read(request.POST.get("prgm", ''))[0]
        return kudritza.keval(prgm, {'keys': 'removed; use get-keys'})
    else:
        return template_cache['lolhome']

@route('/validate')
def validate():
    val = request.GET.get('value', '')
    user = request.GET.get('user', '')
    authsuccess = False

    try:
        if val is None or val is '':
            return "Try passing 'value' as a query parameter"
        elif user is None or user is '':
            return "Try passing 'user' as a query parameter"
        dval = val.decode('base64')
        if user == 'admin' and dval == '41b28e17133a45088c8c5781ecb6204d':
            authsuccess = True
        else:
            return "Nope, not an administrator"
    except:
        return "Incorrect key format"
    if authsuccess:
        return redirect('/win')
    return "Hmm. Nope, not valid"


@route('/win')
def win():
    return "<html><body><center><b>You are the Winrar... but how come you didn't just force browse here?</b><hr>KEY:IamtheBSidesSLCWINRAR</hr></center></body>"


@route('/')
def index():
    return template_cache['index']


@route('/<name:path>.lol')
def lolloader(name):
    parts = name.split('/')
    root = parts[0:-1]
    filename = parts[-1]
    return lolscript.re_file(filename, root)

@route('/nope')
def nope():
    return template_cache['nope']


for name in ['lolhome', 'index', 'nope', 'login', 'signup']:
    with file('./templates/{0}.html'.format(name), 'r') as fh:
        template_cache[name] = fh.read()

if __name__ == "__main__":
    session_opts = {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True
    }
    app = SessionMiddleware(app(), session_opts)
    run(host='0.0.0.0', port=8085, app=app)
