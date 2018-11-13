import wsgiref
from flask import render_template, request ,redirect,url_for,flash,logging,sessions,session
from flask_login import login_manager,UserMixin
from flaskext.mysql import MySQL
from functools import wraps
import mysql.connector
from . import app

#######################################mysql connection #########################################

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'project1'
app.config['MYSQL_DATABASE_HOST'] = '3306'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'

mysql.init_app(app)
mysql=MySQL(app)
conn = mysql.connect()
cursor =conn.cursor()

#########################################decorator's####################
#to check if user logged out

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('unothorized, please login and proceed','danger')
            return redirect(url_for('index'))
    return wrap



#######################################the main page#########################################


@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('Main.html')

#######################################student login page #########################################

@app.route('/slogin/', methods=['GET', 'POST'])
def slogin():
    #flash('You were logged out.')
    if request.method == 'POST':
        userdetails = request.form
        roll = userdetails['roll']
        password = userdetails['password']
        print(roll, password)
        try:
            cursor.execute("select roll_no from student where roll_no=%s;", roll)
            mroll = cursor.fetchone()
            mroll = mroll[0]
            print(mroll)
            cursor.execute("select pass from student where roll_no=%s;", roll)
            mpass = cursor.fetchone()
            mpass = mpass[0]
            print(mpass)
            cursor.execute('select roll_no,sname,pass,email,phno,rank from student where roll_no=%s;', roll)
            data = cursor.fetchall()
            if roll == mroll and password == mpass:
                session['logged_in']=True
                session['username']=roll
                flash('you are logged in','success')
                return redirect(url_for('search_college', roll=roll, branch='all', loc='all'))
            else:
                message = 'incorrect password!!'
                return render_template('index.html', message=message)
        except:
            message = 'invalid username!!'
            return render_template('index.html', message=message)
    message = 'login with your user name and password'
    return render_template('index.html',message=message)

#######################################student signup page #########################################

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    print('hai')
    if request.method == 'POST':
        print('hai')
        signupdetails = request.form
        rollno = str(signupdetails['rollno'])
        name=str(signupdetails['name'])
        password = str(signupdetails['password'])
        email=str(signupdetails['email'])
        phno=int(signupdetails['phno'])
        rank=int(signupdetails['rank'])
        #print(signupdetails)
        print(rollno,name,password,email,phno,email,rank)
        try:
            cursor.execute("select roll_no,sname,rank from cet_rank where roll_no=%s;", rollno)
            data = cursor.fetchall()
            drollno = str(data[0][0])
            dsname = str(data[0][1])
            drank = int(data[0][2])
            print(drollno, dsname, drank)
            print(rollno, name, rank)
            t = (rollno, name, password, email, phno, rank)
            if rollno == drollno and name == dsname and rank == drank:
                cursor.execute("insert into student(roll_no,sname,pass,email,phno,rank) values(%s,%s,%s,%s,%s,%s);",
                               (rollno, name, password, email, phno, rank))
                conn.commit()
                session['logged_in'] = True
                session['username'] = drollno
                flash('sign up seccussfull', 'success')
                return redirect(url_for('/search_college/', roll=rollno, branch='all', loc='all'))
            else:
                return 'info sari illa'
        except:
            message = 'invalid information'
            return render_template('signup.html', message=message)
    message='login with your user name and password'
    return render_template('signup.html',message=message)



####################################### the search page #########################################

@app.route('/search_college/<roll>/<branch>/<loc>',methods=['GET','POST'])
@is_logged_in
def search_college(roll,branch,loc):
    if request.method=='POST':
        search_details=request.form
        branch=search_details['branch']
        loc=search_details['loc']
        print(branch,loc)
        cursor.execute('select rank from student where roll_no=%s;', roll)
        rank = cursor.fetchone()
        print(rank)
        rank = rank[0]
        if branch=='all' and loc=='all':
            print("yup")
            cursor.execute("""select c.cid,c.cname,b.bname,c.loc,b.cutoff,b.fees,b.seats from college c,branch b 
                                    where b.cutoff>=%s and c.cid=b.cid;""",
                           rank)
        elif branch=='all':
            cursor.execute("""select c.cid,c.cname,b.bname,c.loc,b.cutoff,b.fees,b.seats from college c,branch b 
            where b.cutoff>=%s and c.cid=b.cid and c.loc=%s;""",
                           (rank,loc))
        elif loc=='all':
            cursor.execute("""select c.cid,c.cname,b.bname,c.loc,b.cutoff,b.fees,b.seats from college c,branch b 
                        where b.cutoff>=%s and c.cid=b.cid and b.bname=%s;""",
                           (rank, branch))

        else:
            cursor.execute("""select c.cid,c.cname,b.bname,c.loc,b.cutoff,b.fees,b.seats from college c,branch b 
                                                where b.cutoff>=%s and b.bname=%s and c.loc=%s and c.cid=b.cid;""",
                           (rank,branch,loc))
        college=cursor.fetchall()
        return render_template('search.html', roll=roll, rank=rank, college=college, branch=branch, loc=loc)

    print(roll)
    cursor.execute('select rank from student where roll_no=%s;',roll)
    rank=cursor.fetchone()
    print(rank)
    rank=rank[0]
    cursor.execute('select c.cid,c.cname,b.bname,c.loc,b.cutoff,b.fees,b.seats from college c,branch b where b.cutoff>=%s and c.cid=b.cid;',rank)
    college=cursor.fetchall()
    return render_template('search.html',roll=roll,rank=rank,college=college,branch=branch,loc=loc)



####################################### student update page #########################################

@app.route('/student_update/<roll>',methods=['GET','POST'])
@is_logged_in
def student_update(roll):

    if request.method=='POST':
        update_details=request.form
        new_pass=update_details['password']
        new_email=update_details['email']
        new_phno=update_details['phno']
        cursor.execute('update student set email=%s where roll_no=%s;',(new_email,roll))
        conn.commit()
        cursor.execute('update student set pass=%s where roll_no=%s;', (new_pass, roll))
        conn.commit()
        cursor.execute('update student set phno=%s where roll_no=%s;', (new_phno, roll))
        conn.commit()
        return 'update aithu'



    cursor.execute('select roll_no,sname,pass,email,phno,rank from student where roll_no=%s;',roll)
    data=cursor.fetchall()
    sname=data[0][1]
    password=data[0][2]
    email=data[0][3]
    phno=data[0][4]
    rank=data[0][5]
    return render_template('student_update.html',roll=roll,sname=sname,password=password,email=email,phno=phno,rank=rank)

######################################student final page ##########################################

@app.route('/student_final/<cid>/<bname>/<roll>')
@is_logged_in
def student_final(cid,bname,roll):
    print(cid,bname,roll)
    cursor.execute('select roll_no from student where cid is not null and roll_no=%s;',roll)
    new_roll=cursor.fetchone()
    if new_roll:
        new_roll=new_roll[0]
        message=' nimdu entry already agide'
        return render_template('student_final.html', new_roll=new_roll,message=message)
    else:
        cursor.execute('update student set cid=%s where roll_no=%s;', (cid, roll))
        conn.commit()
        cursor.execute('update student set bname=%s where roll_no=%s;', (bname, roll))
        conn.commit()

        return render_template('student_final.html', cid=cid, bname=bname, roll=roll)



#######################################college login page #########################################

@app.route('/college_login/', methods=['GET', 'POST'])
def college_login():
    print('hai')
    if request.method =='POST':
        clogin_details=request.form
        cid=clogin_details['coll_id']
        cpass=clogin_details['password']
        try:
            cursor.execute("select cpass from college where cid=%s;", cid)
            data = cursor.fetchone()
            dcpass = data[0]
            if cpass == dcpass:
                print("hello")
                session['logged_in'] = True
                session['username'] = cid
                flash('you are logged in', 'success')
                return redirect(url_for('college_main', cid=cid))
            else:
                message = "invalid password"
                return render_template('college_login.html', message=message)

        except:
            message = 'invalid college id'
            return render_template('college_login.html', message=message)
    message='login with college id and password'
    return render_template('college_login.html',message=message)


#######################################college main#################################################


@app.route('/college_main/<cid>',methods=['GET','POST'])
@is_logged_in
def college_main(cid):

    cursor.execute("select * from student where cid=%s;",cid)
    students=cursor.fetchall()
    print(students)
    return render_template('college_main.html', cid=cid,students=students)



#######################################college info#################################################


@app.route('/college_info/<cid>',methods=['GET','POST'])
@is_logged_in
def college_info(cid):
    if request.method=='POST':
        update_details=request.form
        form_no = int(update_details['submit'])
        password = update_details['password']
        email = update_details['email']
        cursor.execute('update college set cpass=%s,cemail=%s where cid=%s',
                       (password, email, cid))
        conn.commit()
    cursor.execute('select * from college where cid=%s;',cid)
    college_data=cursor.fetchall()
    return render_template('college_info.html',cid=cid,cdata=college_data)

#######################################branch info#################################################

@app.route('/branch_info/<cid>',methods=['GET','POST'])
@is_logged_in
def branch_info(cid):
    if request.method == 'POST':
        update_details = request.form
        form_no = int(update_details['submit'])
        if form_no==1:
            seats = int(update_details['seats'])
            cut_off = int(update_details['cut_off'])
            fees = int(update_details['fees'])
            bname = str(update_details['dep'])
            form_no = int(update_details['submit'])
            print(seats, cut_off, fees, bname, form_no)
            cursor.execute('update branch set seats=%s,cutoff=%s,fees=%s where bname=%s and cid=%s;',
                           (seats, cut_off, fees, bname, cid))
            conn.commit()
            # conn.rollback()
            return redirect(url_for('branch_info', cid=cid))
        elif form_no==2:
            bname=str(update_details['bname'])
            seats = int(update_details['seats'])
            cut_off = int(update_details['cut_off'])
            fees=int(update_details['fees'])
            cursor.execute('insert into branch(cid,bname,seats,cutoff,fees) values(%s,%s,%s,%s,%s)',
                           (cid,bname,seats,cut_off,fees))
            conn.commit()

            print(cid,bname,seats,cut_off,fees,cid)
            return redirect(url_for('branch_info', cid=cid))


    cursor.execute('select bname,seats,cutoff,fees from branch where cid=%s;', cid)
    branch_data = cursor.fetchall()

    return render_template('branch_info.html', cid=cid, bdata=branch_data)


####################################### admin login page #########################################

@app.route('/admin_login/',methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        login_details=request.form
        id=login_details['id']
        password=login_details['password']
        try:
            cursor.execute("select password from admin where id=%s;", id)
            data = cursor.fetchone()
            dpass = data[0]
            if password == dpass:
                session['logged_in'] = True
                session['username'] = id
                flash('you are logged in', 'success')
                return redirect(url_for('admin_main', id=id))
            else:
                message = 'incorrect password!!!'
                return render_template('admin_login.html', message=message)
        except:
            message = 'invalid admin name or password.'
            return render_template('admin_login.html',message=message)
    message='login with admin name password.'
    return render_template('admin_login.html',message=message)

########################################### ADMIN MAIN   ########################################

@app.route('/admin_main/<id>/')
@is_logged_in
def admin_main(id):
    cursor.execute("select name from admin where id=%s;", id)
    data = cursor.fetchone()
    name = data[0]
    return render_template('admin_main.html',name=name)

########################################### ADMIN STUDENT  ########################################


@app.route('/admin_student/<roll>',methods=['GET','POST'])
@is_logged_in
def admin_student(roll):
    print("hai")
    if request.method=='POST':
        print('hai1')
        roll=request.form
        roll=roll['roll']
        print(roll)
        if roll=='all':
            cursor.execute('select * from student;')
            result = cursor.fetchall()
        else:
            cursor.execute('select * from student where roll_no=%s;',roll)
            result=cursor.fetchall()


        return render_template('admin_student.html', roll=roll,result=result)
    cursor.execute('select * from student;')
    result = cursor.fetchall()
    return render_template('admin_student.html',roll=roll,result=result)

########################################### ADMIN COLLEGE   ########################################


@app.route('/admin_college/<cid>',methods=['GET','POST'])
@is_logged_in
def admin_college(cid):
    if request.method=='POST':
        details=request.form
        form_no=int(details['submit'])
        if form_no==1:
            cid = details['cid']
            if cid == 'all':
                cursor.execute('select * from college;')
                result = cursor.fetchall()
                print(1)
            else:
                cid = (cid)
                cursor.execute('select * from college where cid=%s;', cid)
                result = cursor.fetchall()
                print(result)
            return render_template('admin_college.html', cid=cid, result=result)
        elif form_no==2:
            name=details['cname']
            password=details['password']
            cemail=details['email']
            loc=details['loc']
            print(name,password,cemail,loc)
            cursor.execute('insert into college(cname,cpass,cemail,loc) values(%s,%s,%s,%s);',(name,password,cemail,loc))
            conn.commit()
            return redirect(url_for('admin_college',cid=cid))


    cursor.execute('select * from college;')
    result=cursor.fetchall()
    print('aaa')
    return render_template('admin_college.html',cid=cid,result=result)


########################################### admin cetrank ##################################################


@app.route('/admin_cetrank/',methods=['GET','POST'])
@is_logged_in
def admin_cetrank():
    if request.method=='POST':
        new_entry=request.form
        roll=new_entry['roll']
        name=new_entry['sname']
        rank=new_entry['rank']
        cursor.execute("insert into cet_rank(roll_no,sname,rank) values(%s,%s,%s);",(roll,name,rank))
        conn.commit()
        return redirect(url_for('admin_cetrank'))
    cursor.execute("select * from cet_rank;")
    data=cursor.fetchall()
    return render_template('admin_cetrank.html',data=data)




########################################### delete ##################################################

@app.route('/delete/<what>/<id>')
def delete(what,id):
    if what=='student':
        cursor.execute('delete from student where roll_no=%s;',id)
        conn.commit()
        return redirect(url_for('admin_student',roll='all'))
    elif what=='college':
        cursor.execute('delete from college where cid=%s;',id)
        conn.commit()
        return redirect(url_for('admin_college', cid='all'))
    elif what=='rank':
        cursor.execute('delete from cet_rank where roll_no=%s;',id)
        conn.commit()
        return redirect(url_for('admin_cetrank'))

###########################################logout ##################################################

@app.route('/logout')
def logout():
    session.clear()
    flash('you are now logged out')
    return render_template('Main.html')