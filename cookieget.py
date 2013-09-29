#!/usr/local/bin/python
"""
The MIT License (MIT)

Copyright (c) 2013 spoljo@diznilend.org

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import time
import Levenshtein as lsd
import clint.textui as ct
import prettytable
import requests
from sys import argv
import numpy


class NoCookies(Exception):
    """
    No cookie Exception.
    """
    pass


def doprefix(site_url):
    """
    Returns protocol prefix for url if needed.
    """
    if site_url.startswith("http://") or site_url.startswith("https://"):
        return ""
    return "http://"


def fme(post_data):
    """
    Turns url encoded post data into dictionary.
    """
    import urlparse
    dic = {}
    for key, value in urlparse.parse_qsl(post_data):
        dic[key] = value
    return dic


def cookieget(url, cookie_number, logindata_string=None, type_login=None):
    """Fetches cookies by either GET or POST requests.

    Requests cookie_number number of cookies from the url with
    either GET or POST.
    The action depends if logindata_string and type_login were given.

    Args:
        url: Url to grab cookies from.
        cookie_number: How much cookies to grab.
        logindata_string: Urlencoded data to pass to the server.
        type_login: Either 'json' to serialise it, or anything for plain
        urlencoded POST.

    Returns:
        A list of CookieJar objects. CookieJar objects will be initialised,
        but there is posibility that they will be empty.

    """
    lista_cookiea = []
    prefix = doprefix(url)
    ct.puts("Fetching cookies")
    for _ in ct.progress.bar(range(cookie_number)):
        if not logindata_string:
            response = requests.get(prefix+url)
        else:
            if type_login == "json":
                headers = {"Content-type":"application/json"}
            else:
                headers = {}
            response = requests.post(prefix + url, data=fme(logindata_string),
                    headers=headers)
        lista_cookiea.append(response.cookies)
    return lista_cookiea


def dictify_cookies(cookie_list):
    """
    Turns list of cookies into dictionary where key is name of the cookie
    and value is list of cookie values.

    Args:
        cookie_list: List of CookieJar objects.

    Returns:
        Dictionary of cookie names as key and list of cookie values as
        dictionary value.
        Example:

        {"__cfduid":["db37572f9dd1", "d02f7e47ecb5"],
        "ts":["1380409840349","1380409840992"]}

    """
    dicookie = {}
    cookies = []
    _ = [cookies.extend(i.items()) for i in cookie_list]
    for name, cookie_val in cookies:
        if name in dicookie:
            dicookie[name].append(cookie_val)
        else:
            dicookie[name] = [cookie_val]
    return dicookie


def draw_cookies(name, lista):
    """
    Creates a PrettyTable object.

    Args:
        name: Name of the cookie column.
        lista: list of cookie values in a column

    Returns:
        Drawable(printable) PrettyTable object.
    """
    table = prettytable.PrettyTable()
    name = ct.colored.green(name).color_str
    table.add_column(name, lista)
    return table


def levdis(lista):
    """
    Calculates mean Levenshtein distance between cookies.

    Args:
        lista: list of cookie values

    Returns:
        Float representing mean Levenshtein distance between all cookie values.
    """
    matrix = []
    for i in lista:
        matrix.append([lsd.distance(x, i) for x in  lista])
    fastmatrix = numpy.array(matrix)
    return fastmatrix.mean()


def findtimestamp(lista, timee):
    """
    Tries to find UNIX timestamp within cookies.

    Args:
        lista: list of cookie values
        timee: string of UNIX timestamp, without the decimals

    Returns:
        tmp_pos: possible start of UNIX timestamp within cookie values
        leng: Lenght of timestamp matched in all cookies
    """
    for i in range(len(timee)):
        pos =  [row.find(timee[:i]) for row in lista]
        if  all([ True if x>=0 else False for x in pos]):
            tmp_pos = pos[0]
        else:
            leng = i
            break
    else:
        leng = i
    return tmp_pos, leng


def charfinder(lista):
    """
    Tries to find same letters within cookie value, on same index.

    Args:
        lista: list of cookie values

    """
    minlen = min([len(word) for word in  lista])
    sames = []
    for i in range(minlen):
        sames.append(all([ x[i] == lista[0][i] for x in  lista]))
    same = []
    for i in range(minlen):
        same.append(lista[0][i] if sames[i] else " ")
    return "".join(same)

def main(site, num, logindata=None, typee=None):
    """
    Main function.
    """
    strtim = str(int(time.time()))
    ct.puts(ct.colored.green("Cookieget, gotta check em all!"))
    ct.puts("Checking for {} ,{} cookies.".format(
        ct.colored.green(site),
        ct.colored.green(num)
        ))
    raw_list = cookieget(site, int(num), logindata, typee)
    try:
        dicc = dictify_cookies(raw_list)
    except IndexError, _:
        raise NoCookies()
    print "\n"
    for i in dicc.keys():
        ct.puts("Cookie val: ")
        print draw_cookies(i, dicc[i])
        sames = charfinder(dicc[i])
        ct.puts("Shared letters amongst all values:")
        print ct.colored.green(sames)

        loc, how_much = findtimestamp(dicc[i], strtim)
        if how_much > 7:
            ct.puts("Possible timestamp at index {}.".format(loc))
            ct.puts(ct.colored.green(
                    " "*(loc+2)+strtim[:how_much]).color_str)
        ldist = levdis(dicc[i])
        ct.puts("Average Levenshtein disance between all cookies: {}"\
                .format(ldist))
        avg_len = reduce(lambda x, v: (x + v)/2.0,
                [ len(cookie_val) for cookie_val in dicc[i]])
        sighash = ldist/avg_len*100
        ct.puts("Chance of hashed/encrpyted/randomdata cookie ~{}%".\
                format(sighash))
        print "\n\n"


if __name__ == '__main__':
    try:
        if len(argv)-1==4:
            main(argv[1], argv[2], argv[3], argv[4])
        else:
            main(argv[1], argv[2], None, None)
    except IndexError as erro:
        ct.puts_err(ct.colored.red("Use the source, Luke!"))
        print erro
        exit(1)
    except NoCookies as  erro:
        ct.puts_err(ct.colored.red("Returned 0 cookies."))
        print erro
        exit(1)
    except Exception as erro:
        print erro
        exit(1)
    finally:
        exit(0)
