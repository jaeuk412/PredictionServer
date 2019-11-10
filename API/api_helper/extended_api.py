from flask import request, abort, jsonify
from sqlalchemy import Column
from sqlalchemy.orm import Query
from DB.DataBase.database import db_session





class ExtendedApi:
    _paginated = bool
    _limit = int
    _page = int
    _search = bool
    _target = Column
    _keyword = str

    def __init__(self,db):
        self._db = db
        # self._request=request

    def getInt(self, key):
        return request.args.get(key, type=int)

    def getStr(self, key):
        return request.args.get(key, type=str)

    def paginate(self):
        query = self._db

        self._limit = self.getInt('limit')
        self._page = self.getInt('page')

        # print 'paginate--------------'
        # print self._limit
        # print self._page

        # print '---------------0---------------'

        if self._limit:
            # print '-------------0101-------------'
            self._paginated = True

            if not self._page:
                self._page=1


            elif self._page <1:
                abort(400)

            total = query.count()
            total_page = round(total / self._limit)

            # print 'total:',total
            # print 'self_limit:',self._limit
            # print 'total_page:',total_page
            # print 'selfpage:',self._page

            if self._page > total_page:
                if self._page==1:
                    pass
                else:
                    abort(400)

            offset = self._limit * (self._page - 1)
            query = query.limit(self._limit).offset(offset)
            # print '-----------------------'

            if self._page:
                if not self._limit:
                    abort(400)

        if self._page:
            # print '----------1--------------'
            if not self._limit:
                abort(400)

        # print '----------2------------'
        records=db_session.execute(query)

        if not records:
            return jsonify(False)

            # offset
            # total-page
        # print '-------------result'
        # print self
        return records

#    query = db_session.query(Project).order_by(Project.id.asc())

    def search(self, target):
        self._keyword = self.getStr('keyword')

        # if not query:
        #     abort(400)
        #
        # else:

        if self._keyword:
            self._search = True
            self._target = target

            search = '%' + self._keyword + '%'
            query = db_session.query(self._target).filter(target.name.like(search)).order_by(self._target.id.asc())

            # quert1 = query.filter(self._target.name.like(search))

            # query = db_session.query(self._target).filter(target.name.like(search))

            return query
        else:
            pass

    def execute(self, sql=Query):
        if self._paginated:
            sql = sql.limit(self._limit)
            # offset

        if self._search:
            sql = sql.filter(self._target == self._keyword)

        return sql