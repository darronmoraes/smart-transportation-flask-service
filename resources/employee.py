from flask import Blueprint, jsonify, request, session
import json

from db import db

from models.employee import Employee
from models.driver import Driver

from middleware.auth import auth_admin_middleware

bp = Blueprint("employee", __name__, url_prefix="/employee")



@bp.route("/employee", methods=["GET", "POST"])
def get_employee():
    employees = Employee.query.all()
    employees_list = []
    for employee in employees:
        employees_list.append({'id': employee.id, 'user': {'firstname': employee.firstname, 'lastname': employee.lastname, 'userId': employee.user_id, 'role': employee.role}})
    return jsonify(employees_list)



@bp.route("/register-driver", methods=["POST"])
@auth_admin_middleware
def add_passenger_details():
    license_no = request.json.get("licenseNo")
    firstname = request.json.get("firstname")
    lastname = request.json.get("lastname")
    contact = request.json.get("contact")
    gender = request.json.get("gender")
    role = request.json.get("role")
    employee_no = request.json.get("employeeNo")
    user_id = request.json.get("userid")

    # check if email and password are not empty
    if not firstname or not lastname or not contact:
        return jsonify({
            'success': False,
            'message': 'firstname, lastname and contact are required',
            'status': 400}), 400
    
    if role == "driver":
        # create Driver
        driver = Driver(license_no=license_no)
        db.session.add(driver)
        db.session.commit()
        employee = Employee(firstname=firstname, lastname=lastname, contact=contact, gender=gender, role=role, employee_no= employee_no, user_id=user_id, driver_id=driver.id)
        db.session.add(employee)
        db.session.commit()

    # return added-details success
    return jsonify({
        'success': True,
        'message': 'employee details registered successfully',
        'status': 200,
        'firstname': employee.firstname,
        'lastname': employee.lastname }), 200