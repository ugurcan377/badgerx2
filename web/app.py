from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from honey_engine.engine import HoneyEngine

app = Flask(__name__)
engine = HoneyEngine()

@app.route("/")
def index():
    return render_template("main.html")


@app.route('/search')
def search():
    query_str = request.args.get('query', '')
    print(query_str)
    if not query_str:
       return redirect('/')
    results = engine.execute_query(query_str)
    return render_template("results.html", results=results, query=query_str)


@app.route('/document/<doc_id>')
def document(doc_id):
    query_str = request.args.get('query', '')
    title, content = engine.get_document(doc_id, query_str)
    return render_template("document.html", query=query_str, title=title, content=content)


app.run(debug=True)