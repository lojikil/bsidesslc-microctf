from bottle import route, request, run
import kudritza
import os
from ast import literal_eval


parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_cache = {}


@route('/lol', method=['post', 'get'])
@route('/lol/', method=['post', 'get'])
def lolhome():
    if request.method == "POST":
        prgm = kudritza.read(request.POST.get("prgm", ''))[0]
        return kudritza.keval(prgm, {"uuids":envuuids})
    else:
        return template_cache['lolhome']

@route('/validate')
def validate():
    val = request.GET.get('value')
    try:
        if val is None or val is '':
            return "Try passing 'value' as a query parameter"
        dval = literal_eval(val.decode('base64'))
        if type(dval) is tuple:
            if dval[0] == 'SinterKlaas' and dval[1] == '05d6c968-ab39-48f1-abe5-f26262bb1a96':
                return "Yes, you found Santa Claus!"
        return "Nope, Not Santa!"
    except:
        return "Nope, Not Santa!"

@route('/')
def index():
    return template_cache['index']


@route('/<name:path>.lol')
def lolloader(name):
    parts = name.split('/')
    root = parts[0:-1]
    filename = parts[-1]
    return lolscript.re_file(filename, root)


for name in ['lolhome', 'index']:
    with file('./templates/{0}.html'.format(name), 'r') as fh:
        template_cache[name] = fh.read()

uuids = [
    ('JackMannino', '06f1dc39-3b58-431b-8efc-22a79f5d2c98'),
    ('KenJohnson', '086c0e74-6d30-4e0a-8f96-830d9ea60d0c'),
    ('SethLaw', '8ccbf290-a773-47fb-8064-7c0c7d9df75c'),
    ('DavidWhitlaw', '267b4d16-0b62-49a8-97f4-45e0c3553b84'),
    ('DavidLindner', '56956bcc-e833-481b-9e66-a4e5046a2713'),
    ('MeganBradley', 'e19ba096-d8af-47d8-9043-90a90f33a380'),
    ('TimTomes', '10c204b3-f99e-4057-b3b4-92a3755aaa97'),
    ('AbdullahMunawar', '6149afb7-f1b0-4e34-8b2d-206f1943021e'), 
    ('BrianGlas', 'bf4dc2ed-118d-4d0b-9108-3fa891342371'),
    ('NikkiKasakitis', 'd16889a9-e6f6-4133-9480-734c0ba75ad0'),
    ('AmyMcElroy', 'fe78d347-9a76-41df-99cb-8074ff7673b1'),
    ('CleaLevinson', '796dc7f6-6e0b-4750-9cc7-a04529f27b0a'),
    ('JamesMeeks', '609a02ac-c313-441e-8a8c-3b62a20f8025'),
    ('HannyFlint', '20f897f3-496b-42a3-aaa7-c6e734a708ba'),
    ('StefanEdwards', '409b08df-f079-4f61-8265-ad046b1b2de9'),
    ('JohnPoulin', 'eeb2f81e-65ca-430b-8830-a21ad3a4606f'),
    ('DavidCoursey', '02782a6c-2559-4b92-8752-3fe0e3645a71'),
    ('DavidVo', 'c7039160-b4b2-4e3a-a5cc-f2dbd45388b4'),
    ('JonnCallahan', '78c9ec1e-a615-4160-a0be-75633b910951'),
    ('RyanReid', 'a0d74396-b5fe-4f5c-b6e9-6d15f722749c'),
    ('MarcusRichardson', '92bcf0de-caaa-4c3a-b7a3-2fa089c82b11'),
    ('RiandiWiguna', 'f739f6b3-32c7-4e1d-8943-50ab5f53688b'),
    ('AnandVemuri', '971edafa-14a8-499c-a5ea-1de0b0e0c0a1'),
    ('AlejandroSaenz', '6d263e94-e9e1-468f-8d71-10453e6891c5'),
    ('SeanLyford', 'dd11fd08-9ef5-44c1-94a6-c2fca1325b84'),
    ('RichGrimes', '2e4e1e4c-454e-4422-83bd-e65c67dbcae9'),
    ('HongyiDong', 'e6c8c7dd-da92-4af7-84aa-0b7fd2400f0e'),
    ('SinterKlaas', '05d6c968-ab39-48f1-abe5-f26262bb1a96')]

envuuids = [str(x).encode('base64').encode('rot13') for x in uuids]

if __name__ == "__main__":
    run(host='0.0.0.0', port=8085)
