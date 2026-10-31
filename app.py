from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from benchmark import run_comparison
from language import LanguageError
import csv, io, json, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-key-change-me")

SAMPLES = {
    "Arithmetic": "a = 10; b = 20; c = a + b * 2; print(c);",
    "If-else": "x = 12; if (x > 10) { print(1); } else { print(0); }",
    "While loop": "i = 0; sum = 0; while (i < 5) { sum = sum + i; i = i + 1; } print(sum);",
    "Boolean short-circuit": "x = 0; if (x != 0 && 10 / x > 1) { print(1); } else { print(0); }",
    "Combined": "n = 5; fact = 1; while (n > 1) { fact = fact * n; n = n - 1; } print(fact);"
}

@app.get("/")
def index():
    sample_name = request.args.get("sample", "Arithmetic")
    source = SAMPLES.get(sample_name, SAMPLES["Arithmetic"])
    return render_template("index.html", source=source, samples=SAMPLES, selected=sample_name, result=None, error=None)

@app.post("/run")
def run():
    source = request.form.get("source", "")
    try:
        result = run_comparison(source)
        return render_template("index.html", source=source, samples=SAMPLES,
                               selected="", result=result, error=None)
    except Exception as exc:
        return render_template("index.html", source=source, samples=SAMPLES,
                               selected="", result=None, error=str(exc))

@app.post("/export")
def export():
    raw = request.form.get("payload", "")
    try:
        data = json.loads(raw)
    except Exception:
        flash("No valid comparison result to export. Run a program first.")
        return redirect(url_for("index"))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Path", "Lexical analysis (ms)", "Parsing (ms)", "Translation (ms)", "Execution (ms)", "Total (ms)", "Instruction count", "Output"])
    for key, label in [("interpreter", "Interpreter"), ("vm", "Compiler + VM")]:
        r = data[key]
        writer.writerow([label, r["lex_ms"], r["parse_ms"], r["translation_ms"],
                         r["execution_ms"], r["total_ms"], r["instruction_count"],
                         " | ".join(r["output"])])
    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="comparison_report.csv")

@app.get("/batch")
def batch():
    rows = []
    for name, source in SAMPLES.items():
        try:
            rows.append({"name": name, "result": run_comparison(source), "error": None})
        except Exception as exc:
            rows.append({"name": name, "result": None, "error": str(exc)})
    return render_template("batch.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
