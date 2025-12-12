from flask import Flask, render_template, request
import markwise

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    #default
    max_results = 5

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        query_type = request.form.get("query_type")

        max_results = int(request.form.get("max_results", max_results))

        if not query:
            return render_template("index.html", error="Please enter some text.")

        # Call the correct function based on type
        if query_type == "book":
            raw_results = markwise.search_books(query, max_results)
            results = markwise.process_books_for_display(raw_results, query)
        elif query_type == "song" or query_type == "lyrics":
            raw_results = markwise.search_spotify(query, max_results)
            results = markwise.process_spotify_for_display(raw_results, query)
        else:
            results = []

        return render_template("results.html",
                               query=query,
                               query_type=query_type,
                               results=results,
                               max_results=max_results)
    return render_template("index.html",
                           max_results=max_results)
