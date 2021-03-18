from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super secret key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/hosp_mang_sys'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class doctor_mgmt(db.Model):
    DOC_ID = db.Column(db.Integer, primary_key=True)
    Doctor_Name = db.Column(db.String(80), unique=False, nullable=False)
    specialization = db.Column(db.String(20), nullable=False)
    City = db.Column(db.String(20), nullable=False)
    State = db.Column(db.String(30), nullable=False)


class patient_mgmt(db.Model):
    SSN_ID = db.Column(db.Integer, primary_key=True)
    Patient_Name = db.Column(db.String(80), unique=False, nullable=False)
    Patient_Age = db.Column(db.Integer, nullable=False)
    Bed_type = db.Column(db.String(20), nullable=False)
    Address = db.Column(db.String(50), nullable=False)
    City = db.Column(db.String(20), nullable=False)
    State = db.Column(db.String(30), nullable=False)


class master_med(db.Model):
    med_id = db.Column(db.Integer, nullable=False, primary_key=True)
    med_name = db.Column(db.String(30), nullable=False)
    quant_avail = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)


class track_med(db.Model):
    sno = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    med_id = db.Column(db.Integer, db.ForeignKey('master_med.med_id'))
    qty = db.Column(db.Integer, nullable=False)
    ssn_id = db.Column(db.Integer, db.ForeignKey('patient_mgmt.SSN_ID'))


# Home Page
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session and session['user'] == 'admin':
        return render_template('newRegistration.html')

    if request.method == 'POST':
        uname = request.form.get('username')
        pword = request.form.get('pwd')
        if uname == 'admin' and pword == 'admin_pass':
            session['user'] = uname
            flash("Login Successful")
            return render_template('home.html')
        else:
            flash("Incorrect username or password")

    return render_template('login.html')


# Patient Dropdown Functions
# New Patient Registration
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        ssnid = request.form.get('ssnID')
        name = request.form.get('name')
        age = request.form.get('age')
        bedType = request.form.get('bedType')
        addr = request.form.get('addr')
        state = request.form.get('state')
        city = request.form.get('city')

        entry = patient_mgmt(SSN_ID=ssnid, Patient_Name=name, Patient_Age=age,
                             Bed_type=bedType, Address=addr, City=city, State=state)

        db.session.add(entry)
        db.session.commit()

        flash('Patient Successfully Registered!')
    return render_template('newRegistration.html')


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        docid = request.form.get('docid')
        docname = request.form.get('docname')
        department = request.form.get('department')
        city = request.form.get('city')
        state = request.form.get('state')

        entry = doctor_mgmt(DOC_ID=docid, Doctor_Name=docname, specialization=department,
                            City=city, State=state)

        db.session.add(entry)
        db.session.commit()

        flash('Appointment Successfully Registered!')
    return render_template('newappointment.html')


@app.route('/Medicine', methods=['GET', 'POST'])
def Medicine():
    if request.method == 'POST':
        medid = request.form.get('medid')
        medname = request.form.get('medname')
        quantity = request.form.get('quantity')
        price = request.form.get('price')

        entry = master_med(med_id=medid, med_name=medname, quant_avail=quantity,
                           rate=price)

        db.session.add(entry)
        db.session.commit()

        flash('new medicine successfully Registered!')
    return render_template('medicine.html')


# Update Patient Details
@app.route('/searchPatient', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        ssnid = request.form.get('ssnID')
        return redirect(url_for("update_route", ssnId=ssnid))
    else:
        return render_template('updateSearch.html')


@app.route('/update/<ssnId>', methods=['GET', 'POST'])
def update_route(ssnId):
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        bedType = request.form.get('bedType')
        addr = request.form.get('addr')
        state = request.form.get('state')
        city = request.form.get('city')

        update = patient_mgmt.query.filter_by(SSN_ID=ssnId).first()
        update.Patient_Name = name
        update.Patient_Age = age
        update.Bed_type = bedType
        update.Address = addr
        update.City = city
        update.State = state

        db.session.commit()
        flash('patient details successfully updated')
        # return redirect('/'+ ssnId)
    update = patient_mgmt.query.filter_by(SSN_ID=ssnId).first()
    return render_template('updatePatient.html', update=update)


# View All the patients in hospital
@app.route('/viewAll')
def viewAll():
    fetch = patient_mgmt.query.all()
    return render_template('viewPatient.html', fetch=fetch)


# Delete Patient
@app.route('/findPatient', methods=['GET', 'POST'])
def find_patient():
    if request.method == 'POST':
        ssnid = request.form.get('ssnID')
        return redirect(url_for("delete_patient", ssnId=ssnid))
    else:
        return render_template('deleteSearch.html')


@app.route('/delete/<ssnId>', methods=['GET', 'POST'])
def delete_patient(ssnId):
    if request.method == 'POST':
        ssnId = request.form.get('ssnID')

        update = patient_mgmt.query.filter_by(SSN_ID=ssnId).first()
        # update = patient_mgmt.query.filter_by(SSN_ID=ssnId).first()

        db.session.delete(update)
        db.session.commit()
        return redirect('/findPatient')
    update = patient_mgmt.query.filter_by(SSN_ID=ssnId).first()
    return render_template('delete.html', update=update)


# logout of the system
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user' in session and session['user'] == 'admin':
        session.pop('user')
        flash("Logged out successfully!")
        return redirect('/login')


# Pharmacy Dropdown Functions Start

@app.route('/TrackMedicine', methods=['GET', 'POST'])
def Track_Medicine():
    if request.method == 'POST':
        sno = request.form.get('sno')
        medid = request.form.get('medid')
        quantity = request.form.get('quantity')
        ssnid = request.form.get('ssnid')

        entry = track_med(sno=sno, med_id=medid, qty=quantity, ssn_id=ssnid)

        db.session.add(entry)
        db.session.commit()

        flash('medicine successfully Tracked!')
    return render_template('trackmedicine.html')


@app.route('/pharmFind', methods=['GET', 'POST'])
def pharmFind_patient():
    if request.method == 'POST':
        ssnid = request.form.get('ssnID')
        return redirect(url_for("displayMed", ssnId=ssnid))
    else:
        return render_template('pharmGetPatient.html')


# display details of patient alongwith medicine details
@app.route('/pharmDisplayMed/<ssnId>', methods=['GET', 'POST'])
def displayMed(ssnId):
    # if request.method==POST:
    display = patient_mgmt.query.filter_by(SSN_ID=ssnId)
    res = db.session.query(track_med.qty, track_med.ssn_id, master_med.med_name, master_med.rate).join(master_med,
                                                                                                       track_med.med_id == master_med.med_id and track_med.ssn_id == ssnId).all()

    return render_template('pharmDisplayMed.html', display=display, res=res)


# issue more medicines
@app.route('/availCheck', methods=['GET', 'POST'])
def availCheck():
    if request.method == 'POST':
        medname = request.form.get('mname')
        reqQty = request.form.get('qty')
        return redirect(url_for("issueMoreMedi", medname=medname, reqQty=reqQty))
    else:
        return render_template('availMediCheck.html')


@app.route('/issue/<medname>/<reqQty>', methods=['GET', 'POST'])
def issueMoreMedi(medname, reqQty):
    # if request.method=='POST':
    if (medname == master_med.med_name) and (reqQty <= master_med.quant_avail):
        issue = master_med.query.filter_by(med_name=medname).first()
        reqQty = request.form.get('qty')
        master_med.quant_avail = (master_med.quant_avail - reqQty)
        db.session.commit()
        flash('more medicine successfully issued!')
    issue = master_med.query.filter_by(med_name=medname).first()
    return render_template('issueMoreMedi.html', issue=issue)

# medicine issued for each patient
@app.route('/issuemedicine', methods=['GET', 'POST'])
def totalmedissued():
    if request.method == 'POST':
        pid = request.form.get('SSN_ID')
        medname = request.form.get('mname')
        reqQty = request.form.get('qty')
        return redirect(url_for("issueMedi", pid=pid, medname=medname, reqQty=reqQty))
    else:
        return render_template('availablemedicine.html')


@app.route('/issuemed/<medname>/<reqQty>', methods=['GET', 'POST'])
def issueMedi(pid, medname, reqQty):
    # if request.method=='POST':
    if (pid == patient_mgmt.SSN_ID, medname == master_med.med_name) and (reqQty <= master_med.quant_avail):
        issuemed = master_med.query.filter_by(SSN_ID=pid).first()
        medname = request.form.get('mname')
        reqQty = request.form.get('qty')
        master_med.quant_avail = (master_med.quant_avail - reqQty)
        db.session.commit()
        flash('new medicine successfully issued!')
    issuemed = master_med.query.filter_by(med_name=medname).first()
    return render_template('issueMedicine.html', issuemed=issuemed)


if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.run()
