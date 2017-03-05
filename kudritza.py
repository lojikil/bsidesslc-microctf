#!/usr/bin/env python

import cgi
import copy
import sys
import re

# this is a simple, Curl (the programming language) like language.
# basically, we're looking for a tiny Scheme-ish language for the CTF, that
# can be used by contestants to get Remote Code Execution on the server,
# without having too much trouble with attempting to sandbox Python, or
# install a full instance of PHP/ColdFusion.

# The basic language is very similar to Curl or, really, Scheme with
# some Logo-ish elements, and curly braces rather than parens. It's
# actually *not* a terrible language, but I'm making a dirty implementation
# of it.

# the Language supports the following first-class types:

# Symbols: symbol
# Numbers: 1 1.4 (no rationals or complex in this tiny version here...)
# Strings: "this is a string"
# Lists: {list}

# The only "second class" type in the language is functions:
# {fn [params] ...}
# I'm obviously reading Curl code through my previous experiments with
# Digamma and Tatwyd, but I'm fine with that.

# The following forms/syntax are built-in to the language:
# if unless let define + - / * < > <= >= = not and or value eq? while progn
# define-variable

# The following functions are built-in as well:
# eval string-append paragraph get-http-parameter get-body-parameter
# request-method length button form input html cons append first rest
# echo list-variables

# Like Scheme, this language (no name yet; definitely not going with
# "lolscript") is Lexically scoped, but I'm not really going to dive
# into that one too much; if I break scoping rules somewhere, I'm
# ok with that. Makes the CTF more fun ;)

# Update: named it kudrtiza, or "Curl"


stripusername = re.compile('[^a-zA-Z0-9]*')


class KudritzaTypeClash(Exception):
    pass


class KudritzaNoSuchVar(Exception):
    pass


class KudritzaReadError(Exception):
    pass


class KudritzaApplyError(Exception):
    pass


class KudritzaProcedure(object):
    __slots__ = ['params', 'body', 'env']

    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __repr__(self):
        return "#<proc params: {0}>".format(self.params)

    def __str__(self):
        return "#<proc params: {0}>".format(self.params)


def read(src, idx=0):
    """ returns a Kudritza object from a python string. terrible hack, but
      similar to a naieve Scheme reader. """
    state = 0
    obj = None
    slen = len(src)
    if idx >= slen:
        raise KudritzaReadError()
    while idx < slen:
        if src[idx] == '{':
            obj = []
            idx += 1
            while True:
                ret = read(src, idx)
                if ret[2] == -1:
                    return (obj, ret[1] + 1, 0)
                obj.append(ret[0])
                idx = ret[1]
        elif src[idx] == '}':
            return (-1, idx, -1)
        elif src[idx] == "'":
            obj = ["quote"]
            ret = read(src, idx + 1)
            obj.append(ret[0])
            idx = ret[1]
            return (obj, ret[1], 0)
        elif src[idx] == ":":
            obj = ["value"]
            ret = read(src, idx + 1)
            obj.append(ret[0])
            idx = ret[1]
            return (obj, ret[1], 0)
        elif src[idx] == '"':
            obj = []
            idx += 1
            while idx < slen and src[idx] != '"':
                obj.append(src[idx])
                idx += 1
            return (''.join(obj), idx + 1, 1)
        elif src[idx] in '0123456789.':
            tmp = ""
            while True:
                if src[idx] not in '0123456789.':
                    break
                if idx >= slen:
                    break
                if state == 0:
                    if src[idx] == '.':
                        state = 1
                elif state == 1 and src[idx] == '.':
                    break  # illegal here
                tmp += src[idx]
                idx += 1
            if state == 0:
                return (int(tmp), idx, 2)
            else:
                return (float(tmp), idx, 2)
        elif src[idx] in '\t\r\n ':
            while src[idx] in '\t\r\n ':
                idx += 1
            return read(src, idx)
        else:
            obj = ""
            while idx < slen and src[idx] not in '{}\t\r\n" ':
                obj += src[idx]
                idx += 1
            return (obj, idx, 3)
    return (obj, idx, 0)


def keval(obj, env={}):
    " evaluates a Kudritza object"
    # this really should be a eval-apply cycle, but
    # instead each primitive form just evals the number of arguments it
    # should have. Messy, but works for now.
    if type(obj) is list:
        head = obj[0]
        rest = obj[1:]

        if type(head) is list:
            head = keval(head, env)

            if type(head) is str or type(head) is KudritzaProcedure:
                tmp = [head]
            else:
                tmp = copy.copy(head)

            tmp.extend(rest)
            return keval(tmp, env)

        elif type(head) is KudritzaProcedure:
            if len(rest) != len(head.params):
                raise KudritzaApplyError()

            tenv = head.env

            for n, v in zip(head.params, rest):
                tenv[n] = keval(v, tenv)

            for form in head.body:
                ret = keval(form, tenv)

            return ret
        elif type(head) is not str:
            raise KudritzaApplyError()
        elif head == "define":
            env[rest[0]] = keval(rest[1], env)
            return None
        elif head == "set!":
            if rest[0] not in env:
                raise KudritzaNoSuchVar(rest[0])
            env[rest[0]] = keval(rest[1], env)
        elif head == "if":
            ret = keval(rest[0], env)
            if ret:
                return keval(rest[1], env)
            else:
                return keval(rest[2], env)
        elif head == "unless":
            ret = keval(rest[0], env)
            if not ret:
                return keval(rest[1], env)
        elif head == "when":
            ret = keval(rest[0], env)
            if not ret:
                return keval(rest[1], env)

        elif head == "quote":
            return rest[0]

        elif head == "let":
            vardecs = rest[0]
            body = rest[1:]
            tenv = copy.copy(env)

            while True:
                varname = vardecs[0]
                varexpr = vardecs[1]
                vardecs = vardecs[2:]
                tenv[varname] = keval(varexpr, tenv)
                if len(vardecs) == 0:
                    break

            for form in body:
                ret = keval(form, tenv)

            return ret

        elif head == "fn":
            return KudritzaProcedure(rest[0], rest[1:], copy.copy(env))
        elif head == "get-keys":
            first = keval(rest[0], env)
            if type(first) is not str:
                raise KudritzaTypeClash()
            first = stripusername.sub("", first)
            with file('./keys/{0}.dat'.format(first)) as fh:
                data = fh.read().strip()
                return data.encode('base64').encode('rot13')
        elif head == "+":
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            if type(first) is not int and type(first) is not float:
                raise KudritzaTypeClash()
            if type(secnd) is not int and type(secnd) is not float:
                raise KudritzaTypeClash()
            return first + secnd
        elif head == "-":
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            if type(first) is not int and type(first) is not float:
                raise KudritzaTypeClash()
            if type(secnd) is not int and type(secnd) is not float:
                raise KudritzaTypeClash()
            return first - secnd
        elif head == "/":
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            if type(first) is not int and type(first) is not float:
                raise KudritzaTypeClash()
            if type(secnd) is not int and type(secnd) is not float:
                raise KudritzaTypeClash()
            return first / secnd
        elif head == "*":
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            if type(first) is not int and type(first) is not float:
                raise KudritzaTypeClash()
            if type(secnd) is not int and type(secnd) is not float:
                raise KudritzaTypeClash()
            return first * secnd
        elif head == "<":
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            if type(first) is not int and type(first) is not float:
                raise KudritzaTypeClash()
            if type(secnd) is not int and type(secnd) is not float:
                raise KudritzaTypeClash()
            return first < secnd
        elif head == ">":
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            if type(first) is not int and type(first) is not float:
                raise KudritzaTypeClash()
            if type(secnd) is not int and type(secnd) is not float:
                raise KudritzaTypeClash()
            return first > secnd
        elif head == "<=":
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            if type(first) is not int and type(first) is not float:
                raise KudritzaTypeClash()
            if type(secnd) is not int and type(secnd) is not float:
                raise KudritzaTypeClash()
            return first <= secnd
        elif head == ">=":
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            if type(first) is not int and type(first) is not float:
                raise KudritzaTypeClash()
            if type(secnd) is not int and type(secnd) is not float:
                raise KudritzaTypeClash()
            return first >= secnd
        elif head == "=":  # stealing from Arc; `=` is `eq?`
            first = keval(rest[0], env)
            secnd = keval(rest[1], env)
            return first == secnd
        elif head == "true":
            return True
        elif head == "false":
            return False
        elif head == "not":
            first = keval(rest[0], env)
            if first is True:  # strict typing here, lol
                return False
            return True
        elif head == "and":
            for item in rest:
                ret = keval(item, env)
                if not ret:
                    return False
            return True
        elif head == "or":
            for item in rest:
                ret = keval(item, env)
                if ret:
                    return True
            return False
        elif head == "list":
            rlist = []
            for item in rest:
                rlist.append(keval(item, env))
            return rlist
        elif head == "head":
            first = keval(rest[0], env)
            if type(first) is list:
                return first[0]
            else:
                raise KudritzaTypeClash()
        elif head == "rest":
            first = keval(rest[0], env)
            if type(first) is list:
                return first[1:]
            else:
                raise KudritzaTypeClash()
        elif head == "butlast":
            first = keval(rest[0], env)
            if type(first) is list:
                return first[0:-1]
            else:
                raise KudritzaTypeClash()
        elif head == "value":
            first = rest[0]
            first = keval(rest[0], env)
            if first in env:
                return env[first]
            raise KudritzaNoSuchVar()
        elif head == "while":
            cnd = rest[0]
            body = rest[1:]

            while True:

                for form in body:
                    ret = keval(form, env)

                test = keval(cnd, env)
                if not test:
                    break
            return ret
        elif head == "progn":
            progn = None
            for form in rest:
                progn = keval(form, env)
            return progn
        elif head == "define-variable":
            env[rest[0]] = keval(rest[1], env)
            return None
        elif head == "echo":
            tmp = keval(rest[0], env)
            print tmp
            return tmp
        elif head == "image":
            url = keval(rest[0], env)
            if len(rest) > 1:
                alt = keval(rest.get(1), env)
                return "<img src=\"{0}\" alt=\"{1}\">".format(url, alt)
            else:
                return "<img src=\"{0}\">".format(url)
        elif head == "list-variables":
            return ','.join(env.keys())
        elif head == "divider":
            ret = ["<div>"]
            for item in rest:
                tmp = keval(item, env)
                if type(tmp) is not str:
                    tmp = str(tmp)
                else:
                    tmp = cgi.escape(tmp)
                ret.append(tmp)
                ret.append(' ')
            ret.append('</div>')
            return ''.join(ret)
        elif head == "paragraph":
            ret = ["<p style=\"display:inline\">"]
            for item in rest:
                tmp = keval(item, env)
                if type(tmp) is not str:
                    tmp = str(tmp)
                if type(tmp) is str:
                    tmp = cgi.escape(tmp)
                else:
                    tmp = str(tmp)
                ret.append(tmp)
                ret.append(' ')
            ret.append("</p>")
            return ''.join(ret)
        elif head == "bold":
            ret = ["<p style=\"font-weight: bold; display: inline\">"]
            for item in rest:
                tmp = keval(item, env)
                if type(tmp) is not str:
                    tmp = str(tmp)
                if type(tmp) is str:
                    tmp = cgi.replace(tmp)
                else:
                    tmp = str(tmp)
                ret.append(tmp)
                ret.append(' ')
            ret.append("</p>")
            return ''.join(ret)
    else:
        return obj


def re_file(filename, root):
    """read and evaluate a file"""
    filename = filename.replace("../", "")
    try:
        fh = file("{0}/{1}".format(root, filename), 'r')
        text = fh.read()
        fh.close()
        data = read(text)
        return keval(data[0], {})
    except Exception as e:
        print e
        return KudritzaReadError()


def repl():
    env = {}
    while True:
        try:
            line = raw_input('kudritza> ')
            if line == ',q':
                break
            data = read(line)
            ret = keval(data[0], env)
            if ret is not None:
                print ret
        except Exception as e:
            print e
            pass

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        re_file(sys.argv[1], ".")
    else:
        repl()
