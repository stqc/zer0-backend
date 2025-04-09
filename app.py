from flask import Flask, request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import datetime
import os
from web3 import Web3
from dotenv import load_dotenv
from config import validate_transaction
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin


load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ.get('WEB3_PROVIDER_URI')))

FACTORY = os.environ.get('FACTORY').lower()
ROUTER = os.environ.get('ROUTER').lower()
MULTI=os.environ.get('MULTI').lower()
NFTPOSITIOM=os.environ.get('NFTPOSITIOM').lower()
QUOTER=os.environ.get('QUOTER').lower()

app = Flask(__name__)

base = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base,"points.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'timeout': 15}}
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)
Migrate(app, db)

class Points(db.Model):
    address = db.Column(db.String(255), primary_key=True)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Points {self.address}: {self.points}>'
    
    def __init__(self, address):
        self.address = address
    

with app.app_context():
    db.create_all()
    db.session.execute(text("PRAGMA journal_mode=WAL"))
    db.session.execute(text("PRAGMA busy_timeout=5000"))
    db.session.commit()




@app.route('/api/v1/get_all_tokens', methods=['GET'])
@cross_origin()
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
@cross_origin()
def perform_action():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    if 'tx_hash' not in data:
        return jsonify({'error': 'Transaction hash is required'}), 400
    
    tx_hash = data['tx_hash'].lower()
    
    is_valid, error_message, sender_address = validate_transaction(tx_hash,w3,[FACTORY,ROUTER,MULTI,NFTPOSITIOM,QUOTER])
    
    if not is_valid:
        return jsonify({'error': error_message}), 400
    
    try:
        db.session.execute(
            text("""
                INSERT INTO points (address, points) 
                VALUES (:address, 1)
                ON CONFLICT(address) DO UPDATE SET 
                points = points + 1
                RETURNING points
            """),
            {"address": sender_address}
        )
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
        }), 200
    
    except SQLAlchemyError as e:
        # Rollback on error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/get_points/<address>', methods=['GET'])
@cross_origin()
def get_points(address):
    address = address.lower()
    record = Points.query.filter_by(address=address).first()
    
    if not record:
        return jsonify({'address': address, 'points': 0}), 200
    
    return jsonify({'address': address, 'points': record.points}), 200

@app.route('/api/v1/leaderboard', methods=['GET'])
@cross_origin()
def leaderboard():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    top_records = Points.query.order_by(Points.points.desc()).offset(offset).limit(limit).all()

    total_count = Points.query.count()
    
    result = [{'address': record.address, 'points': record.points} for record in top_records]
    
    return jsonify({
        'result':result,
        'pagination': {
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }
    }), 200


if __name__ == '__main__':
    print("goodbye world")
    app.run(host='0.0.0.0')