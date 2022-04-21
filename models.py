from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect
from __init__ import db

# Create user model.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))

    # Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # @hybrid_property
    # def password(self):
    #     """Return the hashed user password."""
    #     return self._password

    # @password.setter
    # def password(self, new_pass):
    #     """Salt/Hash and save the user's new password."""
    #     #new_password_hash = compute_new_password_hash(new_pass, self._salt)
    #     #self._password = new_password_hash
    #     self._password = generate_password_hash(new_pass)

    # Required for administrative interface
    def __unicode__(self):
        return self.username

@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value)
    return value

    
class City (db.Model):    
    id = db.Column(db.Integer,primary_key=True) # primary keys are required by SQLAlchemy
    cityName = db.Column(db.String(256), unique=True)      
   
    def __unicode__(self):
        return self.cityName

    def __repr__(self):
        return '<city %r>' % (self.cityName)


class Neighborhood (db.Model):    
    id = db.Column(db.Integer,primary_key=True) # primary keys are required by SQLAlchemy
    neighborhoodName = db.Column(db.String(256), unique = True)
    cityId = db.Column(db.Integer(), db.ForeignKey('city.id'))        
    city = db.relationship('City')
    
    def __unicode__(self):
        return self.neighborhoodName

    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
    
    def __repr__(self):
        return '<Neighborhood %r>' % (self.neighborhoodName)

class Type (db.Model):
    id = db.Column(db.Integer,primary_key=True) # primary keys are required by SQLAlchemy
    typeName = db.Column(db.String(256), unique = True)

    def __unicode__(self):
        return self.cityName

    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
    
    def __repr__(self):
        return '<Type %r>' % (self.typeName)



#city	neighborhood	scheme	pices	date	ID	price_sr	area_square_meter	price_square_meter	Type
class FE_dataset (db.Model):
    id = db.Column(db.Integer,primary_key=True) # primary keys are required by SQLAlchemy
    city =  db.Column(db.String(256) )
    neighborhood =  db.Column(db.String(256))
    scheme =  db.Column(db.String(256))
    pices =  db.Column(db.String(256))
    date =  db.Column(db.String())
    IDNumber =  db.Column(db.String(256))
    price_sr =  db.Column(db.Float)
    area_square_meter =  db.Column(db.Float)
    price_square_meter =  db.Column(db.Float)
    type =  db.Column(db.Integer)        

    def __unicode__(self):
        return self.neighborhoodName

    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    

class FE_predict(db.Model):    
    id = db.Column(db.Integer,primary_key=True ) # primary keys are required by SQLAlchemy
    city =  db.Column(db.String(256))
    neighborhood =  db.Column(db.String(256))
    scheme =  db.Column(db.String(256))
    pices =  db.Column(db.String(256))
    date =  db.Column(db.String(256))
    IDNumber =  db.Column(db.String(256))
    price_sr =  db.Column(db.Float)
    area_square_meter =  db.Column(db.Float)
    price_square_meter =  db.Column(db.Float)
    type =  db.Column(db.Integer)        
    latitude =  db.Column(db.Float)  
    longitude =  db.Column(db.Float)   

    def __unicode__(self):
        return self.neighborhoodName

    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    
  
