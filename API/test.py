datestart = 2015
dateend = 2019

datelist = []
datarange = dateend-datestart
print(range(datarange))
for i in range(datarange):
    print(i)
    datestart += 1
    datelist.append(datestart)

print(datelist)