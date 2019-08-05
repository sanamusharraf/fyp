import pymysql
from app import app , jwt , os
from db_config import mysql
from flask import jsonify
from flask import flash, request
from flask_bcrypt import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required,get_jwt_identity
from pydub import AudioSegment
import re
import nltk
import heapq
from twilio.rest import Client
import smtplib
import requests
from requests.exceptions import HTTPError
import speech_recognition as sr

@app.route('/upload',methods=['POST'])
def upload_file():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        _patientid = request.form['patientid']
        _doctorid = request.form['doctorid']
        target = os.path.join(app.config['UPLOAD_FOLDER'], 'AudioFiles')
        print("Target name is" + target)

        if not os.path.isdir(target):
            os.mkdir(target)

        file = request.files['file']
        filename = file.filename
        f = '/'.join([target, filename])
        print("Final Filename is "+ f)
        file.save(f)
        resp = jsonify('File Added successfully')
        resp.status_code = 200
        return resp
    
    except Exception as e:
        print(e)

    finally:
        cursor.close()
        conn.close()
        basepath = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(basepath, "AudioFiles", filename))
        print(filepath)

        wav_file = os.path.splitext(filepath)[0] + '.wav'
        print(wav_file)
        sound = AudioSegment.from_file(filepath)
        sound.export(wav_file, format="wav")
        os.remove(filepath)

        #speech to text module
        rec = sr.Recognizer()
        audioFile = os.path.abspath(os.path.join(basepath, "AudioFiles", wav_file))
        with sr.AudioFile(audioFile) as sourceFile:
            audio = rec.record(sourceFile) 
        try:
            text = rec.recognize_google(audio)
        except Exception as e:
            print(e)    
        
        print(text)

        #preprocessing the data
        text = re.sub(r'\[[0-9]*\]',' ',text)
        text = re.sub(r'\s+',' ',text)
        clean_text = text.lower()
        clean_text = re.sub(r'\W',' ',clean_text)
        clean_text = re.sub(r'\d',' ',clean_text)
        clean_text = re.sub(r'\s+',' ',clean_text)
        print(clean_text)
        sentences = nltk.sent_tokenize(text)

        stop_words = nltk.corpus.stopwords.words('english')    

        #Figuring out cancer terms and medicine prescribed in the conversation
        #tokenizing the sentences
        words = nltk.word_tokenize(text)
        print(words)
        #applying part of speech on each individual word
        tagged_words = nltk.pos_tag(words)

        #collecting all the nouns in a seperate list
        word_tags=[]
        for tw in tagged_words:
            if tw[1] == "NN" or tw[1] == "NNS" or tw[1] == "NNP" or tw[1] == "NNPS":
                word_tags.append(tw[0])


                                                    #ADD DOCTOR     
@app.route('/add_doctor',methods=['POST'])
def add_doctor():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        _gender = request.form['gender']
        _name = request.form['name']
        _password =request.form['pwd']
        _date_of_birth = request.form['dob']
        _phone_number =request.form['phone']
        _email = request.form['email']
        
        if _name and _gender and _email and _password and _date_of_birth and _phone_number is not 'None':
            cursor.execute("SELECT * FROM doctor WHERE doc_email=%s",_email) 
            row = cursor.fetchone()
            if row is None:
                _hashed_password = generate_password_hash(_password).decode('utf-8')
                sql = "INSERT INTO doctor(doc_name,doc_gender,doc_password,doc_email,phone,dob) VALUES(%s,%s,%s,%s,%s,%s)"
                data = ( _name, _gender,_hashed_password,_email,_phone_number,_date_of_birth)
                cursor.execute(sql, data)
                conn.commit()
                resp = jsonify(success={"message":"DOCTOR added  successfully!"})
                resp.status_code = 200
                return resp
            else:
                resp = jsonify(error={"message":"Email already exists!"})
                return resp
        else:
            resp = jsonify(error={"message":"Error"})
            return resp
    except Exception as e:
         print(e)
    finally:
         cursor.close()
         conn.close()

                                                    #LOGIN DOCTOR         
@app.route('/login_doctor',methods=['POST'])
def login_doctor():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        _json = request.get_json()
        _password = _json['pwd']
        _email = _json['email']
        cursor.execute("SELECT * FROM doctor WHERE doc_email=%s",_email) 
        row = cursor.fetchone()
        if row is not None:
           if check_password_hash(row["doc_password"],_password) is True :
                resp = jsonify(success={"message":"Login successfully","token": create_access_token(identity=row["doc_password"])})
                resp.status_code = 200
                return resp
           else:
                resp = jsonify(error={"message":"Wrong Password Entered"})
                return resp
        else:
            resp = jsonify(error={"message":"Wrong Email Entered"})
            return resp
    except Exception as e:
         print(e)
    finally:
         cursor.close()
         conn.close()

                                            #GET DOCTOR BY EMAIL
@app.route('/getdoctorbyemail',methods=['POST'])
def getdoctorbyemail():
    current_user = get_jwt_identity()
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        email = request.json['email']
        cursor.execute("SELECT * FROM doctor WHERE doc_email=%s",email)
        row = cursor.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

                                                #ADD PATIENT
@app.route('/add_patient',methods=['POST'])
def add_patient():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        _gender = request.form['gender']
        _name = request.form['name']
        _date_of_birth =request.form['dob']
        _phone_number = request.form['phone']
        _email = request.form['email']
        _doc_id=request.form['doc_id']
       
        if _name and _gender and _email and _date_of_birth and _phone_number and _doc_id is not None:
            cursor.execute("SELECT * FROM patient WHERE phone=%s",_phone_number) 
            row = cursor.fetchone()
            if row is None:
                sql = "INSERT INTO patient(pat_name,pat_gender,email,phone,dob,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)"
                data = ( _name, _gender,_email,_phone_number,_date_of_birth,_doc_id)
                cursor.execute(sql, data)
                conn.commit()
                resp = jsonify(success={"message":"PATIENT added successfully!"})
                resp.status_code = 200
                return resp
            else:
                resp = jsonify(error={"message":"Patient already exists!"})
                return resp
        else:
            resp = jsonify(error={"message":"Error"})
            return resp
    except Exception as e:
         print(e)
    finally:
         cursor.close()
         conn.close()

                                                #GET ALL PATIENTS
@app.route('/getallpatients')
def getallpatients():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        id = request.json['id']
        cursor.execute("Select * from patient where doctor_id=%s",id)
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

                                            #GET PATIENT BY PHONE        
@app.route('/getpatientbyphone',methods=['POST'])
def getpatientbyphone():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cellphone = request.json['cellphone']
        cursor.execute("SELECT * FROM patient WHERE phone=%s",cellphone)
        row = cursor.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

                                            #GET PATIENT BY Id        
@app.route('/getpatientbyid',methods=['POST'])
def getpatientbyid():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        id = request.json['id']
        cursor.execute("SELECT * FROM patient WHERE idPatient=%s",id)
        row = cursor.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

                                            #CANCER TERMS MEANING        
@app.route('/meaning',methods=['POST'])
def meaning():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        word = request.json['word']
        cursor.execute("SELECT meaning FROM conversion WHERE word=%s",word)
        row = cursor.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

                                                #MEDICINE TERMS 
@app.route('/medicine',methods=['POST'])
def medicine():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        word = request.json['word']
        cursor.execute("SELECT words FROM medicineterms WHERE words=%s",word)
        row = cursor.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    
# @app.route('/update_doctor', methods=['POST'])
# def update_doctor():
#     try:
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         _json = request.json
#         _id = _json['id']
#         _name = _json['name']
#         _gender = _json['gender']
#         _email = _json['email']
#         _password = _json['pwd']
#         _phone_number = _json['phone']
#         _date_of_birth = _json['dob']
        
#         #validate the received values
#         if _id and _name and _gender and _email and _password and _date_of_birth and _phone_number is not 'None':
#             _hashed_password = generate_password_hash(_password)
#             #save edits
#             sql = "UPDATE doctor SET doc_name=%s, doc_gender=%s , doc_email=%s, doc_password=%s, phone=%s, dob=%s WHERE doc_id=%s"
#             data = ( _name, _gender, _email, _hashed_password, _phone_number, _date_of_birth, _id)
#             cursor.execute(sql, data)
#             conn.commit()
#             resp = jsonify("DOCTOR updated successfully!")
#             resp.status_code = 200
#             return resp
#     except Exception as e:
#             print(e)
#     finally:
#         cursor.close()
#         conn.close()

# @app.route('/update_patient', methods=['POST'])
# def update_patient():
#     try:
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         _json = request.json
#         _id = _json['id']
#         _name = _json['name']
#         _gender = _json['gender']
#         _email = _json['email']
#         _phone_number = _json['phone']
#         _date_of_birth = _json['dob']
#         _doc_id = _json['doctor_id']
#         #validate the received values
#         if _id and _name and _gender and _email and _date_of_birth and _phone_number is not 'None':
#             #save edits
#             sql = "UPDATE patient SET pat_name=%s, pat_gender=%s , email=%s, phone=%s, dob=%s, doctor_id=%s WHERE idPatient=%s"
#             data = ( _name, _gender, _email, _phone_number, _date_of_birth,_doc_id, _id)
#             cursor.execute(sql, data)
#             conn.commit()
#             resp = jsonify("PATIENT updated successfully!")
#             resp.status_code = 200
#             return resp
#     except Exception as e:
#             print(e)
#     finally:
#         cursor.close()
#         conn.close()

# @app.route('/delete_doctor',methods = ['POST'])
# def delete_doctor():
#     try:
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         id = request.json['id']
#         cursor.execute("DELETE FROM doctor WHERE doc_id=%s",id)
#         conn.commit()
#         resp = jsonify('DOCTOR deleted successfully')
#         resp.status_code = 200
#         return resp
#     except Exception as e:
#         print(e)
#     finally:
#         cursor.close()
#         conn.close()

# @app.route('/delete_patient',methods = ['POST'])
# def delete_patient():
#     try:
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         id = request.json['id']
#         cursor.execute("DELETE FROM patient WHERE idPatient=%s",id)
#         conn.commit()
#         resp = jsonify('PATIENT deleted successfully')
#         resp.status_code = 200
#         return resp
#     except Exception as e:
#         print(e)
#     finally:
#         cursor.close()
#         conn.close()

def tokenResponse(msg,st):
    return jsonify(token={"message":msg,"status":st})

def setDefaultJwtTokenBehaviour():

    @jwt.expired_token_loader
    def expired_token_callback(expired_token):
        return tokenResponse("Token Expired","1")


    @jwt.invalid_token_loader
    def invalid_token_callback(invalid_token):
        return tokenResponse("Invalid Token","2")

    @jwt.unauthorized_loader
    def unauthorized_token_callback(invalid_token):
        return tokenResponse("No token passed in request","3")
        
if __name__ == "__main__":
    setDefaultJwtTokenBehaviour()
    app.run(debug=True,port=80,host='0.0.0.0')
    