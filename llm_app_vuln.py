from flask import Flask, request, render_template_string
import requests
from transformers import pipeline

# Initialize the Flask application
app = Flask(__name__)

# Load a pre-trained summarization pipeline (default: DistilBART)
summarizer = pipeline("summarization")

# HTML template for a simple web form
# Now includes a second input for custom prompt injection
HTML = '''
<h2>LLM Summarizer (VULNERABLE)</h2>
<form action="/" method="post">
  <input name="url" placeholder="Enter a URL to summarize"><br>
  <input name="user_prompt" placeholder="Optional: Add custom instruction"><br>
  <button type="submit">Summarize</button>
</form>
<p><strong>Summary:</strong> {{ summary }}</p>
'''

# Define the root route ("/") which handles both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def summarize():
    # Default summary output is empty
    summary = ""
    
    if request.method == 'POST':
        # Extract the submitted URL and optional user prompt from the form
        url = request.form['url']
        user_prompt = request.form.get('user_prompt', '').strip()

        try:
            # Send a GET request to the user-supplied URL and extract text content
            text = requests.get(url).text[:1024]  # Truncate to avoid overly long inputs

            # Combine user prompt and text content into one prompt for the LLM
            # This makes the model vulnerable to prompt injection
            full_input = f"{user_prompt}\n\nSummarize this text:\n{text}" if user_prompt else text

            # Generate the summary using the transformer pipeline
            summary = summarizer(full_input)[0]['summary_text']

        except Exception as e:
            # If an error occurs (e.g., bad URL or request failure), show the error
            summary = f"Error: {e}"

    # Render the HTML form and show the summary result
    return render_template_string(HTML, summary=summary)

# Run the Flask app on port 5000 if the script is executed directly
if __name__ == '__main__':
    app.run(port=5000)
