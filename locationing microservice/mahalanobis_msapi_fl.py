from flask import jsonify, Flask
from process_readings import *

import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

curtime = ""

# the function to be schduled
def update_date_time():
    global curtime
    t = time.strftime("%A, %d. %B %Y %I:%M:%S %p")
    print(t)
    curtime = t


app = Flask(__name__)


@app.route("/")
def example():
    return jsonify({"status": "ok", "time": curtime})

@app.route('/l/', methods = ['POST'])
def locate_using_mahalanobis():
    return jsonify({"main": "test"})


if __name__ == '__main__':
    redis_host = '10.0.0.5'
    redis_pw = "1048576"

    # setup the redis client to access the recordings
    setup_redis_client(redis_host, redis_pw)
    
    # setup the scheduler for interval tasks
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_date_time, trigger="interval", seconds=10)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    app.run(debug=True, port=5009)