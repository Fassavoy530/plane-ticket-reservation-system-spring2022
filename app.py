# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql
import js2py
from datetime import datetime

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airline_system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# Change 'O'Hare' to 'O'''Hare'
def sqlsyntax(x):
    if "'" not in x:
        return x
    new = ''
    for i in x:
        if i == "'":
            new += "''"
        else:
            new += i
    return new
################################################
#               Public
################################################
# Define a route to Home page
@app.route('/')
def home_page():
    return render_template('index.html')

# Define route for login
@app.route('/login')
def login():
    return render_template('log_in.html')

# Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

# Define route for checking flights
@app.route('/flight')
def flight():
    return render_template('flight.html')

@app.route('/publicSearchFlight', methods=['GET', 'POST'])
def publicSearchFlight():
    start_date = request.form['departure_date']
    end_date = request.form['arrival_date']
    depart0 = request.form['depart_city_or_airport']
    arrive0 = request.form['arrive_city_or_airport']
    depart = sqlsyntax(depart0)
    arrive = sqlsyntax(arrive0)
    no_flight = None
    cursor = conn.cursor()
    query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
    cursor.execute(query1, (depart))
    data1 = cursor.fetchall()

    if (data1):
        if len(data1) == 1:
            depart_airport = [data1[0]['airport_name']]
        else:
            depart_airport = []
            for airport in data1:
                depart_airport.append(airport['airport_name'])
    else:
        depart_airport = [depart]

    depart_airport_str = "('" + "','".join(depart_airport) + "')"

    query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
    cursor.execute(query2, (arrive))
    data2 = cursor.fetchall()
    if (data2):
        if len(data2) == 1:
            arrive_airport = [data2[0]['airport_name']]
        else:
            arrive_airport = []
            for i in data2:
                arrive_airport.append(i['airport_name'])
    else:
        arrive_airport = [arrive]

    arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

    query3 = "SELECT * FROM flight  \
                          WHERE DATE(departure_time) = %s AND DATE(arrival_time) = %s AND departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str
    cursor.execute(query3, (start_date, end_date))
    flights = cursor.fetchall()
    cursor.close()
    if not (flights):
        no_flight = 1
    return render_template("flight.html", flights=flights, no_flight=no_flight)

@app.route('/publicSearchFlightStatus', methods=['GET', 'POST'])
def publicSearchFlightStatus():
    flight_number = request.form['f_n']
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']

    cursor = conn.cursor()
    query = "SELECT airline_name, flight_num, airplane_id, status \
    			 FROM flight  \
                 WHERE flight_num = %s AND date(departure_time) = %s AND date(arrival_time) = %s"
    cursor.execute(query, (flight_number, departure_date, arrival_date))
    data = cursor.fetchall()
    cursor.close()

    if (data):
        return render_template('flight.html', flights_status=data)
    else:
        error = 'Cannot find the flight!'
        return render_template('flight.html', error2=error)

################################################
#               Airline Staff
################################################
@app.route('/staff_register')
def a_register():
    return render_template('a_register.html')

@app.route('/staff_login')
def a_login():
    return render_template('a_login.html')

# Authenticates the login of customer
@app.route('/aloginAuth', methods=['GET', 'POST'])
def aloginAuth():
    Myfunction = 'function Myfunction() {return (alert("Sign in failed"))}'
    # grabs information from the forms
    username = request.form['username']
    password = request.form['psw']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s and password = md5(%s)'
    cursor.execute(query, (username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row

    if (data):
        # Find the airline name
        query = "SELECT airline_name FROM airline_staff WHERE username = %s"
        cursor.execute(query, (username))
        airline_name = cursor.fetchone()['airline_name']

        query = "SELECT flight_num, airplane_id, airline_name, departure_airport, arrival_airport, departure_time, arrival_time, price\
                     FROM flight\
                     WHERE airline_name = %s AND departure_time BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
        cursor.execute(query, (airline_name))
        flights = cursor.fetchall()
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        cursor.close()
        return render_template('a_home.html', flights = flights, airline_name = airline_name)
        # return redirect(url_for('home'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        cursor.close()
        return render_template('a_login.html', error=error)

#Authenticates the register of airline_staff
@app.route('/aregisterAuth', methods=['GET', 'POST'])
def aregisterAuth():
    #airline_Staff想要更新自己所属航班信息以及其他信息
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['f_name']
    last_name = request.form['l_name']
    date_of_birth = request.form['DOB']
    airline_name = request.form['a_name']
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    # cursor.execute('SELECT * FROM customer WHERE email = %s')
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('a_register.html', error=error)

    query = "SELECT airline_name FROM airline WHERE airline_name = %s"
    cursor.execute(query, (airline_name))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None

    if(data):
        ins = 'INSERT INTO airline_staff VALUES (%s, md5(%s), %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        flash("You have succesfully registered")
        return render_template('a_login.html')
    else:
        error1 = ("This airline doesn't exist")
        return render_template('a_register.html', error=error1)

@app.route('/ahome')
def a_home():
    username = session['username']
    cursor = conn.cursor()
    # Find the airline name
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()['airline_name']

    query = "SELECT flight_num, airplane_id, airline_name, departure_airport, arrival_airport, departure_time, arrival_time, price\
                         FROM flight\
                         WHERE airline_name = %s AND departure_time BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
    cursor.execute(query, (airline_name))
    flights = cursor.fetchall()

    cursor.close()
    return render_template('a_home.html', flights=flights, airline_name=airline_name)

@app.route("/aview")
def a_view():
    return render_template("a_view.html")

@app.route("/aviewshow",methods=['GET', 'POST'])
def a_view_show():
    username = session['username']
    way = request.form['way']
    cursor = conn.cursor()
    no_flight = None
    # Find the airline name
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Search by dates
    if way == 'dates':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        query1 = "SELECT flight_num, airplane_id, airline_name, departure_airport, arrival_airport, departure_time, arrival_time, price\
                  FROM flight\
                  WHERE airline_name = %s AND departure_time >= %s AND arrival_time <= %s"
        cursor.execute(query1, (airline_name, start_date, end_date))
        flights = cursor.fetchall()
        if not (flights):
            no_flight = 1
        return render_template("a_view.html", flights = flights, no_flight = no_flight, airline_name = airline_name, start_date = start_date, end_date = end_date)

    # Search by location
    elif way == 'location':
        depart0 = request.form['depart_city_or_airport']
        arrive0 = request.form['arrive_city_or_airport']
        depart = sqlsyntax(depart0)
        arrive = sqlsyntax(arrive0)

        # If there's city information, detect it and convert it into airport
        cursor = conn.cursor()
        query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
        cursor.execute(query1, (depart))
        data1 = cursor.fetchall()
        # data1 is a list: [{'airport':'a1'}, {'airport':a2}] 注意一个城市可有多个机场

        if (data1):
            if len(data1) == 1:
                depart_airport = [data1[0]['airport_name']]
            else:
                depart_airport = []
                # depart_airport = type(depart_airport)
                for airport in data1:
                    depart_airport.append(airport['airport_name'])
        else:
            depart_airport = [depart]

        depart_airport_str = "('" + "','".join(depart_airport) + "')"

        query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
        cursor.execute(query2, (arrive))
        data2 = cursor.fetchall()
        if (data2):
            if len(data2) == 1:
                arrive_airport = [data2[0]['airport_name']]
            else:
                arrive_airport = []
                for i in data2:
                    arrive_airport.append(i['airport_name'])
        else:
            arrive_airport = [arrive]

        arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

        query3 = "SELECT * FROM flight WHERE departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str + " AND airline_name = %s"
        cursor.execute(query3, (airline_name))
        flights = cursor.fetchall()
        cursor.close()
        if not (flights):
            no_flight = 1
        return render_template("a_view.html", flights = flights, no_flight = no_flight, airline_name = airline_name)

    # Search by location and dates
    elif way == 'both':
        start_date = request.form['start_date1']
        end_date = request.form['end_date1']
        depart0 = request.form['depart_city_or_airport1']
        arrive0 = request.form['arrive_city_or_airport1']
        depart = sqlsyntax(depart0)
        arrive = sqlsyntax(arrive0)


        cursor = conn.cursor()
        query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
        cursor.execute(query1, (depart))
        data1 = cursor.fetchall()

        if (data1):
            if len(data1) == 1:
                depart_airport = [data1[0]['airport_name']]
            else:
                depart_airport = []
                # depart_airport = type(depart_airport)
                for airport in data1:
                    depart_airport.append(airport['airport_name'])
        else:
            depart_airport = [depart]

        depart_airport_str = "('" + "','".join(depart_airport) + "')"

        query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
        cursor.execute(query2, (arrive))
        data2 = cursor.fetchall()
        if (data2):
            if len(data2) == 1:
                arrive_airport = [data2[0]['airport_name']]
            else:
                arrive_airport = []
                for i in data2:
                    arrive_airport.append(i['airport_name'])
        else:
            arrive_airport = [arrive]

        arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

        query3 = "SELECT * FROM flight WHERE airline_name = %s AND departure_time >= %s AND arrival_time <= %s  \
                 AND departure_airport IN " + depart_airport_str  + " AND arrival_airport IN " + arrive_airport_str
        cursor.execute(query3, (airline_name, start_date, end_date))
        flights = cursor.fetchall()
        cursor.close()
        if not (flights):
            no_flight = 1
        return render_template("a_view.html", flights = flights, no_flight = no_flight, airline_name = airline_name, start_date = start_date, end_date = end_date)

    # User did not specify way
    else:
        error = 'Please specify a way to select'
        return render_template("a_view.html", error = error)


    # # Find the airline name
    # query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    # cursor.execute(query, (username))
    # airline_name = cursor.fetchone()['airline_name']
    #
    # query = "SELECT flight_num, airplane_id, airline_name, departure_airport, arrival_airport, departure_time, arrival_time, price\
    #          FROM flight\
    #          WHERE airline_name = %s AND departure_time BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
    # cursor.execute(query, (airline_name))
    # flights = cursor.fetchall()
    # cursor.close()

    return render_template('a_view.html', flights = flights, airline_name = airline_name)

@app.route("/asearchcusbyflight",methods=['GET', 'POST'])
def a_search_cus_by_flight():
    username = session['username']
    flight_num = request.form['flight_num']
    cursor = conn.cursor()

    # Find the airline name
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Check whether flight_number is valid
    query1 = "SELECT * FROM flight WHERE airline_name = %s ANd flight_num = %s"
    cursor.execute(query1, (airline_name, flight_num))
    data = cursor.fetchall()

    if not (data):
        error1 = "Invalid flight number. Please try again"
        return render_template('a_view.html', error1 = error1)

    query2 = "SELECT customer_email, ticket_id FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE airline_name = %s ANd flight_num = %s"
    cursor.execute(query2,(airline_name, flight_num))
    customer = cursor.fetchall()

    cursor.close()
    return render_template('a_view.html', customer = customer)

@app.route("/atwochange",methods=['GET', 'POST'])
def a_change_create_flights():
    username = session['username']
    cursor = conn.cursor()

    # Find the airline name
    query0 = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query0, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Find existing airplane id
    query1 = "SELECT airplane_id FROM airplane WHERE airline_name = %s"
    cursor.execute(query1, (airline_name))
    airplane_id1 = cursor.fetchall()

    if (airplane_id1):
        airplane_id = []
        for i in airplane_id1:
            airplane_id.append(i['airplane_id'])
    else:
        airplane_id = None

    # Find existing flight number
    query2 = "SELECT flight_num FROM flight WHERE airline_name = %s"
    cursor.execute(query2, (airline_name))
    flight_num1 = cursor.fetchall()

    if (flight_num1):
        flight_num = []
        for i in flight_num1:
            flight_num.append(i['flight_num'])
    else:
        flight_num = None

    # Find existing airport
    query3 = "SELECT airport_name FROM airport"
    cursor.execute(query3)
    airport1 = cursor.fetchall()

    if (airport1):
        airport = []
        for i in airport1:
            airport.append(i['airport_name'])
    else:
        airport = None

    # Check permission
    query = "SELECT * FROM permission WHERE username = %s"
    cursor.execute(query, (username))
    data = cursor.fetchall()

    if not (data): # This person does not have any permission
        error = 'Sorry you do not have the permission to create flights or change flight status'
        return render_template("a_change_create_flights.html", admin = None, operator = None, data = data, error = error)
    else:
        per = []
        for i in data:
            per.append(i['permission_type'])
        if 'Admin' in per:
            if 'Operator' in per:
                return render_template("a_change_create_flights.html", admin = 1, operator = 1, data=data, airplane_id = airplane_id, airport = airport, flight_num = flight_num)
            else:
                return render_template("a_change_create_flights.html", admin = 1, operator = None, data = data, airplane_id = airplane_id, airport = airport)
        else:
            return render_template("a_change_create_flights.html", admin = None, operator = 1 , data=data, flight_num = flight_num)

@app.route("/acreate",methods=['GET', 'POST'])
def a_create_flight():
    username = session['username']
    flight_number = request.form['f_n']
    departure_date = request.form['depar_date']
    arrival_date = request.form['arr_date']
    airplaneid = request.form['airp_id']
    arrival_airport = request.form['arrival_airport']
    departure_airport = request.form['depar_airport']
    status = request.form['status']
    price = request.form['price']
    departure_time = request.form['departure_time']
    arrival_time = request.form['arrival_time']
    cursor = conn.cursor()

    # Find the airline name
    query0 = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query0, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Find existing airplane id
    query1 = "SELECT airplane_id FROM airplane WHERE airline_name = %s"
    cursor.execute(query1, (airline_name))
    airplane_id1 = cursor.fetchall()

    if (airplane_id1):
        airplane_id = []
        for i in airplane_id1:
            airplane_id.append(i['airplane_id'])
    else:
        airplane_id = None

    # Find existing airport
    query3 = "SELECT airport_name FROM airport"
    cursor.execute(query3)
    airport1 = cursor.fetchall()

    if (airport1):
        airport = []
        for i in airport1:
            airport.append(i['airport_name'])
    else:
        airport = None

    # Update Permission
    query2 = "SELECT * FROM permission WHERE username = %s"
    cursor.execute(query2, (username))
    data = cursor.fetchall()

    per = []
    for i in data:
        per.append(i['permission_type'])
    if 'Operator' in per:
        admin=1
        operator=1
    else:
        admin=1
        operator=None

    # Check airplane id
    if airplane_id == None:
        error0 = 'Fail to create flight, reason: invalid airplane id'
        return render_template('a_change_create_flights.html', error0=error0, admin = admin , operator = operator, airplane_id = airplane_id, airport = airport)
    # Check airport
    if departure_airport == None:
        error1  = 'Fail to create flight, reason: invalid departure airport'
        return render_template('a_change_create_flights.html', error1=error1, admin = admin , operator = operator, airplane_id = airplane_id, airport = airport)
    if arrival_airport == None:
        error2  = 'Fail to create flight, reason: invalid arrival airport'
        return render_template('a_change_create_flights.html', error2=error2, admin = admin , operator = operator, airplane_id = airplane_id, airport = airport)
    if departure_airport == arrival_airport:
        error3 = 'Fail to create flight, reason: Departure airport and arrival airport are the same'
        return render_template('a_change_create_flights.html', error3=error3, admin = admin , operator = operator, airplane_id = airplane_id, airport = airport)

    # Check flight number
    query = "SELECT flight_num FROM flight WHERE airline_name = %s"
    cursor.execute(query, (airline_name))
    data = cursor.fetchall()
    flights = []
    for i in data:
        flights.append(i['flight_num'])
    if flight_number in flights:
        error4 = 'Fail to create flight, reason: Flight number existed'
        return render_template('a_change_create_flights.html', error4=error4, admin = admin , operator = operator, airplane_id = airplane_id, airport = airport)

    # Check dates
    if departure_date > arrival_date or departure_date < datetime.today().strftime('%Y-%m-%d'):
        error5 = 'Fail to create flight, reason: Invalid departure and arrival time'
        return render_template('a_change_create_flights.html', error4=error5, admin=admin, operator=operator,
                               airplane_id=airplane_id, airport=airport)

    # Insert
    ins = "INSERT INTO flight VALUES (\'{}\', \'{}\', \'{}\', \'{},{}\', \'{}\', \'{}, {}\', \'{}\', \'{}\', \'{}\')"
    cursor.execute(ins.format(airline_name, flight_number, departure_airport, departure_date, departure_time, arrival_airport, arrival_date, arrival_time, price, status, airplaneid))
    conn.commit()
    cursor.close()

    message = "You have successfully create the new flight"
    return render_template('a_change_create_flights.html', message = message, admin = admin ,
                           operator = operator, airplane_id = airplane_id, airport = airport)

@app.route("/achange",methods=["GET","POST"])
def a_change_status():
    username = session['username']
    flight_number = request.form["flight_number"]
    new_status = request.form["newstatus"]
    cursor=conn.cursor()

    # Update Permission
    query2 = "SELECT * FROM permission WHERE username = %s"
    cursor.execute(query2, (username))
    data = cursor.fetchall()

    per = []
    for i in data:
        per.append(i['permission_type'])
    if 'Operator' in per:
        admin = 1
        operator = 1
    else:
        admin = 1
        operator = None

    # Find the airline name
    query0 = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query0, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Find existing flight number
    query2 = "SELECT flight_num FROM flight WHERE airline_name = %s"
    cursor.execute(query2, (airline_name))
    flight_num1 = cursor.fetchall()

    if (flight_num1):
        flight_num = []
        for i in flight_num1:
            flight_num.append(i['flight_num'])
    else:
        flight_num = None

    # Check status
    query = "SELECT status FROM flight WHERE flight_num = %s"
    cursor.execute(query,(flight_number))
    data = cursor.fetchall()
    if new_status == data[0]['status']:
        error6 = 'Update failed, reason: The flight is already in this status'
        return render_template('a_change_create_flights.html', error6=error6, flight_num = flight_num, admin =admin, operator = operator)

    # Update
    ins="Update flight SET status = %s WHERE flight_num = %s"
    cursor.execute(ins, (new_status, flight_number))
    conn.commit()
    cursor.close()
    message2 = 'You have successfully update the status'
    return render_template('a_change_create_flights.html', message2 = message2, flight_num=flight_num, admin=admin, operator=operator)

@app.route("/atwoadd")
def a_add_airplane_airport():
    username = session['username']
    cursor = conn.cursor()

    # Check whether Admin
    query = "SELECT * FROM permission WHERE username = %s"
    cursor.execute(query, (username))
    data = cursor.fetchall()
    cursor.close()

    if not (data):
        error = 'Sorry, you do not have the permission to add airplane or airport' # This person do not have any permission
        return render_template("a_add_airplane_airport.html", error=error, data=None)
    else:
        per = []
        for i in data:
            per.append(i['permission_type'])
        if 'Admin' not in per: # This person is not admin
            error = 'Sorry, you do not have the permission to add airplane or airport'
            return render_template("a_add_airplane_airport.html", error=error, data = None)

    return render_template("a_add_airplane_airport.html", data = data)

@app.route("/aplusairplane",methods=["GET","POST"])
def a_add_airplane():
    username = session['username']
    airplane_id = request.form["airplane"]
    seats = request.form["seats"]
    cursor = conn.cursor()
    data = 1

    # Find the airline name
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Check whether this airplane already exist
    query1 = "SELECT * FROM airplane WHERE airline_name = %s AND airplane_id = %s"
    cursor.execute(query1, (airline_name, airplane_id))
    data2 = cursor.fetchall()

    if (data2):
        error1 = 'This airplane already exists'
        return render_template('a_add_airplane_airport.html', error1 = error1, data=data)


    ins="INSERT INTO airplane VALUES(%s,%s,%s)"
    cursor.execute(ins, (airline_name, airplane_id, seats))
    conn.commit()

    # Find all the airplane
    query2 = "SELECT airplane_id, seats FROM airplane WHERE airline_name = %s"
    cursor.execute(query2, (airline_name))
    airplanes = cursor.fetchall()

    message = "You have successfully add the airplane"
    return render_template('a_add_airplane_airport.html', message = message, data = data, airline_name = airline_name, airplanes = airplanes)

@app.route("/aplusairport",methods=["GET","POST"])
def a_add_airport():
    airport_name = request.form['airport']
    airport_city=request.form["city"]
    data = 1
    cursor=conn.cursor()

    # Check whether the airport exist
    query = "SELECT * FROM airport WHERE airport_name = %s"
    cursor.execute(query, (airport_name))
    data2 = cursor.fetchall()

    if (data2):
        error3 = 'This airport already exists'
        return render_template('a_add_airplane_airport.html', error3 = error3, data=data)

    ins = "INSERT INTO airport VALUES(%s,%s)"
    cursor.execute(ins, (airport_name, airport_city))
    conn.commit()
    cursor.close()

    message2 = ("You have successfully add the airport")
    return render_template('a_add_airplane_airport.html', message2 = message2, data = data)

@app.route('/aviewagent')
def a_view_booking_agent():
    username = session['username']
    cursor = conn.cursor()

    # Top 5 based on num of tickets in the past month
    query1 = "SELECT booking_agent.email, booking_agent_id, COUNT(ticket_id) AS ticket\
            FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket AS t, airline_staff\
            WHERE purchase_date between DATE_ADD(NOW(), INTERVAL -'1' MONTH) and NOW() and username = %s  and t.airline_name = airline_staff.airline_name\
            GROUP BY booking_agent_id \
            ORDER BY COUNT(ticket_id) DESC \
            LIMIT 5"
    cursor.execute(query1,(username))
    top_1m_ticket = cursor.fetchall()

    # Top 5 based on num of tickets in the past year
    query2 = "SELECT booking_agent.email, booking_agent_id, COUNT(ticket_id) AS ticket\
            FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket AS t, airline_staff\
            WHERE purchase_date between DATE_ADD(NOW(), INTERVAL -'12' MONTH) and NOW() and username = %s  and t.airline_name = airline_staff.airline_name\
            GROUP BY booking_agent_id \
            ORDER BY COUNT(ticket_id) DESC \
            LIMIT 5"
    cursor.execute(query2, (username))
    top_12m_ticket = cursor.fetchall()

    # Top 5 based on commission in the last year
    query3 = "SELECT email, booking_agent_id, sum(price) * 0.1 as commission FROM booking_agent NATURAL JOIN purchases \
              NATURAL JOIN flight NATURAL JOIN ticket AS T, airline_staff \
              WHERE username = %s and airline_staff.airline_name = T.airline_name and YEAR(purchase_date) = YEAR(CURDATE())-1 \
              GROUP BY email, booking_agent_id \
              ORDER BY commission DESC \
              LIMIT 5 "
    cursor.execute(query3, (username))
    top_12m_commission = cursor.fetchall()
    cursor.close()
    return render_template("a_booking_agent.html", top_1m_ticket = top_1m_ticket, top_12m_ticket = top_12m_ticket, top_12m_commission = top_12m_commission)

@app.route('/aviewcustomer')
def a_view_customer():
    username = session['username']
    cursor = conn.cursor()

    # Find the most frequent custoemr in the last year
    query = "SELECT customer_email , COUNT(customer_email) as ticket\
            FROM purchases NATURAL JOIN ticket as t, airline_staff\
            WHERE airline_staff.username = %s AND airline_staff.airline_name = t.airline_name AND YEAR(purchase_date) = YEAR(CURDATE())-1\
            GROUP BY customer_email \
            ORDER BY COUNT(customer_email) DESC"
    cursor.execute(query, (username))
    frequent_customer = cursor.fetchall()
    cursor.close()

    # Select customer(s) who have the most ticket numbers
    if frequent_customer:
        max = frequent_customer[0]['ticket']
        frequent_cus = []
        for i in frequent_customer:
            if i['ticket'] != max:
                break
            else:
                frequent_cus.append(i)

        return render_template("a_customers.html", frequent_cus = frequent_cus)
    else:
        error1 = 'Sorry, no tickets was bought in the last year'
        return render_template("a_customers.html", error1 = error1)

@app.route('/aviewcustomerflight', methods=['GET','POST'])
def a_view_customer_flight():
    if session.get('username') and'customer_email' in request.form:
        username = session['username']
        customer_email = request.form['customer_email']
        cursor = conn.cursor()
        error = None
        error2 = None
        # the most frequent custoemr
        query = "SELECT customer_email, COUNT(customer_email) as ticket\
                    FROM purchases NATURAL JOIN ticket as t, airline_staff\
                    WHERE airline_staff.username = %s AND airline_staff.airline_name = t.airline_name AND purchase_date between DATE_ADD(NOW(), INTERVAL -'12' MONTH) and NOW()\
                    GROUP BY customer_email \
                    ORDER BY COUNT(customer_email) DESC"
        cursor.execute(query, (username))
        frequent_customer = cursor.fetchall()

        # Select customer(s) who have the most ticket numbers
        if (frequent_customer):
            max = frequent_customer[0]['ticket']
            frequent_cus = []
            for i in frequent_customer:
                if i['ticket'] != max:
                    break
                else:
                    frequent_cus.append(i)
            error1 = None
        else:
            error1 = 'Sorry, no tickets was bought in the last year'

        # Check whether the customer exist in the database
        query2 = "SELECT * FROM customer WHERE email = %s"
        cursor.execute(query2, (customer_email))
        data = cursor.fetchall()

        if not (data):
            error = "The customer hasn't registered yet"
            return render_template("a_customers.html", frequent_customer=frequent_customer, error = error, error1 = error1)

        # Check flights for certain customer
        query1 = "SELECT * FROM purchases NATURAL JOIN ticket as t JOIN flight using(flight_num), airline_staff\
                    WHERE airline_staff.username = %s AND airline_staff.airline_name = t.airline_name AND customer_email = %s"
        cursor.execute(query1, (username, customer_email))
        customer_flight = cursor.fetchall()

        if not (customer_flight):
            error2 = "No tickets was bought by this customer in the past year"

        return render_template("a_customers.html", frequent_customer = frequent_customer, customer_flight = customer_flight, error = error, error1 = error1, error2=error2)

    else:
        session.clear()
        return render_template('404.html')

@app.route('/adestination', methods=['GET','POST'])
def a_destination():
    username = session['username']
    cursor = conn.cursor()

    # Find the airline name
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Top 3 arrival city in the past 3 months
    ## ??这个city需要和airline staff所在航空一致吗
    query1 = "SELECT airport_city as destination, COUNT(ticket_id)\
            FROM purchases NATURAL JOIN ticket NATURAL JOIN flight as t, airport\
            WHERE t.arrival_airport = airport.airport_name AND purchase_date between DATE_ADD(LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 4 MONTH)), INTERVAL 1 DAY) and LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 1 MONTH)) \
            GROUP BY airport_city\
            ORDER BY COUNT(ticket_id) DESC\
            LIMIT 3"
    cursor.execute(query1)
    city_3m=cursor.fetchall()

    # Top 3 arrival city in the past year
    query2 = "SELECT airport_city as destination, COUNT(ticket_id)\
                FROM purchases NATURAL JOIN ticket NATURAL JOIN flight as t, airport\
                WHERE t.arrival_airport = airport.airport_name AND YEAR(purchase_date) = YEAR(CURDATE())-1 \
                GROUP BY airport_city\
                ORDER BY COUNT(ticket_id) DESC\
                LIMIT 3"
    cursor.execute(query2)
    city_12m = cursor.fetchall()


    return render_template("a_destination.html", city_3m=city_3m, city_12m=city_12m )

@app.route('/areport')
def a_report():
    return render_template("a_report.html")

@app.route('/areportshow', methods = ['GET','POST'])
def a_show_report():
    username = session['username']
    cursor = conn.cursor()
    time_way = request.form['time']

    if time_way == 'month':
        # 1-1 Total Amount of tickets in last month
        # Check whether there is tickets
        query0 = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight as t, airline_staff \
                 WHERE airline_staff.username = %s AND t.airline_name = airline_staff.airline_name \
                 AND purchase_date BETWEEN DATE_ADD(LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 2 MONTH)), INTERVAL 1 DAY) and LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 1 MONTH))"
        cursor.execute(query0, (username))
        data = cursor.fetchone()
        if data is None:
            tot_month = 1
            error = 'No tickets Sold in the last month'
            return render_template("a_report.html", tot_month=tot_month, time_way=time_way, error = error)

        query = "SELECT COUNT(ticket_id) as ticket , MONTH(CURDATE())-1 as month FROM ticket NATURAL JOIN purchases NATURAL JOIN airline_staff WHERE username = %s AND purchase_date BETWEEN DATE_ADD(LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 2 MONTH)), INTERVAL 1 DAY) and LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 1 MONTH))"
        cursor.execute(query, (username))
        tot_month= cursor.fetchone()['ticket']
        return render_template("a_report.html", tot_month=tot_month)

    elif time_way == 'year':
        # 2-1 Total Amount of tickets in last year
        # Check whether there is tickets
        query0 = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight as t, airline_staff \
                         WHERE airline_staff.username = %s AND t.airline_name = airline_staff.airline_name \
                         AND YEAR(purchase_date) = YEAR(CURDATE())-1"
        cursor.execute(query0, (username))
        data = cursor.fetchone()
        if data is None:
            tot_year = 1
            error1 = 'No tickets Sold in the last year'
            return render_template("a_report.html", tot_year=tot_year, error1=error1)

        query2= "SELECT COUNT(ticket_id) as ticket FROM ticket NATURAL JOIN purchases NATURAL JOIN airline_staff WHERE username = %s AND YEAR(purchase_date) = YEAR(CURDATE())-1"
        cursor.execute(query2,(username))
        tot_year = cursor.fetchone()['ticket']

        # 2-2 Each month ticket in last year
        t_each_month = []
        month_name=['January','February','March','April','May','June','July','August','September','October','November','December']
        for i in range (1,13):
            query3 = "SELECT COUNT(ticket_id) as ticket FROM ticket NATURAL JOIN purchases NATURAL JOIN airline_staff WHERE username = %s AND YEAR(purchase_date) = YEAR(CURDATE())-1 AND MONTH(purchase_date) = " + str(i)
            cursor.execute(query3,(username))
            data1 = {}
            data1['Month'] = month_name[i-1]
            data1['Tickets'] = cursor.fetchone()['ticket']
            t_each_month.append(data1)
        return render_template("a_report.html", tot_year=tot_year, t_each_month= t_each_month)

    # 3-1 Total Amount of tickets in the date range
    else:
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        query3 = "SELECT COUNT(ticket_id) as ticket FROM ticket NATURAL JOIN purchases NATURAL JOIN airline_staff WHERE username = %s AND purchase_date BETWEEN %s AND %s"
        cursor.execute(query3,(username, start_date, end_date))
        tot_date = cursor.fetchone()['ticket']

        # Check whether there is tickets
        query0 = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight as t, airline_staff \
                                 WHERE airline_staff.username = %s AND t.airline_name = airline_staff.airline_name \
                                 AND  purchase_date BETWEEN %s AND %s "
        cursor.execute(query0, (username, start_date, end_date))
        data = cursor.fetchone()
        if data is None:
            tot_date = 1
            error2 = 'No tickets Sold during ' + start_date + ' and ' + end_date
            return render_template("a_report.html", tot_date=tot_date, error2=error2)

    # 3-3 tickets in each month
        query4 ="SELECT COUNT(ticket_id) as ticket, YEAR(purchase_date) as year, MONTH(purchase_date) as month \
                 FROM ticket NATURAL JOIN purchases NATURAL JOIN airline_staff WHERE username = %s AND purchase_date BETWEEN %s AND %s \
                GROUP BY MONTH(purchase_date), YEAR(purchase_date)"
        #[{'ticket': 7, 'year': 2022, 'month': 4}, {'ticket': 20, 'year': 2022, 'month': 5}]
        #convert it into {2022-04: 7, 2022-05: 20}  x轴：2022-04-11 - 2022-4-30， 2022-05-01 - 2022-05-22
        cursor.execute(query4,(username, start_date, end_date))
        tot_date_each_month = cursor.fetchall()
        t_date_each_month = []
        for i in tot_date_each_month:
            data={}
            data['Month'] = str(i['year'])+'-'+str(i['month'])
            data['Tickets'] = i['ticket']
            t_date_each_month.append(data)
        return render_template("a_report.html", tot_date = tot_date, t_date_each_month = t_date_each_month, start_date=start_date, end_date=end_date)

@app.route('/arevenue')
def a_revenue():
    username = session['username']
    cursor = conn.cursor()

    # Find the airline name
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()['airline_name']

    cursor.close()
    return render_template("a_revenue.html", airline_name = airline_name)

@app.route('/arevenueshow', methods = ['GET','POST'])
def a_revenue_show():
    username = session['username']
    cursor = conn.cursor()
    time = request.form['time']

    # Find the airline name
    query = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Revenue from last month
    if time == 'month':
        error1 = None
        # Customer Money
        query = "SELECT SUM(price) as revenue_cus FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE airline_name = %s AND booking_agent_id IS NULL  \
                AND purchase_date BETWEEN DATE_ADD(LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 2 MONTH)), INTERVAL 1 DAY) and LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 1 MONTH)) "
        cursor.execute(query, airline_name)
        r_month_cus = cursor.fetchone()['revenue_cus']  #int

        # Booking Money 减去agent10%提成
        query1 = "SELECT SUM(price)*0.9 as revenue_agent FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE airline_name = %s AND booking_agent_id IS NOT NULL  \
                AND purchase_date BETWEEN DATE_ADD(LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 2 MONTH)), INTERVAL 1 DAY) and LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 1 MONTH)) "
        cursor.execute(query1, airline_name)
        r_month_agent = cursor.fetchone()['revenue_agent']

        if r_month_cus == r_month_agent == None:
            error1 = "No revenue from agents and customers in " + airline_name + 'during the last month'

        return render_template("a_revenue.html", r_month_cus = r_month_cus, r_month_agent = r_month_agent, error1 = error1)

    # Revenue from last year
    elif time == 'year':
        # Customer Money
        error = None
        query2 = "SELECT SUM(price) as revenue_cus FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE airline_name = %s AND booking_agent_id IS NULL  \
                AND YEAR(purchase_date) = YEAR(CURDATE())-1"
        cursor.execute(query2, airline_name)
        r_year_cus = cursor.fetchone()['revenue_cus']

        # Booking Money 减去agent10%提成
        query3 = "SELECT SUM(price)*0.9 as revenue_agent FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE airline_name = %s AND booking_agent_id IS NOT NULL  \
                AND YEAR(purchase_date) = YEAR(CURDATE())-1"
        cursor.execute(query3, airline_name)
        r_year_agent = cursor.fetchone()['revenue_agent']

        if r_year_cus == r_year_agent == None:
            error = "No revenue from agents and customers in " + airline_name + 'during the last year'

        return render_template("a_revenue.html", r_year_cus = r_year_cus, r_year_agent = r_year_agent, error = error)

@app.route('/apermission', methods=['GET','POST'])
def a_permission():
    username = session['username']
    cursor = conn.cursor()

    # Check whether Admin
    query = "SELECT * FROM permission WHERE username = %s"
    cursor.execute(query, (username))
    data = cursor.fetchall()

    if not (data):
        error = 'Sorry, you do not have the permission to grant permmission' # This person do not have any permission
        return render_template("a_permission.html", error=error, data=None)
    else:
        per = []
        for i in data:
            per.append(i['permission_type'])
        if 'Admin' not in per: # This person is not admin
            error = 'Sorry, you do not have the permission to grant permmission'
            return render_template("a_permission.html", error=error, data = None)

    return render_template("a_permission.html", data=data)

@app.route('/apermissionstart', methods=['GET','POST'])
def a_permission_start():
    username = session['username']
    staff_username = request.form['staff_username']
    permission_type = request.form['permission_type']
    cursor = conn.cursor()
    data = 1

    # Check whether staff_email is valid
    query1 = "SELECT * FROM airline_staff WHERE username = %s"
    cursor.execute(query1, (staff_username))
    data2 = cursor.fetchone()

    if not (data2):
        error2 = "The staff hasn't registered yet"
        return render_template("a_permission.html", data=data, error2=error2)

    # Find the airline name
    query2 = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query2, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Check whether staff in the same airline
    query3 = "SELECT username FROM airline_staff WHERE username = %s AND airline_name = %s"
    cursor.execute(query3, (staff_username, airline_name))
    data3 = cursor.fetchone()

    if not (data3):
        error3 = "You can only grant permission to staff in the same airline as you do"
        return render_template("a_permission.html", data=data, error3=error3)


    # Check whether this is duplicate insert
    query4 = "SELECT username FROM permission WHERE username = %s AND permission_type = %s"
    cursor.execute(query4,(staff_username,permission_type))
    data4 = cursor.fetchone()

    if (data4):
        error4 = 'This staff already had this permission'
        return render_template("a_permission.html", data=data, error4 =error4)
    # Inset permission type
    #重复insert报错
    ins = "INSERT INTO permission VALUES (%s, %s)"
    cursor.execute(ins, (staff_username, permission_type))
    conn.commit()
    cursor.close()
    message = 'Permission Granted Successfully!'

    return render_template("a_permission.html", data=data, data3=data3, message = message)

@app.route('/aaddagent')
def a_add_booking_agent():
    username = session['username']
    cursor = conn.cursor()

    # Check whether Admin
    query = "SELECT * FROM permission WHERE username = %s"
    cursor.execute(query, (username))
    data = cursor.fetchall()

    if not (data):
        error = 'Sorry, you do not have the permission to add booking agent'  # This person do not have any permission
        return render_template("a_add_booking_agent.html", error=error, data=None)
    else:
        per = []
        for i in data:
            per.append(i['permission_type'])
        if 'Admin' not in per:  # This person is not admin
            error = 'Sorry, you do not have the permission to add booking agent'
            return render_template("a_add_booking_agent.html", error=error, data=None)

    # Find the airline that this staff work for
    query2 = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query2, (username))
    airline_name = cursor.fetchone()['airline_name']
    cursor.close()

    return render_template("a_add_booking_agent.html", data=data, airline = airline_name)

@app.route('/aaddagentstart', methods=['GET', 'POST'])
def a_add_booking_agent_start():
    username = session['username']
    booking_agent_email = request.form['booking_agent_email']
    data=1
    cursor = conn.cursor()

    # Find the airline that this staff work for
    query2 = "SELECT airline_name FROM airline_staff WHERE username = %s"
    cursor.execute(query2, (username))
    airline_name = cursor.fetchone()['airline_name']

    # Check whether this agent has registered
    query = "SELECT * FROM booking_agent WHERE email = %s"
    cursor.execute(query, (booking_agent_email))
    data1 = cursor.fetchone()

    if not (data1):
        error1  = "This booking agent hasn't registered yet"
        return render_template("a_add_booking_agent.html", error1 = error1, data = data, airline = airline_name)

    # Check whether this agent has already worked for the airline
    query2 = "SELECT airline_name FROM booking_agent_work_for WHERE email = %s AND airline_name = %s"
    cursor.execute(query2, (booking_agent_email, airline_name))
    data2 = cursor.fetchone()

    if (data2):
        error2 = "This booking agent has already worked for " + airline_name
        return render_template("a_add_booking_agent.html", error2=error2, data=data, airline=airline_name)

    ins = "INSERT INTO booking_agent_work_for VALUES (%s, %s)"
    cursor.execute(ins, (booking_agent_email, airline_name))
    conn.commit()
    cursor.close()

    message = "This agent has been succussfully add to the airline"
    return render_template("a_add_booking_agent.html", message = message, data=data, airline = airline_name)

################################################
#               Booking Agent
################################################
@app.route('/booking_agent_register')
def b_register():
    return render_template('b_register.html')

@app.route('/booking_agent_login')
def b_login():
    return render_template('b_login.html')

# Authenticates the login of customer
@app.route('/bloginAuth', methods=['GET', 'POST'])
def bloginAuth():
    if 'email' in request.form and 'psw' in request.form:
        email = request.form['email']
        password = request.form['psw']

        cursor = conn.cursor()
        query = 'SELECT * FROM booking_agent WHERE email = %s and password = md5(%s)'
        cursor.execute(query, (email, password))
        data = cursor.fetchone()
        error = None

        if (data):
            query1 = "SELECT * \
                     FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent JOIN flight USING (flight_num) \
                     WHERE booking_agent.email = %s AND flight.status ='Upcoming'"
            cursor.execute(query1,(email))
            data1 = cursor.fetchall()
            query2 = "SELECT airline_name FROM booking_agent_work_for WHERE email = %s"
            cursor.execute(query2,(email))
            data2 = cursor.fetchall()
            cursor.close()
            session['email'] = email
            return render_template('b_home.html', flights = data1, email = email, airlines_work_for = data2)
        else:
            error = 'Invalid login or username'
            return render_template('b_login.html', error=error)
    else:
        session.clear()
        return render_template('404.html')

#Authenticates the register of booking agent
@app.route('/bregisterAuth', methods=['GET', 'POST'])
def bregisterAuth():
    # if session.get('email') and 'psw' in request.form and 'B_ID' in request.form:
        email = request.form['email']
        password = request.form['password']
        booking_agent_id =request.form['B_ID']

        cursor = conn.cursor()
        query = 'SELECT * FROM booking_agent WHERE email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()


        query2 = 'SELECT * FROM booking_agent WHERE booking_agent_id = %s'
        cursor.execute(query2, (booking_agent_id))
        data2 = cursor.fetchone()

        if data is not None and data2 is None:
            # If the previous query returns data, then user exists
            error = "This user already exists: Invalid Email"
            return render_template('b_register.html', error=error)
        elif data is None and data2 is not None:
            error1 = "This user already exists: Invalid Booking Agent ID"
            return render_template('b_register.html', error1=error1)
        elif data is not None and data2 is not None:
            error2 = "This user already exists: Invalid Email and Booking Agent ID"
            return render_template('b_register.html', error2=error2)
        else:
            ins = "INSERT INTO booking_agent VALUES(%s, md5(%s), %s)"
            cursor.execute(ins, (email, password, booking_agent_id))
            conn.commit()
            cursor.close()
            flash("You have succesfully registered")
            return render_template('b_login.html')
    # else:
    #     session.clear()
    #     return render_template('404.html')

@app.route('/bhome')
def b_home():
    if session.get('email'):
        email = session['email']

        cursor = conn.cursor()
        query1 = "SELECT * \
                         FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent JOIN flight USING (flight_num) \
                         WHERE booking_agent.email = %s AND flight.status ='Upcoming'"
        cursor.execute(query1, (email))
        data1 = cursor.fetchall()
        query2 = "SELECT airline_name FROM booking_agent_work_for WHERE email = %s"
        cursor.execute(query2, (email))
        data2 = cursor.fetchall()
        cursor.close()
        return render_template('b_home.html', flights=data1, email=email, airlines_work_for=data2)
    else:
        session.clear()
        return render_template('404.html')

@app.route("/bview")
def b_view():
    return render_template("b_view.html")

@app.route("/bviewshow",methods=['GET', 'POST'])
def b_view_show():
    email = session['email']
    way = request.form['way']
    cursor = conn.cursor()
    no_flight = None


    # Search by dates
    if way == 'dates':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        query1 = "SELECT * \
                  FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent JOIN flight USING (flight_num) \
                  WHERE booking_agent.email = %s AND flight.status ='Upcoming' AND departure_time >= %s AND arrival_time <= %s"
        cursor.execute(query1, (email, start_date, end_date))
        flights = cursor.fetchall()
        if not (flights):
            no_flight = 1
        return render_template("b_view.html", flights=flights, no_flight=no_flight)

    # Search by location
    elif way == 'location':
        depart0 = request.form['depart_city_or_airport']
        arrive0 = request.form['arrive_city_or_airport']
        depart = sqlsyntax(depart0)
        arrive = sqlsyntax(arrive0)

        # If there's city information, detect it and convert it into airport
        cursor = conn.cursor()
        query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
        cursor.execute(query1, (depart))
        data1 = cursor.fetchall()
        # data1 is a list: [{'airport':'a1'}, {'airport':a2}] 注意一个城市可有多个机场

        if (data1):
            if len(data1) == 1:
                depart_airport = [data1[0]['airport_name']]
            else:
                depart_airport = []
                # depart_airport = type(depart_airport)
                for airport in data1:
                    depart_airport.append(airport['airport_name'])
        else:
            depart_airport = [depart]

        depart_airport_str = "('" + "','".join(depart_airport) + "')"

        query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
        cursor.execute(query2, (arrive))
        data2 = cursor.fetchall()
        if (data2):
            if len(data2) == 1:
                arrive_airport = [data2[0]['airport_name']]
            else:
                arrive_airport = []
                for i in data2:
                    arrive_airport.append(i['airport_name'])
        else:
            arrive_airport = [arrive]

        arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

        query3 = "SELECT * \
                  FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent JOIN flight USING (flight_num) \
                  WHERE booking_agent.email = %s AND departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str + " AND status = 'Upcoming'"
        cursor.execute(query3, (email))
        flights = cursor.fetchall()
        cursor.close()
        if not (flights):
            no_flight = 1
        return render_template("b_view.html", flights=flights, no_flight=no_flight)

    # Search by location and dates
    elif way == 'both':
        start_date = request.form['start_date1']
        end_date = request.form['end_date1']
        depart0 = request.form['depart_city_or_airport1']
        arrive0 = request.form['arrive_city_or_airport1']
        depart = sqlsyntax(depart0)
        arrive = sqlsyntax(arrive0)

        cursor = conn.cursor()
        query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
        cursor.execute(query1, (depart))
        data1 = cursor.fetchall()

        if (data1):
            if len(data1) == 1:
                depart_airport = [data1[0]['airport_name']]
            else:
                depart_airport = []
                # depart_airport = type(depart_airport)
                for airport in data1:
                    depart_airport.append(airport['airport_name'])
        else:
            depart_airport = [depart]

        depart_airport_str = "('" + "','".join(depart_airport) + "')"

        query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
        cursor.execute(query2, (arrive))
        data2 = cursor.fetchall()
        if (data2):
            if len(data2) == 1:
                arrive_airport = [data2[0]['airport_name']]
            else:
                arrive_airport = []
                for i in data2:
                    arrive_airport.append(i['airport_name'])
        else:
            arrive_airport = [arrive]

        arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

        query3 = "SELECT * \
                  FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent JOIN flight USING (flight_num) \
                  WHERE booking_agent.email = %s AND departure_time >= %s AND arrival_time <= %s AND status = 'Upcoming' AND departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str
        cursor.execute(query3, (email, start_date, end_date))
        flights = cursor.fetchall()
        cursor.close()
        if not (flights):
            no_flight = 1
        return render_template("b_view.html", flights=flights, no_flight=no_flight)

    # User did not specify way
    else:
        error = 'Please specify a way to select'
        return render_template("b_view.html", error=error)

@app.route('/bsearch_purchase')
def b_search_purchase():
    if session.get('email'):
        email = session['email']
        cursor = conn.cursor()
        query1 = "SELECT airline_name FROM booking_agent_work_for WHERE email = %s"
        cursor.execute(query1, (email))
        data1 = cursor.fetchall()

        if (data1):
            airline = []
            for i in data1:
                airline.append(i['airline_name'])

            airline_for_agent = "('" + "','".join(airline) + "')"
            # data2 is the flight number of airline (UPCOMING)
            query2 = "SELECT flight_num FROM flight WHERE airline_name IN " + airline_for_agent
            cursor.execute(query2)
            data2 = cursor.fetchall()
        else:
            data2 = None
        cursor.close()
        return render_template('b_search_purchase.html', airlines_work_for=data1, flights_for_airlines = data2)
    else:
        session.clear()
        return render_template('404.html')


@app.route('/bsearch', methods=['GET', 'POST'])
def b_search():
    if session.get('email') and 'way' in request.form:
        way = request.form['way']
        cursor = conn.cursor()
        no_flight = None

        email = session['email']
        query4 = "SELECT airline_name FROM booking_agent_work_for WHERE email = %s"
        cursor.execute(query4, (email))
        data4 = cursor.fetchall()

        if (data4):
            airline = []
            for i in data4:
                airline.append(i['airline_name'])

            airline_for_agent = "('" + "','".join(airline) + "')"
            query5 = "SELECT flight_num FROM flight WHERE airline_name IN " + airline_for_agent
            cursor.execute(query5)
            data5 = cursor.fetchall()
        else:
            data5 = None

        # Search by dates
        if way == 'dates':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            query1 = "SELECT *\
                              FROM flight \
                              WHERE departure_time >= %s AND arrival_time <= %s AND status = 'Upcoming'"
            cursor.execute(query1, (start_date, end_date))
            flights = cursor.fetchall()
            if not (flights):
                no_flight = 1
            return render_template("b_search_purchase.html", flights=flights, no_flight=no_flight, airlines_work_for=data4, flights_for_airlines = data5)

        # Search by location
        elif way == 'location':
            depart0 = request.form['depart_city_or_airport']
            arrive0 = request.form['arrive_city_or_airport']
            depart = sqlsyntax(depart0)
            arrive = sqlsyntax(arrive0)

            cursor = conn.cursor()
            query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query1, (depart))
            data1 = cursor.fetchall()

            if (data1):
                if len(data1) == 1:
                    depart_airport = [data1[0]['airport_name']]
                else:
                    depart_airport = []
                    # depart_airport = type(depart_airport)
                    for airport in data1:
                        depart_airport.append(airport['airport_name'])
            else:
                depart_airport = [depart]

            depart_airport_str = "('" + "','".join(depart_airport) + "')"

            query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query2, (arrive))
            data2 = cursor.fetchall()
            if (data2):
                if len(data2) == 1:
                    arrive_airport = [data2[0]['airport_name']]
                else:
                    arrive_airport = []
                    for i in data2:
                        arrive_airport.append(i['airport_name'])
            else:
                arrive_airport = [arrive]

            arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

            query3 = "SELECT * FROM flight\
                              WHERE departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str + " AND status = 'Upcoming'"
            cursor.execute(query3)
            flights = cursor.fetchall()
            cursor.close()
            if not (flights):
                no_flight = 1
            return render_template("b_search_purchase.html", flights=flights, no_flight=no_flight, airlines_work_for=data4, flights_for_airlines = data5)
        # Search by location and dates
        elif way == 'both':
            start_date = request.form['start_date1']
            end_date = request.form['end_date1']
            depart0 = request.form['depart_city_or_airport1']
            arrive0 = request.form['arrive_city_or_airport1']
            depart = sqlsyntax(depart0)
            arrive = sqlsyntax(arrive0)

            cursor = conn.cursor()
            query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query1, (depart))
            data1 = cursor.fetchall()

            if (data1):
                if len(data1) == 1:
                    depart_airport = [data1[0]['airport_name']]
                else:
                    depart_airport = []
                    # depart_airport = type(depart_airport)
                    for airport in data1:
                        depart_airport.append(airport['airport_name'])
            else:
                depart_airport = [depart]

            depart_airport_str = "('" + "','".join(depart_airport) + "')"

            query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query2, (arrive))
            data2 = cursor.fetchall()
            if (data2):
                if len(data2) == 1:
                    arrive_airport = [data2[0]['airport_name']]
                else:
                    arrive_airport = []
                    for i in data2:
                        arrive_airport.append(i['airport_name'])
            else:
                arrive_airport = [arrive]

            arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

            query3 = "SELECT * FROM flight  \
                              WHERE departure_time >= %s AND arrival_time <= %s AND status = 'Upcoming' AND departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str
            cursor.execute(query3, (start_date, end_date))
            flights = cursor.fetchall()
            cursor.close()
            if not (flights):
                no_flight = 1
            return render_template("b_search_purchase.html", flights=flights, no_flight=no_flight, airlines_work_for=data4, flights_for_airlines = data5)

        # User did not specify way
        else:
            error = 'Please specify a way to select'
            return render_template("b_search_purchase.html", error=error)
    else:
        session.clear()
        return render_template('404.html')


@app.route('/bpurchase', methods=['GET', 'POST'])
def b_purchase():
    # Delay flight的可以买吗
    if session.get('email') and 'customer_email' in request.form:
        email = session['email']
        airline_name = request.form.get("airline_name")
        flight_num = request.form.get("flight_number")
        customer_email = request.form['customer_email']
        cursor = conn.cursor()

        # Get airline_works_for, flights_for_airlines to make sure one can purchase multiple times
        query0 = "SELECT airline_name FROM booking_agent_work_for WHERE email = %s"
        cursor.execute(query0, (email))
        data0 = cursor.fetchall()
        if (data0):
            airline = []
            for i in data0:
                airline.append(i['airline_name'])

            airline_for_agent = "('" + "','".join(airline) + "')"
            # data4 is the flight number of airline (UPCOMING)
            query4 = "SELECT flight_num FROM flight WHERE airline_name IN " + airline_for_agent
            cursor.execute(query4)
            data4 = cursor.fetchall()

        #Validate flight
        query = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s"
        cursor.execute(query, (airline_name, flight_num))
        data = cursor.fetchall()
        if not (data):
            error0 = "The flight doesn't exist or it is not in upcoming status, please try again"
            return render_template ('b_search_purchase.html', error1 = error0, airlines_work_for=data0, flights_for_airlines=data4)

        # Find booking agent ID
        #?? Validate Booking Agent
        query1 = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(query1, (email))
        data1 = cursor.fetchone()
        booking_agent = data1['booking_agent_id'] #int

        # Validate customer
        query2 = "SELECT * FROM customer WHERE email = %s"
        cursor.execute(query2, (customer_email))
        data2 = cursor.fetchone()
        if not (data2):
            error1 = "The customer hasn't registered yet"
            return render_template('b_search_purchase.html', error1=error1, airlines_work_for=data0, flights_for_airlines=data4)

        # Validate Flight Date
        query5 = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND departure_time < CURDATE()"
        cursor.execute(query5, (airline_name, flight_num))
        data5 = cursor.fetchall()
        if (data5):
            error2 = "The flight is not in the upcoming status"
            return render_template('b_search_purchase.html', error2=error2, airlines_work_for=data0, flights_for_airlines=data4)

        # Set New Ticket ID
        query3 = "SELECT max(ticket_id) FROM ticket"
        cursor.execute(query3)
        data3 = cursor.fetchone()
        new_ticket_id = data3['max(ticket_id)']+1

        # Insert a new ticket
        ins1 = "INSERT INTO ticket VALUES (%s, %s, %s)"
        cursor.execute(ins1, (new_ticket_id, airline_name, flight_num))

        # Insert a new purchase
        ins2 = "INSERT INTO purchases VALUES (%s, %s, %s, CURDATE())"
        cursor.execute(ins2, (new_ticket_id, customer_email, booking_agent))
        conn.commit()
        cursor.close()
        message1 = 'Purchase Successfully!'
        return render_template('b_search_purchase.html', message = message1, airlines_work_for=data0, flights_for_airlines=data4)
    else:
        session.clear()
        return render_template('404.html')


@app.route('/bcommission')
def b_commission():
    if session.get('email'):
        email = session['email']

        cursor = conn.cursor()
        #Find the booking agent id
        query1 = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(query1, (email))
        data1 = cursor.fetchone()
        booking_agent = data1['booking_agent_id']  # int

        #Default: Find the total price/ average price/ tickets sold
        query2 = "SELECT sum(price)*0.1, avg(price)*0.1, count(ticket_id) \
                FROM ticket NATURAL JOIN purchases NATURAL JOIN flight \
                WHERE booking_agent_id = %s AND purchase_date between DATE_ADD(NOW(), INTERVAL -'30' DAY) and NOW()"
        cursor.execute(query2, (booking_agent))
        data2 = cursor.fetchone()
        cursor.close()
        total_comm, avg_comm, total_tickets = data2['sum(price)*0.1'], data2['avg(price)*0.1'], data2['count(ticket_id)']

        return render_template('b_commission.html', total_comm=total_comm, avg_comm=avg_comm,
                               total_tickets=total_tickets)
    else:
        session.clear()
        return render_template('404.html')


@app.route('/bcommissionwdate', methods=['GET', 'POST'])
def b_commission_with_date():
    if session.get('email'):
        email = session['email']

        cursor = conn.cursor()
        # Find the booking agent id
        query1 = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(query1, (email))
        data1 = cursor.fetchone()
        booking_agent = data1['booking_agent_id']  # int

        # Default: Find the total price/ average price/ tickets sold
        query2 = "SELECT sum(price)*0.1, avg(price)*0.1, count(ticket_id) \
                    FROM ticket NATURAL JOIN purchases NATURAL JOIN flight \
                    WHERE booking_agent_id = %s AND purchase_date between DATE_ADD(NOW(), INTERVAL -'30' DAY) and NOW()"
        cursor.execute(query2, (booking_agent))
        data2 = cursor.fetchone()
        total_comm, avg_comm, total_tickets = data2['sum(price)*0.1'], data2['avg(price)*0.1'], data2['count(ticket_id)']



        start = request.form['start_date']
        end = request.form['end_date']
        query3 = "SELECT sum(price)*0.1, avg(price)*0.1, count(ticket_id) \
                 FROM ticket NATURAL JOIN purchases NATURAL JOIN flight \
                 WHERE booking_agent_id = %s AND purchase_date >= %s AND purchase_date <= %s"
        cursor.execute(query3, (booking_agent, start, end))
        data3 = cursor.fetchone()
        # test = "SELECT * \
        #             FROM ticket NATURAL JOIN purchases NATURAL JOIN flight \
        #             WHERE booking_agent_id = %s AND purchase_date >=  %s AND purchase_date <=  %s"
        # cursor.execute(test, (booking_agent, start, end))
        # data4 = cursor.fetchall()
        total_comm1, avg_comm1, total_tickets1 = data3['sum(price)*0.1'], data3['avg(price)*0.1'], data3['count(ticket_id)']
        return render_template('b_commission.html', total_comm = total_comm, avg_comm = avg_comm,
                                   total_tickets = total_tickets, comm = data3,
                                   total_comm1 = total_comm1, avg_comm1 = avg_comm1, total_tickets1 = total_tickets1,
                                   start = start, end = end)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/btopcustomer')
def b_topcustomer():
    if session.get('email'):
        email = session['email']
        cursor = conn.cursor()

        # Find the booking agent id
        query1 = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(query1, (email))
        data1 = cursor.fetchone()
        booking_agent = data1['booking_agent_id']  # int

        #Find top 5 customers of tickets
        query2 = "SELECT customer_email as Customer , count(ticket_id) as Tickets \
                 FROM purchases WHERE booking_agent_id = %s AND \
                 purchase_date between DATE_ADD(LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 7 MONTH)), INTERVAL 1 DAY) and LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 1 MONTH))\
                 GROUP BY customer_email \
                 ORDER BY count(ticket_id) desc \
                 LIMIT 5"
        cursor.execute(query2,(booking_agent))
        top_ticket = cursor.fetchall()  #[{'customer_email': 'two@nyu.edu', 'count(ticket_id)': 4}, {'customer_email': 'one@nyu.edu', 'count(ticket_id)': 3}, {'customer_email': 'three@nyu.edu', 'count(ticket_id)': 3}, {'customer_email': 'four@nyu.edu', 'count(ticket_id)': 2}, {'customer_email': 'Customer@nyu.edu', 'count(ticket_id)': 1}]


        #Find top 5 customers of commission
        query3 = "SELECT customer_email as Customer, sum(price)*0.1 as Commission \
                     FROM ticket NATURAL JOIN purchases NATURAL JOIN flight \
                     WHERE booking_agent_id = %s AND \
                     YEAR(purchase_date) = YEAR(CURDATE())-1 \
                     GROUP BY customer_email \
                     ORDER BY sum(price) desc \
                     LIMIT 5"
        cursor.execute(query3, (booking_agent))
        top_commission = cursor.fetchall() #[{'customer_email': 'one@nyu.edu', 'sum(price)*0.1': Decimal('240.0')}, {'customer_email': 'two@nyu.edu', 'sum(price)*0.1': Decimal('121.4')}, {'customer_email': 'three@nyu.edu', 'sum(price)*0.1': Decimal('120.0')}, {'customer_email': 'five@nyu.edu', 'sum(price)*0.1': Decimal('80.0')}, {'customer_email': 'Customer@nyu.edu', 'sum(price)*0.1': Decimal('80.0')}]

        return render_template('b_topcustomers.html', top_ticket = top_ticket, top_commission = top_commission)
    else:
        session.clear()
        return render_template('404.html')

################################################
#               Customer
################################################
@app.route('/customer_login')
def c_login():
    return render_template('c_login.html')

@app.route('/customer_register')
def c_register():
    return render_template('c_register.html')

# Authenticates the login of customer
@app.route('/cloginAuth', methods=['GET', 'POST'])
def cloginAuth():
    if "email" in request.form and 'psw' in request.form:
        email = request.form['email']
        password = request.form['psw']

        cursor = conn.cursor()
        query = 'SELECT * FROM customer WHERE email = %s and password = md5(%s)'
        cursor.execute(query, (email, password))
        data = cursor.fetchone()
        error = None
        if (data):
            session['email'] = email
            query = "SELECT *\
                     FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
                     WHERE customer_email = %s AND departure_time BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
            cursor.execute(query, (email))
            flights = cursor.fetchall()

            return render_template('c_home.html', email = email, flights = flights)
        else:
            error = 'Invalid login or username'
            return render_template('c_login.html', error=error)
    else:
        session.clear()
        return render_template('404.html')

#Authenticates the register of customer
@app.route('/cregisterAuth', methods=['GET', 'POST'])
def cregisterAuth():
    #护照，生日日期必须有效
    #信息必须填满才能成功注册
    #提示信息flash不出来
    #用户可以update他的信息，例如护照日期，街道地址等等
    # if "email" in request.form and \
    #         'name' in request.form and \
    #         'password' in request.form and \
    #         'building number' in request.form and \
    #         'street' in request.form and \
    #         'city' in request.form and \
    #         'state' in request.form and \
    #         'phone number' in request.form and \
    #         'passport number' in request.form and \
    #         'passport expiration' in request.form and \
    #         'passport country' in request.form and \
    #         'date of birth' in request.form:
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        building_number = request.form['building number']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        phone_number = request.form['phone number']
        passport_number = request.form['passport number']
        passport_expiration = request.form['passport expiration date']
        passport_country = request.form['passport country']
        date_of_birth = request.form['date of birth']

        cursor = conn.cursor()
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()
        error = None
        if (data):
            error = "This user already exists"
            return render_template('c_register.html', error=error)
        else:
            ins = 'INSERT INTO customer VALUES (%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
            #cursor.execute('INSERT INTO customer VALUES(%s, %s)')
            conn.commit()
            cursor.close()
            flash("You have succesfully registered")
            return render_template('c_login.html')
    # else:
    #     session.clear()
    #     return render_template('404.html')

@app.route('/chome')
def c_home():
    email = session['email']
    cursor = conn.cursor()
    query = "SELECT *\
    FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
    WHERE customer_email = %s AND departure_time BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
    cursor.execute(query, (email))
    flights = cursor.fetchall()

    return render_template('c_home.html', email=email, flights=flights)

@app.route('/cview')
def c_view():
    return render_template('c_view.html')

@app.route('/cviewshow', methods=['GET', 'POST'])
def c_view_show():
    if session.get('email') and 'way' in request.form:
        email = session['email']
        way = request.form['way']
        cursor = conn.cursor()
        no_flight = None

        # Search by dates
        if way == 'dates':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            query1 = "SELECT *\
                      FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
                      WHERE customer_email = %s AND departure_time >= %s AND arrival_time <= %s AND status = 'Upcoming'"
            cursor.execute(query1, (email, start_date, end_date))
            flights = cursor.fetchall()
            if not (flights):
                no_flight = 1
            return render_template("c_view.html", flights=flights, no_flight=no_flight)

        # Search by location
        elif way == 'location':
            depart0 = request.form['depart_city_or_airport']
            arrive0 = request.form['arrive_city_or_airport']
            depart = sqlsyntax(depart0)
            arrive = sqlsyntax(arrive0)

            cursor = conn.cursor()
            query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query1, (depart))
            data1 = cursor.fetchall()

            if (data1):
                if len(data1) == 1:
                    depart_airport = [data1[0]['airport_name']]
                else:
                    depart_airport = []
                    # depart_airport = type(depart_airport)
                    for airport in data1:
                        depart_airport.append(airport['airport_name'])
            else:
                depart_airport = [depart]

            depart_airport_str = "('" + "','".join(depart_airport) + "')"

            query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query2, (arrive))
            data2 = cursor.fetchall()
            if (data2):
                if len(data2) == 1:
                    arrive_airport = [data2[0]['airport_name']]
                else:
                    arrive_airport = []
                    for i in data2:
                        arrive_airport.append(i['airport_name'])
            else:
                arrive_airport = [arrive]

            arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

            query3 = "SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
                      WHERE customer_email = %s AND status = 'Upcoming' AND departure_airport IN " \
                      + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str
            cursor.execute(query3, (email))
            flights = cursor.fetchall()
            cursor.close()
            if not (flights):
                no_flight = 1
            return render_template("c_view.html", flights=flights, no_flight=no_flight)

        # Search by location and dates
        elif way == 'both':
            start_date = request.form['start_date1']
            end_date = request.form['end_date1']
            depart0 = request.form['depart_city_or_airport1']
            arrive0 = request.form['arrive_city_or_airport1']
            depart = sqlsyntax(depart0)
            arrive = sqlsyntax(arrive0)

            cursor = conn.cursor()
            query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query1, (depart))
            data1 = cursor.fetchall()

            if (data1):
                if len(data1) == 1:
                    depart_airport = [data1[0]['airport_name']]
                else:
                    depart_airport = []
                    # depart_airport = type(depart_airport)
                    for airport in data1:
                        depart_airport.append(airport['airport_name'])
            else:
                depart_airport = [depart]

            depart_airport_str = "('" + "','".join(depart_airport) + "')"

            query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query2, (arrive))
            data2 = cursor.fetchall()
            if (data2):
                if len(data2) == 1:
                    arrive_airport = [data2[0]['airport_name']]
                else:
                    arrive_airport = []
                    for i in data2:
                        arrive_airport.append(i['airport_name'])
            else:
                arrive_airport = [arrive]

            arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

            query3 = "SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
                      WHERE customer_email = %s AND departure_time >= %s AND arrival_time <= %s AND status = 'Upcoming' AND departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str
            cursor.execute(query3, (email, start_date, end_date))
            flights = cursor.fetchall()
            cursor.close()
            if not (flights):
                no_flight = 1
            return render_template("c_view.html", flights=flights, no_flight=no_flight)

        # User did not specify way
        else:
            error = 'Please specify a way to select'
            return render_template("c_view.html", error=error)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/csearch_purchase')
def c_search_purchase():
    if session.get('email'):
        email = session['email']
        cursor =conn.cursor()

        query = "SELECT airline_name FROM airline"
        cursor.execute(query)
        airlines= cursor.fetchall()

        query1 = "SELECT flight_num FROM flight"
        cursor.execute(query1)
        flightsnum = cursor.fetchall()

        return render_template('c_search_purchase.html', flightsnum = flightsnum, airlines = airlines)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/csearch', methods = ['GET','POST'])
def c_search():
    if session.get('email') and 'way' in request.form:
        email = session['email']
        way = request.form['way']
        cursor = conn.cursor()
        no_flight = None

        # make sure one can purchase multiple times
        query = "SELECT airline_name FROM airline"
        cursor.execute(query)
        airlines = cursor.fetchall()

        query1 = "SELECT flight_num FROM flight"
        cursor.execute(query1)
        flightsnum = cursor.fetchall()

        # Search by dates
        if way == 'dates':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            query1 = "SELECT *\
                          FROM flight \
                          WHERE departure_time >= %s AND arrival_time <= %s AND status = 'Upcoming'"
            cursor.execute(query1, (start_date, end_date))
            flights = cursor.fetchall()
            if not (flights):
                no_flight = 1
            return render_template("c_search_purchase.html", flights=flights, no_flight=no_flight, flightsnum = flightsnum, airlines = airlines)

        # Search by location
        elif way == 'location':
            depart0 = request.form['depart_city_or_airport']
            arrive0 = request.form['arrive_city_or_airport']
            depart = sqlsyntax(depart0)
            arrive = sqlsyntax(arrive0)

            cursor = conn.cursor()
            query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query1, (depart))
            data1 = cursor.fetchall()

            if (data1):
                if len(data1) == 1:
                    depart_airport = [data1[0]['airport_name']]
                else:
                    depart_airport = []
                    # depart_airport = type(depart_airport)
                    for airport in data1:
                        depart_airport.append(airport['airport_name'])
            else:
                depart_airport = [depart]

            depart_airport_str = "('" + "','".join(depart_airport) + "')"

            query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query2, (arrive))
            data2 = cursor.fetchall()
            if (data2):
                if len(data2) == 1:
                    arrive_airport = [data2[0]['airport_name']]
                else:
                    arrive_airport = []
                    for i in data2:
                        arrive_airport.append(i['airport_name'])
            else:
                arrive_airport = [arrive]

            arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

            query3 = "SELECT * FROM flight\
                          WHERE departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str + " AND status = 'Upcoming'"
            cursor.execute(query3)
            flights = cursor.fetchall()
            cursor.close()
            if not (flights):
                no_flight = 1
            return render_template("c_search_purchase.html", flights=flights, no_flight=no_flight, flightsnum = flightsnum, airlines = airlines)

        # Search by location and dates
        elif way == 'both':
            start_date = request.form['start_date1']
            end_date = request.form['end_date1']
            depart0 = request.form['depart_city_or_airport1']
            arrive0 = request.form['arrive_city_or_airport1']
            depart = sqlsyntax(depart0)
            arrive = sqlsyntax(arrive0)

            cursor = conn.cursor()
            query1 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query1, (depart))
            data1 = cursor.fetchall()

            if (data1):
                if len(data1) == 1:
                    depart_airport = [data1[0]['airport_name']]
                else:
                    depart_airport = []
                    # depart_airport = type(depart_airport)
                    for airport in data1:
                        depart_airport.append(airport['airport_name'])
            else:
                depart_airport = [depart]

            depart_airport_str = "('" + "','".join(depart_airport) + "')"

            query2 = "SELECT airport_name FROM airport WHERE airport_city = %s"
            cursor.execute(query2, (arrive))
            data2 = cursor.fetchall()
            if (data2):
                if len(data2) == 1:
                    arrive_airport = [data2[0]['airport_name']]
                else:
                    arrive_airport = []
                    for i in data2:
                        arrive_airport.append(i['airport_name'])
            else:
                arrive_airport = [arrive]

            arrive_airport_str = "('" + "','".join(arrive_airport) + "')"

            query3 = "SELECT * FROM flight  \
                          WHERE departure_time >= %s AND arrival_time <= %s AND status = 'Upcoming' AND departure_airport IN " + depart_airport_str + " AND arrival_airport IN " + arrive_airport_str
            cursor.execute(query3, (start_date, end_date))
            flights = cursor.fetchall()
            cursor.close()
            if not (flights):
                no_flight = 1
            return render_template("c_search_purchase.html", flights=flights, no_flight=no_flight, flightsnum = flightsnum, airlines = airlines)

        # User did not specify way
        else:
            error = 'Please specify a way to select'
            return render_template("c_search_purchase.html", error=error)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/cpurchase', methods = ['GET','POST'])
def c_purchase():
    if session.get('email') and 'airline_name' in request.form and 'flight_number' in request.form:
        email = session['email']
        airline_name = request.form["airline_name"]
        flight_num = request.form["flight_number"]
        cursor = conn.cursor()

        #make sure one can purchase multiple times
        query = "SELECT airline_name FROM airline"
        cursor.execute(query)
        airlines = cursor.fetchall()

        query1 = "SELECT flight_num FROM flight"
        cursor.execute(query1)
        flightsnum = cursor.fetchall()

        # Validate flight
        query = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s"
        cursor.execute(query, (airline_name, flight_num))
        data = cursor.fetchall()
        if not (data):
            error0 = "The flight doesn't exist or it is not in upcoming status, please try again"
            return render_template('c_search_purchase.html', error0=error0, airlines=airlines,
                                   flightsnum=flightsnum)
        # Validate Flight Date
        query2 = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND departure_time < CURDATE()"
        cursor.execute(query2, (airline_name, flight_num))
        data2 = cursor.fetchall()
        if (data2):
            error1 = "The flight is not in the upcoming status"
            return render_template('c_search_purchase.html', error1=error1, airlines=airlines,
                                   flightsnum=flightsnum)

        # Set New Ticket ID
        query3 = "SELECT max(ticket_id) FROM ticket"
        cursor.execute(query3)
        data3 = cursor.fetchone()
        new_ticket_id = data3['max(ticket_id)'] + 1

        # Insert a new ticket
        query4 = "INSERT INTO ticket VALUES (%s, %s, %s)"
        cursor.execute(query4, (new_ticket_id, airline_name, flight_num))

        # Insert a new purchase
        query5 = "INSERT INTO purchases VALUES (%s, %s, %s, CURDATE())"
        cursor.execute(query5, (new_ticket_id, email, None))
        conn.commit()
        cursor.close()
        message1 = 'Purchase Successfully!'
        return render_template('c_search_purchase.html', message=message1, airlines=airlines,
                               flightsnum=flightsnum)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/cspending')
def c_spending():
    return render_template('c_spending.html')

@app.route('/cshowspending', methods =['GET','POST'])
def c_show_spending():
    if session.get('email'):
        email = session['email']
        cursor = conn.cursor()
        time_way = request.form['time']

        if time_way == 'month':
            # 1-1 Total Spending in last month
            query = "SELECT SUM(price) as spending , MONTH(CURDATE())-1 as month  \
                    FROM ticket NATURAL JOIN purchases NATURAL JOIN flight\
                    WHERE customer_email = %s AND purchase_date BETWEEN DATE_ADD(LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 2 MONTH)), INTERVAL 1 DAY) and LAST_DAY(DATE_ADD(CURDATE(), INTERVAL - 1 MONTH))"
            cursor.execute(query, (email))
            tot_month = cursor.fetchone()['spending']
            if tot_month is not None:
                return render_template("c_spending.html", tot_month=tot_month, time_way=time_way)
            error1 = 'No Spending in the last month'
            return render_template("c_spending.html", error1=error1, time_way=time_way)

        elif time_way == 'year':
            # 2-1 Total Spending in last year
            query2 = "SELECT SUM(price) as spending  \
                     FROM ticket NATURAL JOIN purchases NATURAL JOIN flight \
                     WHERE customer_email = %s AND YEAR(purchase_date) = YEAR(CURDATE())-1"
            cursor.execute(query2, (email))
            tot_year = cursor.fetchone()['spending']
            if tot_year is None:
                error2 = 'No Spending in the last year'
                return render_template("c_spending.html", error2=error2, time_way=time_way)

            # 2-2 Each month spending in last year
            t_each_month = []
            month_name = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                          'November', 'December']
            for i in range(1, 13):
                query3 = "SELECT SUM(price) as spending  \
                         FROM ticket NATURAL JOIN purchases  NATURAL JOIN flight\
                         WHERE customer_email = %s AND YEAR(purchase_date) = YEAR(CURDATE())-1 AND MONTH(purchase_date) = " + str(i)
                cursor.execute(query3, (email))
                data = cursor.fetchone()
                data1 = {}
                data1['Month'] = month_name[i - 1]
                if (data['spending']):
                    data1['Spending'] = data['spending']
                else:
                    data1['Spending'] = 0
                t_each_month.append(data1)
            return render_template("c_spending.html", tot_year=tot_year, t_each_month=t_each_month)


        # 3-1 Total Amount of tickets in the date range
        else:
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            query3 = "SELECT SUM(price) as spending FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE customer_email = %s AND purchase_date BETWEEN %s AND %s"
            cursor.execute(query3, (email,start_date, end_date))
            tot_date = cursor.fetchone()['spending']
            if tot_date is None:
                error3 = 'No Spending between ' + start_date +' and ' + end_date
                return render_template("c_spending.html", error3=error3, time_way=time_way)

            # 3-3 tickets in each month
            query4 = "SELECT SUM(price) as spending, YEAR(purchase_date) as year, MONTH(purchase_date) as month \
                         FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE customer_email = %s AND purchase_date BETWEEN %s AND %s \
                        GROUP BY MONTH(purchase_date), YEAR(purchase_date)"
            # [{'ticket': 7, 'year': 2022, 'month': 4}, {'ticket': 20, 'year': 2022, 'month': 5}]
            # convert it into {2022-04: 7, 2022-05: 20}  x轴：2022-04-11 - 2022-4-30， 2022-05-01 - 2022-05-22
            cursor.execute(query4, (email, start_date, end_date))
            tot_date_each_month = cursor.fetchall()
            t_date_each_month = []
            for i in tot_date_each_month:
                data = {}
                data['Month'] = str(i['year']) + '-' + str(i['month'])
                data['Spending'] = i['spending']
                t_date_each_month.append(data)
            return render_template("c_spending.html", tot_date=tot_date, t_date_each_month=t_date_each_month,
                                   start_date=start_date, end_date=end_date)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
