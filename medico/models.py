from medico import db, login_manager, bcrypt, app
from flask_login import UserMixin
from flask import render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from sklearn.impute import SimpleImputer


def scaling(dataframe):
    # Exclude non-numerical columns before scaling
    numeric_columns = dataframe.select_dtypes(include=['number']).columns
    prep_data = dataframe[numeric_columns].copy()  # Copy only numeric data

    # Impute missing values with the mean
    imputer = SimpleImputer(strategy='mean')
    prep_data_imputed = imputer.fit_transform(prep_data)

    # Scale the data
    scaler = StandardScaler()
    prep_data_scaled = scaler.fit_transform(prep_data_imputed)

    return prep_data_scaled, scaler


def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine',algorithm='brute')
    neigh.fit(prep_data)
    return neigh

def build_pipeline(neigh, scaler, params):
    imputer = SimpleImputer(strategy='mean')
    transformer = FunctionTransformer(neigh.kneighbors, kw_args=params)
    pipeline = Pipeline([
        ('imputer', imputer),  # Handle missing values
        ('std_scaler', scaler),  # Standardize features
        ('NN', transformer)  # Apply Nearest Neighbors
    ])
    return pipeline

def extract_data(dataframe,ingredients):
    extracted_data=dataframe.copy()
    extracted_data=extract_ingredient_filtered_data(extracted_data,ingredients)
    return extracted_data
    
def extract_ingredient_filtered_data(dataframe,ingredients):
    extracted_data=dataframe.copy()
    regex_string=''.join(map(lambda x:f'(?=.*{x})',ingredients))
    extracted_data=extracted_data[extracted_data['RecipeIngredientParts'].str.contains(regex_string,regex=True,flags=re.IGNORECASE)]
    return extracted_data

def apply_pipeline(pipeline, _input, extracted_data):
    _input = np.array(_input).reshape(1, -1)
    return extracted_data.iloc[pipeline.transform(_input)[0]]

def recommend(dataframe, _input, params={'n_neighbors': 5, 'return_distance': False}):
    if dataframe.shape[0] >= params['n_neighbors']:
        prep_data, scaler = scaling(dataframe)
        neigh = nn_predictor(prep_data)
        pipeline = build_pipeline(neigh, scaler, params)
        return apply_pipeline(pipeline, _input, dataframe)
    else:
        return None

def extract_quoted_strings(s):
    # Find all the strings inside double quotes
    strings = re.findall(r'"([^"]*)"', s)
    # Join the strings with 'and'
    return strings

def output_recommended_recipes(dataframe):
    if dataframe is not None:
        output=dataframe.copy()
        output=output.to_dict("records")
        for recipe in output:
            recipe['RecipeIngredientParts']=extract_quoted_strings(recipe['RecipeIngredientParts'])
            recipe['RecipeInstructions']=extract_quoted_strings(recipe['RecipeInstructions'])
    else:
        output=None
    return output

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    role = db.Column(db.String(length=10), nullable=False)
    specialisation = db.Column(db.String(length=100), nullable=True) 
    
    # Relationship for user appointments
    user_appointments = db.relationship('Appointment', 
                                        foreign_keys='Appointment.user_id', 
                                        backref='user', 
                                        lazy=True)
    
    # Relationship for doctor appointments
    doctor_appointments = db.relationship('Appointment', 
                                          foreign_keys='Appointment.doctor_id', 
                                          backref='doctor', 
                                          lazy=True)

    def __repr__(self):
        return f'User {self.username}'
    
    
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Appointment for {self.name} on {self.date} at {self.time}'
    
    def get_doctor_name(self):
        doctor = User.query.get(self.doctor_id)
        return doctor.username if doctor else "Unknown Doctor"
    
class ModifiedSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    from_time = db.Column(db.Time, nullable=False)
    to_time = db.Column(db.Time, nullable=False)

    doctor = db.relationship('User', back_populates='modified_schedules')

User.modified_schedules = db.relationship('ModifiedSchedule', back_populates='doctor')

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hostel = db.Column(db.String(100), nullable=False)
    pills = db.Column(db.String(200), nullable=True)
    complaint = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'MedicalRecord {self.id} for {self.name}'

class Pill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    expiry_dates = db.Column(db.JSON)


