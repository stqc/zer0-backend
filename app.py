from flask import Flask
from flask import jsonify
from config import abc

app = Flask(__name__)

@app.route('/api/v1/get_all_tokens', methods=['GET'])
def get_all_tokens():
    return jsonify([
            {
                'name':'BTC',
                'logo':'https://s2.coinmarketcap.com/static/img/coins/64x64/1.png',
                'address':'0x1e0d871472973c562650e991ed8006549f8cbefc'
            },
            {
                'name':'ETH',
                'logo':'https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png',
                'address':'0xce830D0905e0f7A9b300401729761579c5FB6bd6'
            },
            {
                'name':'USDT',
                'logo':'https://s2.coinmarketcap.com/static/img/coins/64x64/825.png',
                'address':'0x9A87C2412d500343c073E5Ae5394E3bE3874F76b'
            },
            {
                'name':'WA0GI',
                'logo':'https://avatars.githubusercontent.com/u/139951901?v=4',
                'address':'0x493eA9950586033eA8894B5E684bb4DF6979A0D3'
            }
        ]
    )

@app.route('/api/v1/perform_action', methods=['POST'])
def perform_action():
    # do calculation for the points of every action here
    return jsonify({'status':'success', 'message':'Action performed successfully'})



if __name__ == '__main__':
    app.run(host='0.0.0.0')