from sqlalchemy import func
from models import User, City, Neighborhood ,FE_predict, FE_dataset
from froms import LoginForm, RegistrationForm
import os
import flask
import pandas as pd
import numpy as np
import json
import requests
from __init__ import create_app, db
from flask import url_for, redirect, render_template, request, jsonify
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
import flask_admin as admin
import flask_login as login
from werkzeug.security import generate_password_hash
#from joblib import load
import pickle
from sklearn.preprocessing import LabelEncoder

URL = "https://discover.search.hereapi.com/v1/discover"
api_key = 'nm01XnznMs6bVyHIDnZXFYS08H17ia964O9Lb6IL0xc' # Acquire from developer.here.com
query = 'hospital , school , supermarket , mosque'
limit = 10

app = create_app()  # we initialize our flask app using the __init__.py function

#le_cols = ['city','neighborhood','scheme','pices','date','area_square_meter','price_square_meter']
le_cols = ['id', 'city','neighborhood','scheme','pices','Type','area_square_meter','price_square_meter','latitude','longitude']
df = pd.DataFrame(columns= le_cols)
            
def convert2num(test_d):

    cols = ('city','neighborhood','scheme','pices')
    # Process columns and apply LabelEncoder to categorical features
    for c in cols:
        lbl = LabelEncoder() 
        lbl.fit(list(test_d[c].values)) 
        test_d[c] = lbl.transform(list(test_d[c].values))
    
    return test_d

def getPredictFromModel (input_variables):
    # load saved model
    with open('model/rfr_model_pkl' , 'rb') as f:
        loaded_model = pickle.load(f)
   
    df_test =  convert2num(input_variables)
   
    test_passengerIds = df_test['id'].values
    Old_price_square_meter = df_test['price_square_meter'].values
    df_test.drop('id', axis = 1, inplace=True)
    df_test.drop(['price_square_meter'], axis=1, inplace=True)
 
    df_test.drop(['price_sr'], axis=1, inplace=True)
    df_test.drop(['latitude'], axis=1, inplace=True)
    df_test.drop(['longitude'], axis=1, inplace=True)
  
    predictions = loaded_model.predict(df_test)    
    return predictions

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)
    
    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)
    
# Create customized model view class
class MyModelView(sqla.ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list    
    column_hide_backrefs = False
    def is_accessible(self):
        return login.current_user.is_authenticated


# Create customized model view class
class NeighborhoodModelView(sqla.ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False
    column_display_all_relations = True
    def is_accessible(self):
        return login.current_user.is_authenticated

class FE_PredictModelView(sqla.ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False
    column_display_all_relations = True
    def is_accessible(self):
        return login.current_user.is_authenticated




# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()
    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):        
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):            
            user = form.get_user()
            login.login_user(user)
        if login.current_user.is_authenticated:            
            return redirect(url_for('.index'))
        
#### don,t remov
        # link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        # self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()
            form.populate_obj(user)
            
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + \
            url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, 'FUTURE-ESTATE : Admin', index_view=MyAdminIndexView(),
                    base_template='my_master.html', template_mode='bootstrap4')

# Add view
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(City, db.session))
admin.add_view(NeighborhoodModelView(Neighborhood, db.session))
admin.add_view (FE_PredictModelView(FE_predict, db.session))

# Flask views
@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':        
        return (flask.render_template('index.html'))


@app.route('/getDetials', methods=['GET', 'POST'])
def getDetials():
    if flask.request.method == 'POST':
        mCity = flask.request.form['city']
        mNeighborhood = flask.request.form['neighborhood']
        mType = flask.request.form['type']        
        return (flask.render_template('show_map.html', city=mCity, neighborhood=mNeighborhood, type=mType))
  
@app.route('/getNeighborhood', methods=['POST', 'GET'])
def getNeighborhood():
    id = request.get_json()
    results = Neighborhood.query.filter(Neighborhood.cityId == id)
    return jsonify({'htmlresponse': render_template('neighborhood.html', neighborhood=results)})

@app.route('/getDataMap', methods=['POST', 'GET'])
def getDataMap():
    if request.method == "POST":
        qtc_data = request.get_json()           
        nCity = qtc_data[0]['city']                
        nNeighborhood = qtc_data[1]['neighborhood']                
        nType = qtc_data[2]['type']                
        row = FE_predict.query.filter(FE_predict.city ==nCity , 
                                      FE_predict.neighborhood == nNeighborhood ,
                                      FE_predict.type == nType).all()
        dataList = []        
        for r in row:
            dataTuple = {}
            dataTuple['id'] = r.IDNumber
            dataTuple['city'] = r.city          
            dataTuple['neighborhood'] = r.neighborhood
            dataTuple['scheme'] = r.scheme
            dataTuple['pices'] = r.pices            
            dataTuple['price_sr'] = r.price_sr 
            dataTuple['Type'] = r.type           
            dataTuple['area_square_meter'] = r.area_square_meter  
            dataTuple['price_square_meter'] = r.price_square_meter             
            dataTuple['latitude'] = r.latitude
            dataTuple['longitude'] = r.longitude   
            dataList.append(dataTuple)       
        dataframe = df.append(dataList , ignore_index=True)
        x = dataframe.copy()
        list_priedct =  getPredictFromModel (x)        
        y_pred = np.array(list_priedct)        
        dataframe['predict'] = y_pred        
        return jsonify(dataframe.to_json(orient='records'))                

        

@app.route('/getVisualtion', methods=['POST', 'GET'])
def getVisualtion():
    if request.method == "POST":
        qtc_data = request.get_json()        
        nCity = qtc_data[0]['city']
        nType = qtc_data[2]['type']                                  
        row = FE_dataset.query.with_entities(FE_dataset.IDNumber , FE_dataset.neighborhood , FE_dataset.price_sr  ,
          func.max(FE_dataset.price_sr)).filter(FE_dataset.city == nCity , FE_dataset.type == nType) .group_by(FE_dataset.neighborhood).all()        
        dataList = []
        for r in row:
            dataTuple = {}
            dataTuple['id'] = r.IDNumber
            dataTuple['neighborhood'] = r.neighborhood
            dataTuple['price_sr'] = r.price_sr
            dataList.append(dataTuple)     
        #print(dataList) 
        json_data = json.dumps(dataList)
        return json_data

@app.route('/getVisualtionCountNeighborhood', methods=['POST', 'GET'])
def getVisualtionCountNeighborhood():
    if request.method == "POST":
        qtc_data = request.get_json()        
        nCity = qtc_data[0]['city']
        nNeighborhood = qtc_data[1]['neighborhood']  
        nType = qtc_data[2]['type']                  
        row = FE_dataset.query.with_entities(FE_dataset.IDNumber , FE_dataset.neighborhood , FE_dataset.price_sr  ,
          func.count(FE_dataset.id).label('deals')).filter(FE_dataset.city == nCity , FE_dataset.type == nType).group_by(FE_dataset.neighborhood).all()        
        dataList = []
        for r in row:
            dataTuple = {}
            dataTuple['id'] = r.IDNumber
            dataTuple['neighborhood'] = r.neighborhood
            dataTuple['price_sr'] = r.price_sr
            dataTuple['deals'] = r.deals
            dataList.append(dataTuple)     
        #print(dataList) 
        #print (len(dataList))
        json_data = json.dumps(dataList)
        return json_data


@app.route('/getVisualtionCountCity', methods=['POST', 'GET'])
def getVisualtionCountCity():
    if request.method == "POST":
        qtc_data = request.get_json()        
        nCity = qtc_data[0]['city']
        nNeighborhood = qtc_data[1]['neighborhood']  
        nType = qtc_data[2]['type']                  
        row = FE_dataset.query.with_entities(FE_dataset.IDNumber , FE_dataset.city ,
          func.count(FE_dataset.id).label('deals')).filter(FE_dataset.type == nType).group_by(FE_dataset.city).all()        
        dataList = []
        for r in row:
            dataTuple = {}
            dataTuple['id'] = r.IDNumber
            dataTuple['city'] = r.city       
            dataTuple['deals'] = r.deals
            dataList.append(dataTuple)     
        #print(dataList) 
        json_data = json.dumps(dataList)
        return json_data


@app.route('/getVisualtionPricePridect', methods=['POST', 'GET'])
def getVisualtionPricePridect():
    if request.method == "POST":
        qtc_data = request.get_json()        
        nScheme = qtc_data[0]['scheme']
        nPices = qtc_data[1]['pices']        
        #print (qtc_data)        
        row = FE_dataset.query.filter(FE_dataset.scheme == nScheme  , FE_dataset.pices == nPices).all()# .group_by(FE_dataset.date).all()        
        dataList = []
        for r in row:
            dataTuple = {}
            dataTuple['id'] = r.IDNumber
            dataTuple['pices'] = r.neighborhood
            dataTuple['date'] = r.date
            dataList.append(dataTuple)        
        json_data = json.dumps(dataList)
        return json_data

@app.route('/getCity', methods=['POST', 'GET'])
def getCity():
    if request.method == "POST":        
        city = City.query.all()
        cityList = []
        for r in city:
            cityData = {}
            cityData['id'] = r.id
            cityData['cityName'] = r.cityName
            cityList.append(cityData)        
        json_data = json.dumps(cityList)
        return json_data

@app.route('/getNeighborhoodByCityName', methods=['POST', 'GET'])
def getNeighborhoodByCityName():
    if request.method == "POST":
        qtc_data = request.get_json()        
        nCity = qtc_data[0]['city']      

        neighborhood = Neighborhood.query.join(City).filter(
            City.cityName == nCity
        ).all()        

        nList = []
        for r in neighborhood:
            nData = {}
            nData['id'] = r.id
            nData['neighborhoodName'] = r.neighborhoodName
            nList.append(nData)
        json_data = json.dumps(nList)
        return json_data

@app.route('/getServiceLoation', methods=['POST', 'GET'])
def getServiceLoation():
    qtc_data = request.get_json()  
    nlat = qtc_data[0]['lat']
    nlog = qtc_data[0]['log']
    PARAMS = {
            'apikey':api_key,
            'q':query,
            'limit': limit,
            'at':'{},{}'.format(nlat,nlog)
        }    
    # sending get request and saving the response as response object 
    r = requests.get(url = URL, params = PARAMS) 
    data = r.json()   
    return jsonify(data)

#from waitress import serve
if __name__ == '__main__':
    
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    app.run(debug=True)