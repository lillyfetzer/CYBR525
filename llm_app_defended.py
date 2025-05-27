# llm_app_defended.py
from flask import Flask, request, render_template_string
import requests
from transformers import pipeline
from urllib.parse import urlparse

#initialize Flask app
app = Flask(__name__)

#Load a pre-trained summarization pipeline (default: DistilBART)
summarizer = pipeline("summarization")

#Load a pre-trained summarization pipeline (default: DistilBART)
HTML = '''
<h2>LLM Summarizer (DEFENDED)</h2>
<form action="/" method="post">
  <input name="url" placeholder="Enter a URL to summarize"><br>
  <input name="user_prompt" placeholder="Optional: Add custom instruction"><br>
  <button type="submit">Summarize</button>
</form>
<p><strong>Summary:</strong> {{ summary }}</p>
'''

# SSRF Defense: Check if the supplied URL points to localhost or internal IPs
def is_internal(url):
    parsed = urlparse(url)
    hostname = parsed.hostname

    #common internal/loopback hostnames
    return hostname in ['127.0.0.1', 'localhost', '::1']

# Prompt Injection Defense: Detect known malicious prompt phrases
def prompt_is_malicious(prompt):
    blacklist = ["ignore previous", "disregard", "instead", "output", "override", "you are a"]
    #case-insensitive keyword match
    return any(term in prompt.lower() for term in blacklist)

#Define the root route ("/") which handles both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def summarize():
    #Default summary output is empty
    summary = ""
    if request.method == 'POST':
        url = request.form['url']
        user_prompt = request.form.get('user_prompt', '').strip()

        # SSRF Protection
        if is_internal(url):
            return render_template_string(HTML, summary="Blocked: Internal access not allowed.")

        # Prompt Injection Protection (basic)
        if prompt_is_malicious(user_prompt):
            return render_template_string(HTML, summary="Blocked: Unsafe prompt detected.")

        try:
            # Fetch the content of the provided URL (with a timeout)
            text = requests.get(url, timeout=3).text[:1024]
            # Build the input for the summarizer: include prompt if provided
            full_prompt = f"{user_prompt}\n\nSummarize this text:\n{text}" if user_prompt else text
            # Run the summarizer and extract the generated summary text
            summary = summarizer(full_prompt)[0]['summary_text']
        except Exception as e:
            summary = f"Error: {e}"
    # Render the HTML form and display the result
    return render_template_string(HTML, summary=summary)

# Run the Flask app on port 5000 when executed directly
if __name__ == '__main__':
    app.run(port=5000)
