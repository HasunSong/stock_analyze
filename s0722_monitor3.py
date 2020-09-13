# http://blog.samstdio.com/scheduling-in-python-apcheduler/
# %%
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


# main code
def runner():
    print(f'{datetime.now()}:runner')


sched = BlockingScheduler()

# main job
runner_job = sched.add_job(runner, 'interval', seconds=10)

# start job
def start_runner():
    print(f'{datetime.now()}:start_runner')
    runner_job.resume()

# stop job
def stop_runner():
    print(f'{datetime.now()}:stop_runner')
    runner_job.pause()

# to delay main job
stop_runner()

# schedules for main job
sched.add_job(start_runner, 'cron', minute='1,11,21,31,41,51')
sched.add_job(stop_runner, 'cron', minute='5,15,25,35,45,55')

sched.start()