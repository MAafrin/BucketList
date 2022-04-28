import psycopg2 as psycopg2
from flask import Flask, render_template, request, url_for, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'secret'


def get_db_connection():
    conn = psycopg2.connect(host="localhost", dbname="bucketlist", user="postgres", password="postgres")
    conn.autocommit = True
    return conn


def create_cursor():
    conn = get_db_connection()
    cur = conn.cursor()
    return cur


def close_connections():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.close()
    return conn.close()


@app.route('/')
@app.route('/home')
def main():  # put application's code here
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signin')
def showSignin():
    return render_template('signin.html')


@app.route('/api/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        sql = "select * from tbl_user where user_email =%s"

        cur = create_cursor()
        cur.execute(sql, (_username,))
        data = cur.fetchall()
        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                session['user'] = data[0][0]
                return redirect('/userhome')
            else:
                return render_template('error.html', error='Wrong Email address or Password')
        else:
            return render_template('error.html', error='Wrong Email address or Password')


    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        close_connections()


@app.route('/api/signup', methods=['POST'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _hashed_password = generate_password_hash(_password)
        sql = "select * from tbl_user where user_email =%s"

        cur = create_cursor()

        cur.execute(sql, (_email,))
        data = cur.fetchall()
        if len(data) > 0:
            return render_template('error.html', error='User already exists')
        else:
            cur.execute('INSERT INTO tbl_user (user_name, user_email, user_password)''VALUES (%s, %s, %s)',
                        (_name, _email, _hashed_password))
            return render_template('index.html', message="success", name=_name)
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        close_connections()
    return render_template('index.html')


@app.route('/userhome')
def userHome():
    if session.get('user'):
        _user = session.get('user')
        sql = "select * from tbl_wish where wish_user_id  =%s"

        cur = create_cursor()

        cur.execute(sql, (_user,))
        wishes = cur.fetchall()
        return render_template('userhome.html',wishes=wishes)
    else:
        return render_template('error.html', error='Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/addWish',  methods=['GET', 'POST'])
def addWish():
    if request.method == 'POST':
        try:
            if session.get('user'):
                _title = request.form['inputTitle']
                _description = request.form['inputDescription']
                _user = session.get('user')
                sql = "insert into tbl_wish(wish_title,wish_description,wish_user_id,wish_date) values(%s,%s,%s,NOW());"

                cur = create_cursor()
                cur.execute(sql, (_title, _description, _user))

                return redirect('/userhome')
            else:
                return render_template('error.html', error='Unauthorized Access')
        except Exception as e:
            return render_template('error.html', error=str(e))
        finally:
            close_connections()
    return render_template('addWish.html')


# @app.route('/getWish')
# def getWish():
#     try:
#         if session.get('user'):
#             # _user = session.get('user')
#             # sql = "select * from tbl_wish where wish_user_id  =%s"
#             #
#             # cur = create_cursor()
#             #
#             # cur.execute(sql, (_user,))
#             # wishes = cur.fetchall()
#             return redirect('/userhome')
#         else:
#             return render_template('error.html', error='Unauthorized Access')
#     except Exception as e:
#         return render_template('error.html', error=str(e))


if __name__ == '__main__':
    app.run()
