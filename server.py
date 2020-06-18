from flask import Flask, request
import json
import psycopg2
app = Flask(__name__)

@app.route("/")
def hello():
    cur.execute("select * from user_data")
    rows = cur.fetchall()
    s=''
    for r in rows:
        s += f"{r[0]} {r[1]} {r[2]} {r[3]} \n"
    return s, 200

@app.route("/login", methods=['POST'])
def password():
    global cur
    username = request.form['username']
    cur.execute(f"select password, id_u from user_data where login='{username}'")
    rows = cur.fetchall()
    if len(rows) == 0:
        return 'Invalid username', 200
    if rows[0][0] == request.form['password']:
        return str(rows[0][1])
    return 'Invalid password', 200
    

@app.route("/registration", methods=['POST'])
def registration():
    cur.execute(f"select count(*) from user_data where login='{request.form['username']}'")
    count = cur.fetchall()
    print(count)
    if count[0][0] >= 1:
        return 'User in base', 200
    cur.execute("select max(id_u) from user_data")
    max_id_u = cur.fetchall()[0][0]
    cur.execute("insert into user_data (login, password, id_u, id_g) values (%s, %s, %s, %s)", 
                            (request.form['username'], request.form['password'], max_id_u + 1, []))
    con.commit()
    return "Ok!", 200
    
@app.route("/getgroups", methods=['POST'])
def getgroups():
    cur.execute(f"select id_g from user_data where id_u={int(request.form['id_u'])}")
    u_rows = cur.fetchall()
    print(u_rows)
    all_g = dict()
    for id_g in u_rows[0][0]:
        cur.execute(f"select id_u, name, id_d from group_data where id_g={id_g}")
        g_rows = cur.fetchall()
        all_g.update({id_g:g_rows[0]})
    all_g_json = json.dumps(all_g)
    print(all_g_json)
    return all_g_json, 200

@app.route("/getdesks", methods=['POST'])
def getdesks():
    cur.execute(f"select id_d from group_data where id_g={int(request.form['id_g'])}")
    g_rows = cur.fetchall()
    print(g_rows)
    all_d = dict()
    for id_d in g_rows[0][0]:
        cur.execute(f"select name, image from desk_data where id_d={id_d}")
        d_rows = cur.fetchall()
        #print(d_rows[0][0])
        name = d_rows[0][0]
        image = d_rows[0][1]
        all_d.update({id_d:[name, image]})
    all_d_json = json.dumps(all_d)
    return all_d_json, 200

@app.route("/getusers", methods=['POST'])
def getusers():
    cur.execute(f"select id_u from group_data where id_g={int(request.form['id_g'])}")
    g_rows = cur.fetchall()
    all_u = []
    for id_u in g_rows[0][0]:
        cur.execute(f"select login from user_data where id_u={id_u}")
        u_rows = cur.fetchall()
        all_u.append(u_rows[0])
    print(all_u)
    all_u_json = json.dumps(all_u)
    return all_u_json, 200

@app.route("/addnewgroup", methods=['POST'])
def addnewgroup():
    cur.execute("select max(id_g) from group_data")
    max_id_g = cur.fetchall()[0][0]
    if max_id_g == None:
        max_id_g = 0
    id_u = []
    id_u.append(request.form['id_u'])
    cur.execute("insert into group_data (id_g, name, id_u, id_d) values (%s, %s, %s, %s)", 
                            (max_id_g + 1, request.form['name'], [int(request.form['id_u'])], []))
    cur.execute(f"select id_g from user_data where id_u={int(request.form['id_u'])}")
    id_g = cur.fetchall()[0][0]
    id_g.append(max_id_g + 1)
    print(id_g, int(request.form['id_u']))
    cur.execute("update user_data set id_g=%s where id_u=%s", (id_g, int(request.form['id_u'])))
    con.commit()
    return "Ok!", 200

@app.route("/addnewuser", methods=['POST'])
def addnewuser():
    login = request.form['login']
    id_g = int(request.form['id_g'])
    cur.execute(f"select id_g, id_u from user_data where login='{login}'")
    rows = cur.fetchall()
    print(rows)
    if len(rows) == 0:
        return "There are no user with this login", 200
    id_g_of_u = rows[0][0]
    id_u = int(rows[0][1])
    if int(request.form['id_g']) in id_g_of_u:
        return "This user is in this group yet", 200
    id_g_of_u.append(id_g)
    cur.execute("update user_data set id_g=%s where login=%s", (id_g_of_u, login))
    cur.execute(f"select id_u from group_data where id_g={id_g}")
    id_u_of_g = cur.fetchall()[0][0]
    id_u_of_g.append(id_u)
    cur.execute("update group_data set id_u=%s where id_g=%s", (id_u_of_g, id_g))
    con.commit()
    return "Ok!", 200

@app.route("/addnewdesk", methods=['POST'])
def addnewdesk():
    cur.execute("select max(id_d) from desk_data")
    max_id_d = cur.fetchall()[0][0]
    if max_id_d == None:
        max_id_d = 0
    cur.execute("insert into desk_data (id_d, name, image) values (%s, %s, %s)", 
                            (max_id_d + 1, request.form['name'], request.form['image']))
    cur.execute(f"select id_d from group_data where id_g={int(request.form['id_g'])}")
    id_d = cur.fetchall()[0][0]
    id_d.append(max_id_d + 1)
    print(id_d, int(request.form['id_g']))
    cur.execute("update group_data set id_d=%s where id_g=%s", (id_d, int(request.form['id_g'])))
    con.commit()
    return "Ok!", 200

@app.route("/setimage", methods=['POST'])
def setimage():
    cur.execute("update desk_data set image=%s where id_d=%s", (request.form['image'], int(request.form['id_d'])))
    con.commit()
    return "Ok!", 200

@app.route("/getimage", methods=['POST'])
def getimage():
    cur.execute(f"select image from desk_data where id_d={int(request.form['id_d'])}")
    image = cur.fetchall()[0][0]
    return image, 200

if __name__ == "__main__":
    con = psycopg2.connect(
    user='leyeyvguxryvqy', 
    password='714b1c972790c13e689e235a54172a58f095ba55a150d952970c5ecd6cb91eaa', 
    host='ec2-46-137-123-136.eu-west-1.compute.amazonaws.com', 
    port=5432,
    database="d2b8pf09ft58u9"
    )
    cur = con.cursor()
    app.run()