from . import app
# from API.main_api import apis
from API.Login.login_API import user_apis
from API.Predict.predic_API import predic_apis
from API.DataSet.data_API import data_apis
from DB.DataBase.model_API import model_apis
# app.register_blueprint(apis)
app.register_blueprint(user_apis)
app.register_blueprint(predic_apis)
app.register_blueprint(data_apis)
app.register_blueprint(model_apis)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10300, debug=False)


