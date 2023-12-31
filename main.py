import os
import threading
import streamlit as st
from utils import whatsapp as wa
from utils.database import init_app, db_sqlalchemy
from flask import Flask, request, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy

 

# ======= STREAMLIT =======

def run_streamlit():
    port_streamlit = 8500
    print (f"Running streamlit on {port_streamlit} ...")
    os.system(f"streamlit run Menu.py --server.port {port_streamlit}")
threading.Thread(target=run_streamlit).start()





# ======= FLASK =======
# db_sqlalchemy = SQLAlchemy()


app = Flask(__name__)
init_app(app)


@app.route('/')
def home():
    url = 'http://localhost:8500'
    return render_template('index.html', url=url)


# Fungsi untuk akses ke file gambar
@app.route('/images/<filename>')
def send_image(filename):
    return send_from_directory('static/images', filename)


# Fungsi untuk webhook incoming messages
@app.route("/webhook", methods=['POST'])
def webhook():
    # print("Incoming message")
    try:
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                # print(str(data))
                wa.handle_incoming_message(data)
                # handle_incoming_message(data)
                return '', 200
            else:
                return 'Unsupported Media Type', 415
    except Exception as e:
        print(f"Error: {e}")
        return 'Internal Server Error', 500



def run_flask():
    #app.run(port=5000)
    port_flask = 5000
    print(f"Running on port {port_flask} ...")
    app.run(host='0.0.0.0', port=port_flask, debug=False, use_reloader=False)



threading.Thread(target=run_flask).start()