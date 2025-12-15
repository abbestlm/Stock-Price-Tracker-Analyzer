from flask import Flask, jsonify, request, send_from_directory
from flask_caching import Cache
from polygon import RESTClient
import datetime

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Replace with your Polygon.io API key
api_key = 'your_polygon_api_key_here'

# Initialize the Polygon client
client = RESTClient(api_key)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/stock_prices')
@cache.cached(timeout=3600, query_string=True)
def stock_prices():
    ticker = request.args.get('ticker', '').upper()
    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        end_date = datetime.date.today() - datetime.timedelta(days=1)
        start_date = end_date - datetime.timedelta(days=30)

        aggs = client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan='day',
            from_=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d'),
            limit=5000
        )

        if aggs:
            stock_data = [{
                'date': datetime.datetime.fromtimestamp(agg.timestamp / 1000).strftime('%Y-%m-%d'),
                'open': agg.open,
                'close': agg.close,
                'high': agg.high,
                'low': agg.low,
                'volume': agg.volume
            } for agg in aggs]

            return jsonify({ticker: stock_data})
        else:
            return jsonify({'error': 'No data found for ticker'}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
