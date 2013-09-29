#cookieget.py

Cookie checking utility with some basic heuristics, like [Levenshtein distance](http://en.wikipedia.org/wiki/Levenshtein_distance), timestamp recognition, trivial checkup of delimitors and check for hashed/encrypted cookie. 

## Usage

Without login, just do

python cookieget.py [url] [num of cookies]

First cookie:

![gmail.com](http://i.imgur.com/SpgN5BA.png)


Second Cookie:

![gmail.com cont](http://i.imgur.com/QGnIi9L.png)


With login,

python cookieget.py [login form url] [num of cookies] [data] [type (json/post)]

![reddit.com](http://i.imgur.com/WHhkgfA.png?0)\

## License

[MIT](http://www.opensource.org/licenses/MIT)
