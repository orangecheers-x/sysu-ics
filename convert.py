import ics
import requests
import time
import json
import datetime
import os


def parse_data(x: str):
    splited = x.split(";;")
    ans = {}
    for i in splited:
        ti = i.split(":")
        if len(ti) != 2:
            continue
        ans[ti[0]] = ti[1]
    return ans


# 在这里设置cookie
cookie = ""

if cookie == "":
    cookie = os.environ.get("COOKIE")

# example: (肯定是不能用的)
# cookie = "LYSESSIONID=f4f175ff-e432-435n-b93e-7y653edf00fc; user=fjdkenakclxmdnghbcialcnxma63hdz9ftmn84han04adxa34fawibmFtZSI6Iuefs+a9hyIsImxvZ2luUGF0dGVyfjaudxlaneblndxl46hgndkuhanxjsl8fhandlxh5"

# 设置学期和开学日期
semester = "2023-2"
start_day = "2024-02-26"

url = "https://cms.sysu.edu.cn/start-class/classTableInfo/selectStudentClassTable"

from_week = 1
to_week = 21
for i in range(from_week, to_week):
    res = requests.get(url, headers={
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"
    }, params={
        "code": "byytjsd_jskbcx_week_query",
        "academicYear": semester,
        "weekly": i
    })
    if res.status_code != 200:
        print("抓取失败, 请检查cookie是否正确")
        exit(1)
    os.makedirs("data", exist_ok=True)
    with open("data/{}.json".format(i), "w") as f:
        f.write(res.text)
    print("grab {}.json".format(i))
    time.sleep(1)

weeks = [
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]

course_time = [
    ("08:00:00", "08:45:00"),
    ("08:55:00", "09:40:00"),
    ("10:10:00", "10:55:00"),
    ("11:05:00", "11:50:00"),
    ("14:20:00", "15:05:00"),
    ("15:15:00", "16:00:00"),
    ("16:30:00", "17:15:00"),
    ("17:25:00", "18:10:00"),
    ("19:00:00", "19:45:00"),
    ("19:55:00", "20:40:00"),
    ("20:50:00", "21:35:00"),
]

cal = ics.Calendar()
tz = datetime.timezone(datetime.timedelta(hours=8))

for i in range(from_week, to_week):
    st = datetime.datetime.fromisoformat(
        start_day) + (i-1) * datetime.timedelta(days=7)
    st = st.replace(tzinfo=tz)
    kb = [[None for i in range(7)] for j in range(11)]
    obj = json.load(open("data/{}.json".format(i)))
    for j in obj['data']:
        for k in range(7):
            if weeks[k] not in j.keys():
                continue
            kb[j['section']-1][k] = parse_data(j[weeks[k]])
    # print(kb)
    for j in range(7):
        current_day = st + j * datetime.timedelta(days=1)
        is_first = True
        la = 0
        for k in range(11):
            if kb[k][j] is None:
                la += 1
                continue
            if is_first:
                la = k
                is_first = False
            if k in [3, 7, 10] or kb[k+1][j] == None or kb[k+1][j]['kcmc'] != kb[k][j]['kcmc']:
                print("wk", i, "day", weeks[j], kb[k][j]['kcmc'], la, k)
                event = ics.Event()
                event.name = kb[k][j]['kcmc']
                (hour, minute) = list(
                    map(int, course_time[la][0].split(":")[0:2]))
                event.begin = current_day.replace(
                    hour=hour, minute=minute)
                (hour, minute) = list(
                    map(int, course_time[k][1].split(":")[0:2]))
                event.end = current_day.replace(
                    hour=hour, minute=minute)
                event.location = kb[k][j]['skdd']
                event.description = '第' + str(i) + '周, ' + kb[k][j]['rkjs']
                cal.events.add(event)
                la = k+1

with open("result.ics", "w") as f:
    f.writelines(cal.serialize_iter())

# print(parse_data("slx:yjs;;kcmc:高级计算机网络;;rkjs:温武少;;skdd:东校园-教学大楼D栋东D104;;0;;jxb:23级专硕专博班;;xkzrs:1;;xslx:yjs;;sksj:2-18每周（2-4节）;;kclb:专业课;;zs:2-18周;;js:周一 2-4节,,xslx:yjs;;kcmc:高级计算机网络;;rkjs:温武少;;skdd:东校园-教学大楼D栋东D104;;0;;jxb:23级专硕专博班;;xkzrs:45;;xslx:yjs;;sksj:2-18每周（2-4节）;;kclb:专业基础课;;zs:2-18周;;js:周一 2-4节"))
