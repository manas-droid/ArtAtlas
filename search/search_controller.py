from flask import Flask, jsonify, request
from .user_query_search_service import find_top15_relevant_results

app = Flask(__name__)


@app.route('/api/search', methods=['GET'] )
def get_relevant_search_response():

    query:str = request.args.get('q')
    
    response = find_top15_relevant_results(query)

    if len(response['results']) == 0:
        return jsonify(response), 404


    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)