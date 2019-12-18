import datetime
from pytz import timezone, utc

KST = timezone('Asia/Seoul')

now = datetime.datetime.utcnow()
# UTC 기준 naive datetime : datetime.datetime(2019, 2, 15, 4, 18, 28, 805879)

utc.localize(now)
# UTC 기준 aware datetime : datetime.datetime(2019, 2, 15, 4, 18, 28, 805879, tzinfo=<UTC>)

KST.localize(now)
# UTC 시각, 시간대만 KST : datetime.datetime(2019, 2, 15, 4, 18, 28, 805879, tzinfo=<DstTzInfo 'Asia/Seoul' KST+9:00:00 STD>)

utc.localize(now).astimezone(KST)
# KST 기준 aware datetime : datetime.datetime(2019, 2, 15, 13, 18, 28, 805879, tzinfo=<DstTzInfo 'Asia/Seoul' KST+9:00:00 STD>)

KST = timezone('Asia/Seoul')
TW = timezone('Asia/Taipei')

date = datetime.datetime.now()
# datetime.datetime(2019, 2, 15, 13, 59, 44, 872224)
print(date)
date.replace(hour=10) # hour만 변경
# datetime.datetime(2019, 2, 15, 10, 59, 44, 872224)

print(date.replace(tzinfo=KST)) # tzinfo만 변경
# datetime.datetime(2019, 2, 15, 13, 59, 44, 872224, tzinfo=<DstTzInfo 'Asia/Seoul' LMT+8:28:00 STD>)

print(date.replace(tzinfo=TW)) # tzinfo만 변경
# datetime.datetime(2019, 2, 15, 13, 59, 44, 872224, tzinfo=<DstTzInfo 'Asia/Taipei' LMT+8:06:00 STD>)

