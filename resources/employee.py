from flask import Blueprint, jsonify, request, session
import json

from db import db

from models.employee import Employee
from models.driver import Driver
from models.user import User
from models.session import Session

from middleware.auth import auth_admin_middleware

bp = Blueprint("employee", __name__, url_prefix="/employee")



@bp.route("/employee", methods=["GET", "POST"])
def get_employee():
    employees = Employee.query.all()
    employees_list = []
    for employee in employees:
        employees_list.append({'id': employee.id, 'user': {'firstname': employee.firstname, 'lastname': employee.lastname, 'userId': employee.user_id, 'role': employee.role}})
    return jsonify(employees_list)


# route to register admin as employee
@bp.route("/register-admin", methods=["POST"])
def create_admin():
    # required to create admin
    firstname = request.json.get("firstname")
    lastname = request.json.get("lastname")
    contact = request.json.get("contact")
    gender = request.json.get("gender")
    role = request.json.get("role")
    employee_no = request.json.get("employeeNo")

    # required to create employee-credentials
    email = request.json.get("email")
    password = request.json.get("password")

    # check if email and password are empty
    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'email and password are required',
            'status': 400}), 400

    # check if firstname or lastname or license-no fields are empty
    if not firstname or not lastname or not role:
        return jsonify({
            'success': False,
            'message': 'firstname, lastname and role are required',
            'status': 400}), 400
    
    # check if admin already exists
    existing_admin = User.query.filter_by(email = email).first()
    if existing_admin:
        return jsonify({
            'success': False,
            'message': 'admin already registered',
            'status': 400}), 400
    
    # create new user-employee-driver
    new_admin_user = User(email=email)
    new_admin_user.set_password(password)
    db.session.add(new_admin_user)
    db.session.commit()
    # create admin
    employee = Employee(firstname=firstname, lastname=lastname, contact=contact, gender=gender, role=role, employee_no= employee_no, user_id=new_admin_user.id)
    db.session.add(employee)
    db.session.commit()

    # return added-details success
    return jsonify({
        'success': True,
        'message': 'employee admin details registered successfully',
        'status': 200,
        'user-admin': {'firstname': employee.firstname,
                        'lastname': employee.lastname,
                        'userId': new_admin_user.id,
                        'employeeId': employee.id}}), 200


# route to register driver as employee
@bp.route("/register-driver", methods=["POST"])
@auth_admin_middleware
def add_passenger_details():
    # required to populate driver table
    license_no = request.json.get("licenseNo")

    # required to populate employee-driver table
    firstname = request.json.get("firstname")
    lastname = request.json.get("lastname")
    contact = request.json.get("contact")
    gender = request.json.get("gender")
    role = request.json.get("role")
    employee_no = request.json.get("employeeNo")

    # required to populate user-driver-credentials
    email = request.json.get("email")
    password = request.json.get("password")

    if not license_no:
        return jsonify({
            'success': False,
            'message': 'license number required to register driver',
            'status': 400}), 400

    # check if email and password are empty
    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'email and password are required',
            'status': 400}), 400

    # check if firstname or lastname or license-no fields are empty
    if not firstname or not lastname or not contact:
        return jsonify({
            'success': False,
            'message': 'firstname, lastname and contact are required',
            'status': 400}), 400
    
    if not role:
        return jsonify({
            'success': False,
            'message': 'driver as role is required',
            'status': 405}), 400
    
    # check if driver already exists
    existing_driver = User.query.filter_by(email = email).first()
    if existing_driver:
        return jsonify({
            'success': False,
            'message': 'driver already registered',
            'status': 400}), 400
    
    
    if role == "driver":
        # create new user-employee-driver
        new_driver_user = User(email=email)
        new_driver_user.set_password(password)
        db.session.add(new_driver_user)
        db.session.commit()
        # create Driver
        driver = Driver(license_no=license_no)
        db.session.add(driver)
        db.session.commit()
        employee = Employee(firstname=firstname, lastname=lastname, contact=contact, gender=gender, role=role, employee_no= employee_no, user_id=new_driver_user.id, driver_id=driver.id)
        db.session.add(employee)
        db.session.commit()

    # return added-details success
    return jsonify({
        'success': True,
        'message': 'employee details registered successfully',
        'status': 200,
        'user-driver': {'firstname': employee.firstname,
                        'lastname': employee.lastname,
                        'empId': employee.id,
                        'userId': new_driver_user.id,
                        'driverId': driver.id}}), 200


# route to login as admin
@bp.route("/admin-login", methods=["POST"])
def login():
    # request
    email = request.json.get("email")
    password = request.json.get("password")
    ip_address = request.json.get("ipaddress")
    # role = request.json.get("role")

    # empty data check
    if not email or not password:
        return {"status": 400,
                "message": "missing email or password"}, 400
    
    # Checks if not admin
    employee = Employee.query.join(User).filter(User.email == email).first()
    if not employee or not employee.role == 'admin':
        return jsonify({"status": 400,
                        "message": "Only admins are allowed to login",
                        "success": False
                    }), 400

    user = User.query.filter_by(email=email).first()
    # check if user credentials are valid
    if not user or not user.check_password(password):
        return {"status": 401,
                "message": "invalid email or password"}, 401

    # create token on login
    session = Session(user_id=user.id, ip_address=ip_address)
    db.session.add(session)
    db.session.commit()

    employee = Employee.query.filter(Employee.user_id == user.id).first()

    return {'status': 200,
            'message': 'login successful',
            'user': {
                    'token': session.token,
                    'userId': user.id,
                    'email': user.email,
                    'firstname': employee.firstname,
                    'lastname': employee.lastname}}, 200


@bp.route("/logout", methods=["DELETE"])
def logout():
    # request user session token
    token = request.json.get("token")

    # check if the session exists in the database
    session_obj = Session.query.filter_by(token=token).first()
    if session_obj:
        db.session.delete(session_obj)
        db.session.commit()

    return {
        "status": 200,
        "message": "logout successful",
        "success": True
    }, 200



@bp.route("/drivers", methods=["GET", "POST"])
@auth_admin_middleware
def get_all_drivers():
    # query to join employee and driver to get all details of driver
    employees = Employee.query.join(Driver, Employee.driver_id == Driver.id).all()
    employees_list = []

    for employee in employees:
        # check if employee role is of type driver
        if employee.role == "driver" and employee.driver_id is not None:
            employees_list.append({
                        'firstname': employee.firstname,
                        'lastname': employee.lastname, 
                        'empId': employee.id, 
                        'contact': employee.contact,
                        'gender': employee.gender,
                        'employeeNo': employee.employee_no,
                        'licenseNo': employee.driver.license_no
                        })
            
    return jsonify({'status': 200, 'employee': employees_list})


# Driver employee login
@bp.route("/driver-login", methods=["POST"])
def driver_login_auth():
    # request
    email = request.json.get("email")
    password = request.json.get("password")
    ip_address = request.json.get("ipaddress")
    # role = request.json.get("role")

    # empty data check
    if not email or not password:
        return {"status": 400,
                "message": "missing email or password"}, 400
    
    # Checks if not driver
    employee = Employee.query.join(User).filter(User.email == email).first()
    if not employee or not employee.role == 'driver':
        return jsonify({"status": 400,
                        "message": "Driver access only",
                        "success": False
                    }), 400

    user = User.query.filter_by(email=email).first()
    # check if user credentials are valid
    if not user or not user.check_password(password):
        return {"status": 401,
                "message": "invalid email or password"}, 401

    # create token on login
    session = Session(user_id=user.id, ip_address=ip_address)
    db.session.add(session)
    db.session.commit()

    employee = Employee.query.filter(Employee.user_id == user.id).first()
    driver = Driver.query.filter(Driver.id == employee.driver_id).first()

    return {'status': 200,
            'message': 'login successful',
            'session': {
                'user': {
                    'userId': user.id,
                    'email': user.email,
                },
                'driver': {
                    'firstname': employee.firstname,
                    'lastname': employee.lastname,
                    'gender': employee.gender,
                    'employee-no': employee.employee_no,
                    'license-no': driver.license_no
                },
                'token': session.token,
        }}, 200