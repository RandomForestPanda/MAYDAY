import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import bcrypt
import psutil

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rootpwd'
app.config['MYSQL_DB'] = 'creddb'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # Get form data
    username = request.form['username']
    password = request.form['password']
    
    if authenticate_candidate_login(username, password):
        # Run the required commands when authentication is successful
        run_commands()
        return render_template('index.html')
    else:
        flash("Invalid credentials, please try again.")
        return redirect(url_for('home'))

@app.route('/go_to_checklist', methods=['GET'])
def go_to_checklist():
    # Redirect to Streamlit app when the Flight Assistant button is clicked
    return redirect("http://localhost:8503")

@app.route('/go_to_weather', methods=['GET'])
def go_to_weather():
    # Redirect to Streamlit app when the Flight Assistant button is clicked
    return redirect("http://localhost:8504")

@app.route('/go_to_hazard_alert', methods=['GET'])
def go_to_hazard_alert():
    # Redirect to Streamlit app when the Flight Assistant button is clicked
    return redirect("http://localhost:8505")

@app.route('/go_to_nav_sim', methods=['GET'])
def go_to_nav_sim():
    # Redirect to Streamlit app when the Flight Assistant button is clicked
    return redirect("https://hackathon-ten-indol.vercel.app/")

# Function to authenticate login credentials
def authenticate_candidate_login(username, password):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM credtable WHERE User = %s", (username,))
    user = cursor.fetchone()

    if user:
        stored_hashed_password = user[1]
            
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            return True  # Password is correct
        else:
            return False  # Password is incorrect
    else:
        return False  # User not found



def free_ports():
    # List of ports to check and free
    ports = [8001, 8002, 8503, 8504, 8505]

    for port in ports:
        # Check if any process is using the port
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port:
                pid = conn.pid
                try:
                    process = psutil.Process(pid)
                    print(f"Process {process.name()} (PID {pid}) is using port {port}. Killing it...")
                    process.terminate()  # Terminate the process
                    process.wait()  # Wait for the process to terminate
                except psutil.NoSuchProcess:
                    print(f"Process with PID {pid} not found.")
                except psutil.AccessDenied:
                    print(f"Access denied to terminate process with PID {pid}.")
                except Exception as e:
                    print(f"Error while terminating process {pid}: {e}")

def run_commands():
    try:
        # Free the ports first
        free_ports()

        # Run uvicorn and Streamlit commands after freeing the ports
        subprocess.Popen(["uvicorn", "checklist_server:app", "--host", "0.0.0.0", "--port", "8001"])
        subprocess.Popen(["uvicorn", "accident_report_server:app", "--host", "0.0.0.0", "--port", "8002"])
        subprocess.Popen(["streamlit", "run", "checklist_front.py", "--server.port=8503", "--server.headless=true"])
        subprocess.Popen(["streamlit", "run", "weather_front.py", "--server.port=8504", "--server.headless=true"])
        subprocess.Popen(["streamlit", "run", "accident_report_front.py", "--server.port=8505", "--server.headless=true"])

    except Exception as e:
        print(f"Error while running the commands: {e}")


if __name__ == '__main__':
    app.run(debug=True)
