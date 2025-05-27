from flask import Flask

#Create an instance of the Flask application
app = Flask(__name__)

#Define a route '/config' that simulates an internal configuration endpoint
#when accessed, it returns a fake internal database password as a string
@app.route('/config')
def config():
    return "Internal config: DB_PASS=supersecret123"

#DEfine another route '/admin/secret' to simulate a sensitive internal admin endpoint
#When accessed, it returns a fake secret flag (used for demonstrating SSRF data leakage)
@app.route('/admin/secret')
def admin_secret():
    return "Top Secret: Flag{internal_data_leakage}"

#Run the Flask app inly if this script is executed directly
#The app will listen on port 8000, simulating a service on the internal network
if __name__ == '__main__':
    app.run(port=8000)
