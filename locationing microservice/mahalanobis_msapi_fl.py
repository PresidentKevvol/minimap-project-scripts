from flask import jsonify, Flask
from process_readings import *

import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

# current time as a string
curtime = ""
# the beacons' readings compiled into covariance matrices/mean vectors
# used for calculations
beacons_cov = None
beacons_mean = None
matrix_indices = None

# the function to be schduled
def update_date_time():
    global curtime
    t = time.strftime("%A, %d. %B %Y %I:%M:%S %p")
    #print(t)
    curtime = t

def update_statistical_matrices():
    global beacons_cov, beacons_mean, matrix_indices
    readings = get_all_beacon_readings()
    beacons_cov, beacons_mean, matrix_indices = extract_readings_stats(readings)


app = Flask(__name__)


@app.route("/")
def example():
    return jsonify({"status": "ok", "time": curtime})

@app.route('/l/', methods = ['POST', 'GET'])
def locate_using_mahalanobis():
    return jsonify({"main": "test"})

@app.route('/tds/', methods = ['GET'])
def test_get_datastructures():
    return jsonify({"indices": matrix_indices, "mean_vectors": {k:beacons_mean[k].tolist() for k in beacons_mean}, "covariance_matrices": {k:beacons_cov[k].tolist() for k in beacons_cov}})


if __name__ == '__main__':
    redis_host = '10.0.0.5'
    redis_pw = "1048576"

    # setup the redis client to access the recordings
    setup_redis_client(redis_host, redis_pw)
    
    # setup the scheduler for interval tasks
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_date_time, trigger="interval", seconds=10)
    scheduler.add_job(func=update_statistical_matrices, trigger="interval", seconds=10)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    app.run(debug=True, port=5009)