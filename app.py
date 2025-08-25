from flask import Flask,request,render_template,session,url_for,redirect

from models import db, User,Admin,Lot,Spot,Reservation

from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

from werkzeug.security import generate_password_hash,check_password_hash
app = Flask(__name__, instance_relative_config=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SECRET_KEY'] = 'a-very-secret-and-unique-key'
#Why not instantiate app with db why not the other way around?
db.init_app(app)

#This creates the tables in the db
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    user=db.session.get(User,int(id))
    if user:
        return user 
    admin = db.session.get(Admin,int(id))
    if admin:
        return admin

@app.route('/', methods=['GET', 'POST'])
def login():
    l_again=request.args.get('l_again')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password==request.form['password']:
            login_user(admin)
            return redirect(url_for('admin'))
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('user'))
        else:
            return render_template('/auth/login.html', again=True,l_again=l_again)

    return render_template('/auth/login.html', again=False,l_again=l_again)



@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        user=User.query.filter_by(username=request.form['username']).first()
        if user:
            return render_template('/auth/register.html',again=True)
        new_user = User(
        username=request.form['username'],
        name=request.form['name'],
        pincode=request.form['pincode']
        )   
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login',l_again='True'))
    return render_template('/auth/register.html',again=False)


@app.route('/admin')
@login_required
def admin():
    if request.method=='GET':
        lots=Lot.query.all()
        lot_spots=[]
        for lot in lots:
            container=[[lot.id,lot.prime_location_name,lot.address,lot.price]]
            spots=Spot.query.filter_by(lot_id=lot.id).all()
            occupied=False
            for spot in spots:
                container.append([spot.id,spot.status])
                if spot.status=='O':
                    occupied=True
            container.append(occupied)
            lot_spots.append(container)
        return render_template('admin_home.html',active_tab='home',lot_spots=lot_spots)

@app.route('/viewSpot')
@login_required
def view_spot():
    if request.method=='GET':
        id=request.args.get('id')
        status=request.args.get('status')
        return render_template('view_spot.html',id=id,status=status)

@app.route('/deleteSpot')
@login_required
def delete_spot():
    id=request.args.get('id')
    db.session.query(Spot).filter(Spot.id==id).delete()
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/addLot',methods=['GET','POST'])
@login_required
def add_lot():
    if request.method=='POST':
        location=request.form['location']
        price=request.form['price']
        address=request.form['address']
        pincode=request.form['pincode']
        maxspot=request.form['maxspot']
        lot=Lot(prime_location_name=location,price=price,address=address,pin_code=pincode,maximum_number_of_spots=maxspot)
        db.session.add(lot)
        db.session.flush()
        spots=[]
        for i in range(int(maxspot)):
            spot=Spot(lot_id=lot.id)
            spots.append(spot)
        db.session.add_all(spots)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('add_lot.html')

@app.route('/delete_lot')
@login_required
def delete_lot():
    lot_id=request.args.get('id')
    db.session.query(Spot).filter(Spot.lot_id==lot_id).delete()
    db.session.query(Lot).filter(Lot.id==lot_id).delete()
    db.session.commit()
    return redirect(url_for('admin'))
@app.route('/edit_lot',methods=['GET','POST'])
@login_required
def edit_lot():
    lot_id=request.args.get('id')
    if request.method=='POST':
        maxspot=int(request.form['maxspot'])
        lot=db.session.query(Lot).filter(Lot.id==lot_id)
        spots=db.session.query(Spot).filter(Spot.lot_id==lot_id)
        db.session.query(Lot).filter(Lot.id==lot_id).update({Lot.maximum_number_of_spots:maxspot})
        db.session.flush()
        if spots.count()<maxspot:#increase
            ss=[]
            for i in range(maxspot-spots.count()):
                s=Spot(lot_id=lot_id)
                ss.append(s)
            db.session.add_all(ss)
                
        else:
            diff=spots.count()-maxspot
            avail=spots.filter(Spot.status=='A')
            if diff>avail.count():
                return redirect(url_for('admin'))
            query=db.session.query(Spot.id).filter(Spot.lot_id==lot_id).order_by(db.desc(Spot.id)).limit(diff)
            db.session.query(Spot).filter(Spot.id.in_(query)).delete(synchronize_session='fetch')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('edit_lot.html',id=lot_id)
@app.route('/admin/search')
@login_required
def admin_search():
    return render_template('admin_search.html',active_tab='search')

@app.route('/admin/summary')
@login_required
def admin_summary():
    return render_template('admin_summary.html',active_tab='summary')


@app.route('/user',methods=['GET','POST'])
@login_required
def user():
    if request.method=='POST':
        location=request.form.get('loc')
        lot_spot=db.session.query(Lot,Spot).join(Spot,Lot.id==Spot.lot_id).filter(db.or_(Lot.prime_location_name==location,Lot.pin_code==location)).all()
        return render_template('user_home.html',user=current_user.name,active_tab='home',lot_spot=lot_spot,location=location)
    return render_template('user_home.html',user=current_user.name,active_tab='home')


@app.route('/user/summary')
@login_required
def user_summary():
    return render_template('user_summary.html',active_tab='summary',user=current_user.name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/edit')
@login_required
def edit_profile():
    # Your logic for the edit profile page
    return "This is the edit profile page"

if __name__=='__main__':
    app.debug=True
    app.run()

