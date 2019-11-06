'''


class Data_get_from_db(object):

    _selectArea = str  ## 선택된 지역들.
    _areaValues = str  ## 선택한 지역들(s).

    def __init__(self, select, tableName, condition):
        self._select = select  ## 보고 싶은 지역 정보 선택.
        self._tableName = tableName  ## 정보가 들어있는 테이블
        self._condition = condition  ## 조건문(원하는 정보만 get) , ex) 20190501 이후.


    # 최종 결과 - 조건절 포함.
    def final_result_where(self):

        self.get_select_field(self._select)
        rselect = "select " + str(self._selectArea)
        # print(rselect)
        rfrom = " from " + str(self._tableName)
        # print(rfrom)
        self.get_where_item2(**self._condition)
        rwhere = " where " + str(self._areaValues)
        rresult = rselect + rfrom + rwhere
        return rresult


    # 최종 결과 - 조건 없을 때.
    def final_result_from(self):

        self.get_select_field(self._select)
        rselect = "select " + str(self._selectArea)
        # print(rselect)
        rfrom = " from " + str(self._tableName)
        # print(rfrom)
        rresult = rselect + rfrom
        return rresult


        # 컬럼(열)들을 선택. - en
    def get_select_field(self, select):
        # value = []

        if type(select) is list:
            k = 0
            values = ""
            for i in range(len(select)):
                values = values + str(select[k])
                if not (k + 1) == len(select):
                    values = values + ", "
                k = k + 1

            self._selectArea = values

        else:
            self._selectArea = select


    # where sido_name='광주광역시' and area_name='광주'
    # 조건문. {"sido_name":"광주광역시", "area_name":"광주"}
    def get_where_item(self, **kwargs):
        # value = []
        values = ""
        k = 0
        for i in kwargs.items():
            values = values + " " +str(kwargs.keys()[k]) + "='" + str(kwargs.values()[k])+"'"
            if not (k+1) == len(kwargs.items()):
                values = values + " and"
            k = k+1

        self._areaValues = values

    # 조건문. {"sido_name":["광주광역시","="],"area_name":["광주","="]}
    # 조건문. {"hm":[20,">",30,"<"],"observed":[2019-05-01 12:00:00,">']}
    # 조건문. {"id":[11,"="]}
    def get_where_item2(self, **kwargs):
        # value = []

        values = ""

        k = 0
        for i in kwargs.items():
            l = 0
            for j in range(len(kwargs.values()[k]) / 2):
                values = values + str(kwargs.keys()[k]) + str(kwargs.values()[k][l + 1]) + "'" + str(
                    kwargs.values()[k][l]) + "'"
                l = l + 2
                if not l == len(kwargs.values()[k]):
                    values = values + " and "

            k = k + 1
            if not k == len(kwargs.items()):
                values = values + " and "

        self._areaValues = values





# area 에서 받은 ubicode를 변환.
def get_area_english_name(area):
    # if not type(area) == list:
    #     return False
    #
    # s1 = area[0].encode("UTF-8")
    # s2 = area[1].encode("UTF-8")
    #
    # # 처음에 반드시 [weather_observe_area]에서 해당 지역(ex.광주광역시-광주)의 영어이름(en)을 가져와야함.
    # default_condition = {"sido_name": [s1,'='], "area_name": [s2,'=']}
    default_condition = {"id":[area,'=']}
    en_name = Data_get_from_db("en", "weather_observe_area", default_condition)
    enquery = str(en_name.final_result_where())
    records1 = dbsearch.execute(enquery)

    recn = []
    for row_n in records1:
        recn.append(dict(row_n))

    en_name = row_n[0]

    condition = 0

    # en 이름으로 해당 ex) 광주 광역시 DB(weather_gwangju)를 찾아서 쿼리 찾음.
    area = "weather_" + en_name
    print("select_area: ",area)

    return area


# byRyan


test1={"ws":[0,'>',2.0,'<'],"hm":3}
# test1={"sido_name":"광주광역시", "area_name":"광주"}
def get_where_item11(**kwargs):
    aaaa = str

    try:

        # value = []
        values = ""

        k = 0
        for i in kwargs.items():
            l = 0
            print(kwargs.values()[k])
            for j in range(len(kwargs.values()[k]) / 2):
                values = values + str(kwargs.keys()[k]) + str(kwargs.values()[k][l + 1]) + "'" + str(
                    kwargs.values()[k][l]) + "'"

                if not (k + 1) == len(kwargs.items()):
                    values = values + " and "
                l = l + 2
            k = k + 1

        return values
    except Exception as e:
        print('aaaaa')
        aaaa = e
        aaa = "aa"
        return aaa

# print(get_where_item11(**test1))

'''