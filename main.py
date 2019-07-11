import pymysql
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request
from flask_bcrypt import generate_password_hash,check_password_hash

@app.route('/add_doctor',methods=['POST'])
def add_doctor():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        _json = request.get_json()
        _gender = _json['gender']
        _name = _json['name']
        _password = _json['pwd']
        _date_of_birth = _json['dob']
        _phone_number = _json['phone']
        _email = _json['email']
        
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
                resp = jsonify(success={"message":"Login successfully"})
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
    
@app.route('/add_patient',methods=['POST'])
def add_patient():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        _json = request.get_json()
        _gender = _json['gender']
        _name = _json['name']
        _date_of_birth = _json['dob']
        _phone_number = _json['phone']
        _email = _json['email']
        _doc_id=_json['doc_id']
        docid= int(_doc_id)
        if _name and _gender and _email and _date_of_birth and _phone_number and _doc_id is not None:
            sql = "INSERT INTO patient(pat_name,pat_gender,email,phone,dob,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)"
            data = ( _name, _gender,_email,_phone_number,_date_of_birth,docid)
            cursor.execute(sql, data)
            conn.commit()
            resp = jsonify(success={"message":"PATIENT added  successfully!"})
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(error={"message":"Error"})
            return resp
    except Exception as e:
         print(e)
    finally:
         cursor.close()
         conn.close()

@app.route('/doctors')
def doctors():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * from doctor")
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/')
def doctors_home():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * from doctor")
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/patients')
def patients():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * from patient")
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
        
@app.route('/doctor',methods=['POST'])
def doctor():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        id = request.json['id']
        cursor.execute("SELECT * FROM doctor WHERE doc_id=%s",id)
        row = cursor.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/patient',methods=['POST'])
def patient():
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
    
@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        _json = request.json
        _id = _json['id']
        _name = _json['name']
        _gender = _json['gender']
        _email = _json['email']
        _password = _json['pwd']
        _phone_number = _json['phone']
        _date_of_birth = _json['dob']
        
        #validate the received values
        if _id and _name and _gender and _email and _password and _date_of_birth and _phone_number is not 'None':
            _hashed_password = generate_password_hash(_password)
            #save edits
            sql = "UPDATE doctor SET doc_name=%s, doc_gender=%s , doc_email=%s, doc_password=%s, phone=%s, dob=%s WHERE doc_id=%s"
            data = ( _name, _gender, _email, _hashed_password, _phone_number, _date_of_birth, _id)
            cursor.execute(sql, data)
            conn.commit()
            resp = jsonify("DOCTOR updated successfully!")
            resp.status_code = 200
            return resp
    except Exception as e:
            print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/update_patient', methods=['POST'])
def update_patient():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        _json = request.json
        _id = _json['id']
        _name = _json['name']
        _gender = _json['gender']
        _email = _json['email']
        _phone_number = _json['phone']
        _date_of_birth = _json['dob']
        _doc_id = _json['doctor_id']
        #validate the received values
        if _id and _name and _gender and _email and _date_of_birth and _phone_number is not 'None':
            #save edits
            sql = "UPDATE patient SET pat_name=%s, pat_gender=%s , email=%s, phone=%s, dob=%s, doctor_id=%s WHERE pat_id=%s"
            data = ( _name, _gender, _email, _phone_number, _date_of_birth,_doc_id, _id)
            cursor.execute(sql, data)
            conn.commit()
            resp = jsonify("PATIENT updated successfully!")
            resp.status_code = 200
            return resp
    except Exception as e:
            print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_doctor',methods = ['POST'])
def delete_doctor():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        id = request.json['id']
        cursor.execute("DELETE FROM doctor WHERE doc_id=%s",id)
        conn.commit()
        resp = jsonify('DOCTOR deleted successfully')
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_patient',methods = ['POST'])
def delete_patient():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        id = request.json['id']
        cursor.execute("DELETE FROM patient WHERE pat_id=%s",id)
        conn.commit()
        resp = jsonify('PATIENT deleted successfully')
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True,port=80,host='0.0.0.0')
    