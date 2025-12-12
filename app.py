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

@app.route("/export", methods=["POST"])
def export():
    query = request.form.get("query")
    query_type = request.form.get("query_type")
    max_results = int(request.form.get("max_results", 5))

    # Get results again
    if query_type == "book":
        raw_results = markwise.search_books(query, max_results=max_results)
        results = markwise.process_books_for_display(raw_results, query)
    elif query_type in ["song", "lyrics"]:
        raw_results = markwise.search_spotify(query, limit=max_results)
        results = markwise.process_spotify_for_display(raw_results, query)
    else:
        results = []

    # Build HTML content for the report
    report_html = f"""
    <!doctype html>
    <html>
    <head>
        <title>Mark-Wise Report for {query}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ text-align: center; }}
            .result {{ border: 1px solid #ccc; padding: 10px; margin: 5px 0; }}
            mark {{ background-color: yellow; }}
        </style>
    </head>
    <body>
        <h1>Mark-Wise Report for "{query}"</h1>
    """

    for r in results:
        if query_type == "book":
            report_html += f"""
            <div class="result">
                <strong>{r['title']}</strong> by {r['authors']}<br>
                Similarity: {r['similarity']}%<br>
                Highlighted: {r['highlight']}<br>
                <a href="{r['infoLink']}" target="_blank">Book link</a>
            </div>
            """
        else:
            report_html += f"""
            <div class="result">
                <strong>{r['title']}</strong> by {r['artists']}<br>
                Similarity: {r['similarity']}%<br>
                Highlighted: {r['highlight']}<br>
                <a href="{r['spotify_url']}" target="_blank">Spotify link</a>
            </div>
            """

    report_html += "</body></html>"

    # Return as a downloadable file
    response = make_response(report_html)
    response.headers["Content-Disposition"] = f"attachment; filename=markwise_report_{query}.html"
    response.headers["Content-Type"] = "text/html"
    return response

