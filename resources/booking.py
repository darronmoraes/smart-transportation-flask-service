from flask import Blueprint, jsonify, request, session
from datetime import datetime
import json

from db import db

from models.ticket import Ticket
from models.bus_schedules import BusSchedules
from models.halts import Halts
from models.passenger import Passenger


bp = Blueprint("booking", __name__, url_prefix="/booking")


@bp.route("/instant", methods=["POST"])
def book_instant():
    booked_at = request.json.get("booked-at")
    total_fare_amount = request.json.get("total-fare-amount")
    distance_travelled = request.json.get("distance-travelled")
    passenger_count = request.json.get("passenger-count")
    source_id = request.json.get("source-id")
    destination_id = request.json.get("destination-id")
    passenger_id = request.json.get("passenger-id")
    bus_schedule_id = request.json.get("bus-schedule-id")

    if not booked_at and passenger_count and passenger_id and bus_schedule_id:
         return jsonify({
            'success': False,
            'message': 'booking date, passenger count and passenger-id required to proceed with booking',
            'status': 400}), 400
    

    existing_booking = Ticket.query.filter_by(passenger_id=passenger_id, bus_schedule_id=bus_schedule_id, booked_at=booked_at).first()
    if existing_booking:
         return jsonify({
            'success': False,
            'message': 'There is already an existing booking for this passenger on this bus schedule.',
            'status': 400}), 400
    

    # add bus details if not existing
    new_instant_booking = Ticket(booked_at=booked_at, total_fare_amount=total_fare_amount, distance_travelled=distance_travelled,\
                                  passenger_count=passenger_count, source_id=source_id, destination_id=destination_id,\
                                    passenger_id=passenger_id, bus_schedule_id=bus_schedule_id)
    db.session.add(new_instant_booking)

    # update bus schedule available seats
    bus_schedule = BusSchedules.query.get(bus_schedule_id)
    bus_schedule.available_seats -= passenger_count
    # commit ticket booking and seat_availabilty update
    db.session.commit()


    # get source and destination stands name
    source_stand = new_instant_booking.bus_schedule.schedule.route.source_stand
    destination_stand = new_instant_booking.bus_schedule.schedule.route.destination_stand

    # return registration success
    return jsonify({
        'success': True,
        'message': 'booking successfully',
        'result': {
             'ticket': {
                'ticket-id': new_instant_booking.id,
                'fare-amount': new_instant_booking.total_fare_amount,
                'passenger-count': new_instant_booking.passenger_count,
                'source': new_instant_booking.source.name,
                'destination': new_instant_booking.destination.name,
                'booked-at': new_instant_booking.booked_at  
             },
             'bus': {
                'bus-id': new_instant_booking.bus_schedule.bus.id,
                'bus-type': new_instant_booking.bus_schedule.bus.type,
                'reg-no': new_instant_booking.bus_schedule.bus.reg_no
             },
             'schedule': {
                'schedule-id': new_instant_booking.bus_schedule.id,
                'departure': new_instant_booking.bus_schedule.schedule.departure_at.strftime('%H:%M'),
                'arrival': new_instant_booking.bus_schedule.schedule.arrival_at.strftime('%H:%M'),
                'duration': new_instant_booking.bus_schedule.schedule.duration,
                'departure-stand': source_stand,
                'arrival-stand': destination_stand,
                'date': new_instant_booking.bus_schedule.date.strftime('%Y-%m-%d'),
                'seats-available': new_instant_booking.bus_schedule.available_seats
             }
        },
        'status': 200}), 200



@bp.route("/passenger-off", methods=["POST"])
def passenger_off():
    ticket_id = request.json.get("ticket-id")
    halt_id = request.json.get("halt-id")
    
    if not ticket_id or not halt_id:
        return jsonify({
            'success': False,
            'message': 'Ticket ID and halt ID are required to proceed.',
            'status': 400}), 400
    
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    
    if not ticket:
        return jsonify({
            'success': False,
            'message': 'Ticket not found.',
            'status': 400}), 400
    
    if ticket.status == "completed":
        return jsonify({
            'success': False,
            'message': 'Passenger has already been dropped off.',
            'status': 400}), 400
    
    # update the seat availability for the bus schedule
    bus_schedule = BusSchedules.query.filter_by(id=ticket.bus_schedule_id).first()
    halt = Halts.query.filter_by(id=halt_id).first()
    
    if bus_schedule and halt:
        # calculate the number of seats to add back
        num_seats = ticket.passenger_count
        
        # update the available seats for the bus schedule
        bus_schedule.available_seats += num_seats
        
        # update the status of the ticket to completed
        ticket.status = "completed"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{num_seats} seats have been made available for the bus schedule.',
            'status': 200}), 200
    
    return jsonify({
        'success': False,
        'message': 'Invalid bus schedule or halt ID.',
        'status': 400}), 400


# @bp.route('/passenger-instant-booking', methods=['GET'])
# def passengers_instant_booking():
#     passenger = request.args.get('passenger-id')

#     if not passenger:
#         return jsonify({
#             'success': False,
#             'message': f'Passenger with id {passenger} does not exist',
#             'status': 404}), 404
    
#     passenger_bookings = Ticket.query.filter_by(passenger_id=passenger).all()
#     if not passenger_bookings:
#         return jsonify({
#             'success': False,
#             'message': f'No bookings found for passenger with id {passenger}',
#             'status': 404}), 404
    
#     bookings_data = []
#     for booking in passenger_bookings:
#         booking_data = {
#             'id': booking.id,
#             'booked_at': booking.booked_at,
#             'total_fare_amount': booking.total_fare_amount,
#             'distance_travelled': booking.distance_travelled,
#             'passenger_count': booking.passenger_count,
#             'source_id': booking.source_id,
#             'destination_id': booking.destination_id,
#             'bus_schedule_id': booking.bus_schedule_id,
#             'status': booking.status
#         }
#         bookings_data.append(booking_data)

    
#     return jsonify({
#             'success': True,
#             'passenger-id': passenger,
#             'bookings': bookings_data,
#             'status': 200}), 200



@bp.route('/passenger-ticket-bookings/<int:passenger_id>', methods=['GET'])
def passenger_ticket_bookings(passenger_id):
    passenger = Passenger.query.get(passenger_id)
    if not passenger:
        return jsonify({
            'success': False,
            'message': f'Passenger with id {passenger_id} does not exist',
            'status': 404}), 404

    passenger_bookings = Ticket.query.filter_by(passenger_id=passenger_id).all()
    if not passenger_bookings:
        return jsonify({
            'success': False,
            'message': f'No bookings found for passenger with id {passenger_id}',
            'status': 404}), 404

    bookings_data = []
    for booking in passenger_bookings:
        source_stop = Halts.query.filter_by(id=booking.source_id).first()
        destination_stop = Halts.query.filter_by(id=booking.destination_id).first()

        booking_data = {
            'id': booking.id,
            'booked_at': booking.booked_at,
            'total_fare_amount': booking.total_fare_amount,
            'distance_travelled': booking.distance_travelled,
            'passenger_count': booking.passenger_count,
            'source': source_stop.name,
            'destination': destination_stop.name,
            'bus_schedule_id': booking.bus_schedule_id,
            'status': booking.status
        }
        bookings_data.append(booking_data)

    return jsonify({
        'success': True,
        'passenger_id': passenger_id,
        'bookings': bookings_data,
        'status': 200}), 200



# route to get halts for matching source geo locations
@bp.route('/bus-stops', methods=['GET'])
def get_bus_stops():
    halts = Halts.query.all()
    halts_list = []
    for halt in halts:
        halts_list.append({'id': halt.id, 'name': halt.name, 'long': halt.longitude, 'lat': halt.latitude})
    return jsonify({
        'success': True,
        'result': halts_list,
        'status': 200
    }), 200