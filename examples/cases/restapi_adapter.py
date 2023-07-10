from flask import Flask, jsonify, request
from schema import MainPage

app = Flask(__name__)


@app.route("/parse_html", methods=["POST"])
def parse_html():
    html_doc = request.data  # Assuming the HTML document is sent in the request body
    # Parse the HTML document using BeautifulSoup
    data = MainPage(html_doc.decode("utf8")).dict()

    response = {"status": 200, "data": data}
    return jsonify(response)


if __name__ == "__main__":
    app.run()
