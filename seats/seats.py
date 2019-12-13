#export FLASK_APP=restroom.py
#python3 -m flask run --host=0.0.0.0

import json
import urllib
import time
from flask import Flask
from flask import Response
from flask import request
import random

app = Flask(__name__)

hat = [
    'Todd',
    'Dave',
    'Ashok',
    'Brian',
    'Tom',
    'Daniel',
    'Ben',
    'Kaitlyn',
    'Carol',
    'Leif',
    'Travis',
#    'Kexin',
    'Bhalchandra',
    'Josh',
    'Mario',
    'Skyler'
]

cache = {}

cache['seats'] = ['     0     ',
                  '     1     ',
                  '     2     ',
                  '     3     ',
                  '     4     ',
                  '     5     ',
                  '     6     ',
                  '     7     ',
                  '     8     ',
                  '     9     ',
                  '    10     ',
                  '    11     ',
                  '    12     ',
                  '    13     ',
                  '    14     ',
                  '    15     ',
                  '    16     ',
                  '    17     ',
                  '    18     ']
cache['shuffled'] = False
cache['shuffle'] = {}
common = {}
common['_links'] = {
        'seats': {
            'href':'http://172.17.181.226:5000/seats',
            'method' : 'GET'
        },
        'select_seat': {
            'href': 'http://172.17.181.226:5000/seats?name={name}&seat={seat}',
            'method': 'PUT',
            'templated': 'true :D'
        },
        'delete_seats': {
            'href': 'http://172.17.181.226:5000/seats',
            'method': 'DELETE'
        },
        # 'shuffle': {
        #     'href': 'http://172.17.181.226:5000/seats/shuffle',
        #     'method': 'POST'
        # },
        'clear_shuffle': {
            'href': 'http://172.17.181.226:5000/seats/shuffle/clear',
            'method': 'POST'
        },
        'clear_seat': {
            'href': 'http://172.17.181.226:5000/seats?name={currently_assigned_name}&seat={seat_to_clear}',
            'method': 'PUT',
            'templated': 'true :D'
        }
}

def choose_seat(name, seat):
    seats = cache['seats']
    seats[seat] = name
    cache['seats'] = seats

@app.route('/seats/links', methods = ['GET'])
def getLinks():
    body = {'_links' : common['_links']}
    return Response(json.dumps(body), status=200, mimetype='application/json')


@app.route('/seats/shuffle/clear', methods = ['POST'])
def clearShuffled():
    resp = {
            '_links' : common['_links']
        }

    cache['shuffled'] = False
    cache['shuffle'] = {}
    return Response(json.dumps(resp,indent=4), status=200, mimetype='application/json')

@app.route('/seats', methods = ['DELETE'])
def clear():
    cache['seats'] = ['   0   ', '   1   ', '   2   ', '   3   ', '   4   ', '   5   ', '   6   ', '   7   ', '   8   ','   9   ', '   10   ', '   11   ', '   12   ']
    return Response(status=204)

@app.route('/seats/shuffle', methods = ['POST'])
def shuffle():
    if cache['shuffled'] == True:
        return cache['shuffle']
        # resp = {
        #     'error': 'the order has already been determined you cheater!!',
        #     'order': hat,
        #     '_links' : common['_links']
        # }
        #
        # return Response(json.dumps(resp,indent=4), status=409, mimetype='application/json')
    shuffled = {}

    for i in range(50):
        random.shuffle(hat)

    for i in range(len(hat)):
        shuffled[i] = hat[i]

    resp = {
        'order': shuffled,
        '_links' : common['_links']
    }

    j = json.dumps(resp, indent=4, sort_keys=False)
    #
    # resp = Response(j, status=200, mimetype='application/json')
    cache['shuffled'] = True
    cache['shuffle'] = j
    return cache['shuffle']

@app.route('/seats', methods = ['GET'])
def seats():

    bstring = drawString()
    bstring = bstring + '\n'
    bstring = bstring + '\n' + shuffle() + '\n'
    # bstring = bstring + json.dumps({'_links' : common['_links']}, indent=4, sort_keys=True)
    bstring = bstring + '\n'
    resp = Response(bstring, status=200, mimetype='text/plain')

    return resp

@app.route('/seats', methods = ['PUT'])
def selectSeat():
    name = request.args.get('name')
    seat = int(request.args.get('seat'))
    clear = request.args.get('clear')
    if (seat > len(cache['seats']) - 1):
        error = {'error' : 'the seat ' + str(seat) + ' deos not exist! you must choose another seat!', '_links' : common['_links']}
        return Response(json.dumps(error), status=400, mimetype='application/json')
    tmp = cache['seats']
    y = tmp[seat].strip()
    if (clear == 'true'): #and y.lower() == name.lower()):
        formatted = str(seat)
        while len(formatted) != 11:
            if len(formatted) > 11:
                temp = formatted
            elif len(formatted) < 11:
                formatted = formatted + ' '
        cache['seats'][seat] = formatted
        return seats() # Response(drawString(), status=200, mimetype='text/plain')
    nums = []
    names = []
    for s in tmp:
        x = s.strip()
        if (len(x) <= 2):
            i = int(x)
            nums.append(i)
        else:
            names.append(x.lower())

    if name.lower() in names:
            error = {'error' : name + ' already has a seat! be happy with you seat! or use &clear=true', '_links' : common['_links']}
            return Response(json.dumps(error), status=409, mimetype='application/json')

    if seat not in nums:
            error = {'error' : 'seat ' + str(seat) + ' is already taken! you must choose another seat!', '_links' : common['_links']}
            return Response(json.dumps(error), status=409, mimetype='application/json')

    choose_seat(name, seat)
    return seats()


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/hello', methods = ['GET'])
def api_hello():
    data = {
        'hello'  : 'world'
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')

    return resp




def drawString():
    board = cache['seats']
    for i in range(len(board)):
        while len(board[i]) != 11:
            if len(board[i]) > 11:
                tmp = board[i]
                board[i] = tmp[:11]
            elif len(board[i]) < 11:
                board[i] = board[i] + ' '

    justify = '          '
    justifyLeft = '                  '
    front_door = '\n       |front_door|\n'

    #horizontal row, pod one
    boardString = front_door
    boardString = boardString + '\n' + justifyLeft + '|' + board[1] + '|' + board[2] + '|' + board[3] + '|'
    boardString = boardString + '\n' + justifyLeft + ' -----------------------------------'
    boardString = boardString + '\n' + justifyLeft + '|' + board[4] + '|' + board[5]+ '|' + board[6] + '|'
    boardString = boardString + '\n\n'

    # #vertical rows, podes 2 and 3
    boardString = boardString + '\n' + justifyLeft + '|' + board[7] + '|' + board[10] + '|' + justify + '|' + board[13] + '|' + board[16] + '|'
    boardString = boardString + '\n' + justifyLeft + ' -----------------------' + justify  + '  -----------------------'
    boardString = boardString + '\n' + justifyLeft + '|' + board[8] + '|' + board[11] + '|' + justify + '|' + board[14] + '|' + board[17] + '|'
    boardString = boardString + '\n' + justifyLeft + ' -----------------------' + justify  + '  -----------------------'
    boardString = boardString + '\n' + justifyLeft + '|' + board[9] + '|' + board[12] + '|' + justify + '|' + board[15] + '|' + board[18] + '|'

    boardString = boardString + '\n\n|back_door|\n'
    return boardString

#print(drawString())

if __name__ == '__main__':
    app.run(host='0.0.0.0')

