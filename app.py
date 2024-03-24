from io import BytesIO
from flask import Flask, render_template, send_file
from matplotlib.figure import Figure
from get_dht11_konfig_data import get_konfig_data
import paho.mqtt.publish as publish
import base64


app = Flask(__name__)

@app.route('/background-image')
def background_image():
    return send_file('static/radiator.jpg', mimetype='image/jpg')

def konfig_temp():
    datetimes, temp = get_konfig_data(10)
    fig = Figure()
    ax = fig.subplots()
    fig.subplots_adjust(bottom=0.3)
    ax.tick_params(axis='x', which='both', rotation=30)
    ax.set_facecolor("#fff")
    ax.plot(temp, datetimes, linestyle = "dashed", c="#11f", linewidth = "2.5", marker ="o", mec='black', mfc="white")
    ax.set_xlabel("Timestamps")
    ax.set_ylabel("Temperature Celsius")
    fig.patch.set_facecolor("#fff")
    ax.tick_params(axis="x",colors="blue")
    ax.tick_params(axis="y",colors="blue")
    ax.spines['left'].set_color("blue")
    ax.spines['right'].set_color("blue")
    ax.spines['top'].set_color("blue")
    ax.spines['bottom'].set_color("blue")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/temperatur')
def temperatur():
    temperatur_temperature = konfig_temp()
    return render_template('temperatur.html', temperatur_temperature = temperatur_temperature)

@app.route('/konfiguration')
def konfiguration():
    return render_template('konfiguration.html')

@app.route('/auto/', methods=['POST'])
def auto():
    publish.single("auto", "auto", hostname="68.219.252.196")
    return render_template('konfiguration.html')

@app.route('/knap_0/', methods=['POST'])
def knap_0():
    publish.single("knap_2", "0", hostname="68.219.252.196")
    return render_template('konfiguration.html')

@app.route('/knap_1/', methods=['POST'])
def knap_1():
    publish.single("knap_2", "1", hostname="68.219.252.196")
    return render_template('konfiguration.html')

@app.route('/knap_2/', methods=['POST'])
def knap_2():
    publish.single("knap_2", "2", hostname="68.219.252.196")
    return render_template('konfiguration.html')

@app.route('/knap_3/', methods=['POST'])
def knap_3():
    publish.single("knap_2", "3", hostname="68.219.252.196")
    return render_template('konfiguration.html')


app.run(debug=True)