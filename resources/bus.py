from flask import Blueprint, jsonify, request, session
from datetime import datetime
import json

from db import db

from models.bus import Bus
from models.bus_schedules import BusSchedules
from models.driver import Driver
from models.employee import Employee


bp = Blueprint("bus", __name__, url_prefix="/bus")



@bp.route("/bus", methods=["GET", "POST"])
def bus():
    buses = Bus.query.all()
    bus_list = []
    for bus in buses:
        bus_list.append({'id': bus.id, 'rto-reg-no': bus.reg_no, 'capacity': bus.capacity, 'type': bus.type, 'status': bus.status})
    return jsonify({
        'success': True,
        'status': 200,
        'result': bus_list}), 200


@bp.route("/add-bus-details", methods=["POST"])
def bus_details():
    reg_no = request.json.get("register-no")
    capacity = request.json.get("capacity")
    type = request.json.get("type")
    status = request.json.get("status")

    # registered number required
    if not reg_no:
        return jsonify({
            'success': False,
            'message': 'registration number is required',
            'status': 400}), 400
    
    # check for exisiting bus details
    existing_bus = Bus.query.filter_by(reg_no=reg_no).first()
    if existing_bus:
        return jsonify({
            'success': False,
            'message': 'bus already registered',
            'status': 400}), 400
    
    # add bus details if not exisiting
    new_bus = Bus(reg_no=reg_no, capacity=capacity, type=type, status=status)
    db.session.add(new_bus)
    db.session.commit()

    # return registration success
    return jsonify({
        'success': True,
        'message': 'bus registered successfully',
        'status': 200}), 200


@bp.route("/add-bus-schedule", methods=["POST"])
def bus_schedule():
    bus_id = request.json.get("bus-id")
    schedule_id = request.json.get("schedule-id")
    employee_id = request.json.get("employee-id")
    # available_seats = request.json.get("available-seats")
    date = request.json.get("date")

    # required check
    if not bus_id and schedule_id and employee_id and date:
        return jsonify({
            'success': False,
            'message': 'bus, schedule and driver-employee details required and also date',
            'status': 401}), 401
    
    # check if driver exists in employee model having driver-id
    employee = Employee.query.filter_by(id=employee_id, driver_id=Driver.id).first()
    if not employee:
        return jsonify({
            'success': False,
            'message': 'Driver not found in the employee model',
            'status': 402
        }), 402


    # check for exisiting bus schedule
    existing_schedule = BusSchedules.query.filter_by(bus_id=bus_id, schedule_id=schedule_id, date=date).first()
    if existing_schedule:
        return jsonify({
            'success': False,
            'message': 'bus already scheduled for specified date',
            'status': 403}), 403
    
    # check for exisiting bus schedule
    driver_schedule = BusSchedules.query.filter_by(schedule_id=schedule_id, employee_id=employee_id, date=date).first()
    if driver_schedule:
        return jsonify({
            'success': False,
            'message': 'Driver is already allocated a bus and a schedule',
            'status': 404}), 404
    
   
    
    # get available seats
    bus_details = Bus.query.filter_by(id=bus_id).first()
    available_seats = bus_details.capacity
    
    # add bus details if not exisiting
    new_bus_schedule = BusSchedules(bus_id=bus_id, schedule_id=schedule_id, employee_id=employee_id, available_seats=available_seats, date=date)
    db.session.add(new_bus_schedule)
    db.session.commit()

    # return registration success
    return jsonify({
        'success': True,
        'message': 'bus scheduled with driver successfully',
        'status': 200}), 200


@bp.route("/bus-schedule", methods=["GET", "POST"])
def get_bus_schedule():
    bus_schedule = BusSchedules.query.all()
    bus_schedule_list = []
    for bus in bus_schedule:
        bus_schedule_list.append({'bus-id': bus.bus_id, 'schedule-id': bus.schedule_id, 'available-seats': bus.available_seats, 'date': bus.date})
    return jsonify({
        'success': False,
        'status': 200,
        'result': bus_schedule_list}), 200