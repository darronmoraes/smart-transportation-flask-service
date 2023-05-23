from flask import Blueprint, jsonify, request, session
from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

import json

from db import db

from models.ticket import Ticket
from models.bus_schedules import BusSchedules
from models.halts import Halts
from models.passenger import Passenger
from models.route_info import RouteInfo
from models.route import Route
from models.pass_model import Pass
from models.pass_booking import PassBooking


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
    

    # check for existing booking by the passenger on the schedule and timestamp
    existing_booking = Ticket.query.filter_by(passenger_id=passenger_id, bus_schedule_id=bus_schedule_id, booked_at=booked_at).first()
    if existing_booking:
         return jsonify({
            'success': False,
            'message': 'There is already an existing booking for this passenger on this bus schedule.',
            'status': 400}), 400
    
    # check if available-seats in BusSchedules is less than passenger-count requested
    bus_schedule = BusSchedules.query.get(bus_schedule_id)
    if bus_schedule.available_seats < passenger_count:
        return jsonify({
            'success': False,
            'message': 'Unfortunately there are not enough seats available for the requested number of passengers.',
            'status': 410}), 410
    

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
                'id': new_instant_booking.id,
                'fare-amount': new_instant_booking.total_fare_amount,
                'passenger-count': new_instant_booking.passenger_count,
                'source': new_instant_booking.source.name,
                'destination': new_instant_booking.destination.name,
                'booked-at': new_instant_booking.booked_at  
             },
             'bus': {
                'id': new_instant_booking.bus_schedule.bus.id,
                'bus-type': new_instant_booking.bus_schedule.bus.type,
                'reg-no': new_instant_booking.bus_schedule.bus.reg_no
             },
             'schedule-info': {
                'id': new_instant_booking.bus_schedule.id,
                'schedule': {
                    'id': new_instant_booking.bus_schedule.schedule.id,
                    'departure': new_instant_booking.bus_schedule.schedule.departure_at.strftime('%H:%M'),
                    'departure-stand': source_stand,
                    'arrival': new_instant_booking.bus_schedule.schedule.arrival_at.strftime('%H:%M'),
                    'arrival-stand': destination_stand,
                    'duration': new_instant_booking.bus_schedule.schedule.duration,
                },
                'date': new_instant_booking.bus_schedule.date.strftime('%Y-%m-%d'),
                'seats-available': new_instant_booking.bus_schedule.available_seats
             }
        },
        'status': 200}), 200


# Api to get the booked ticket having current date
@bp.route('/current-booked-ticket', methods=['GET'])
def get_current_booked_ticket():
    passenger_id = request.args.get('passenger-id')
    if not passenger_id:
        return jsonify({
            'success': False,
            'message': 'Passenger ID is missing',
            'status': 400
        }), 400

    current_date = date.today()
    print(f"Current date: {current_date}")
    ticket = Ticket.query.filter(Ticket.status == 'Booked', func.date(Ticket.booked_at) == current_date, Ticket.passenger_id == passenger_id).first()

    if not ticket:
        return jsonify({
            'success': False,
            'message': 'No current booked ticket found',
            'status': 404
        }), 404

    source_stop = Halts.query.filter_by(id=ticket.source_id).first()
    destination_stop = Halts.query.filter_by(id=ticket.destination_id).first()
    bus_schedule_info = BusSchedules.query.filter_by(id=ticket.bus_schedule_id).first()

    ticket_data = {
        'ticket': {
            'id': ticket.id,
            'booked-at': ticket.booked_at,
            'total-fare-amount': ticket.total_fare_amount,
            'distance-travelled': ticket.distance_travelled,
            'passenger-count': ticket.passenger_count,
            'status': ticket.status,
            'source': source_stop.name,
            'destination': destination_stop.name,
        },
        'schedule-info': {
            'id': ticket.bus_schedule_id,
            'date': bus_schedule_info.date.strftime('%Y-%m-%d')
        },
        'bus': {
            'id': bus_schedule_info.bus.id,
            'reg-no': bus_schedule_info.bus.reg_no,
            'type': bus_schedule_info.bus.type
        },
    }

    return jsonify({
        'success': True,
        'ticket': ticket_data,
        'status': 200
    }), 200



# Api to mark passenger ticket status as Completed
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


# api to get passenger ticket bookings
@bp.route('/passenger-ticket-bookings/<int:passenger_id>', methods=['GET'])
def passenger_ticket_bookings(passenger_id):
    passenger = Passenger.query.get(passenger_id)
    if not passenger:
        return jsonify({
            'success': False,
            'message': f'Passenger with id {passenger_id} does not exist',
            'status': 404}), 404

    passenger_tickets = Ticket.query.filter_by(passenger_id=passenger_id).all()
    if not passenger_tickets:
        return jsonify({
            'success': False,
            'message': f'No bookings found for passenger with id {passenger_id}',
            'status': 404}), 404

    tickets_data = []
    for ticket in passenger_tickets:
        source_stop = Halts.query.filter_by(id=ticket.source_id).first()
        destination_stop = Halts.query.filter_by(id=ticket.destination_id).first()
        bus_schedule_info = BusSchedules.query.filter_by(id=ticket.bus_schedule_id).first()

        ticket_data = {
            'ticket': {
                'id': ticket.id,
                'booked-at': ticket.booked_at,
                'total-fare-amount': ticket.total_fare_amount,
                'distance-travelled': ticket.distance_travelled,
                'passenger-count': ticket.passenger_count,
                'status': ticket.status,
                'source': source_stop.name,
                'destination': destination_stop.name,
            },
            'schedule-info': {
                'id': ticket.bus_schedule_id,
                'date': bus_schedule_info.date.strftime('%Y-%m-%d')
            }, 
            'bus': {
                'id': bus_schedule_info.bus.id,
                'reg-no': bus_schedule_info.bus.reg_no,
                'type': bus_schedule_info.bus.type
            },
        }
        tickets_data.append(ticket_data)

    return jsonify({
        'success': True,
        'passenger_id': passenger_id,
        'bookings': tickets_data,
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


# seat-available route
@bp.route('/seat-available', methods=['POST'])
def check_availability():
    bus_id = request.args.get('bus-id')
    schedule_info_id = request.args.get('schedule-info-id')
    schedule_id = request.args.get('schedule-id')
    passenger_count = int(request.args.get('passenger-count'))
    date_str = request.args.get('date')

    # convert date
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    if not bus_id and not schedule_info_id and not schedule_id and not passenger_count and not date:
        return jsonify({
            'success': False,
            'message': 'No schedule and passenger count provided.',
            'status': 400}), 400
    
    bus_schedule = BusSchedules.query.filter_by(id=schedule_info_id, bus_id=bus_id, schedule_id=schedule_id, date=date).first()

    if not bus_schedule:
        return jsonify({
            'success': False,
            'message': 'No buses available for the specified date',
            'status': 400}), 400
    
    available_seats = bus_schedule.available_seats

    if available_seats < passenger_count:
        return jsonify({
            'success': False,
            'message': 'Not enough seats available for the specified number of passengers',
            'status': 400}), 400
    
    return jsonify({
            'success': True,
            'available-seats': available_seats,
            'status': 200}), 200


# api to get available bus-schedules for booking ticket
@bp.route("/search", methods=["GET"])
def bus_available_search():
    source_id = request.args.get('source')
    destination_id = request.args.get('destination')
    date_str = request.args.get('date')

    # convert date
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # query route-info model to find the route between source and destination
    route_query = db.session.query(Halts, RouteInfo).\
        join(RouteInfo, RouteInfo.source_id == Halts.id).\
        filter(RouteInfo.source_id == source_id, RouteInfo.destination_id == destination_id)

    route_info = route_query.first()

    # query bus-schedule model to find the available date
    bus_schedules = BusSchedules.query.filter(BusSchedules.date == date).all()

    if not bus_schedules:
        return jsonify({
            'success': False,
            'message': 'no buses available on this route for the specific date',
            'status': 400
        }), 400

    available_buses = []

    for bus_schedule in bus_schedules:
        # get the route information from the schedule
        route_stand = bus_schedule.schedule.route
        # get the source and destination stands from the route info
        source_stand = route_stand.source_stand
        destination_stand = route_stand.destination_stand

        # query halts table to get source and destination names
        source_halt = Halts.query.get(source_id)
        destination_halt = Halts.query.get(destination_id)

        available_bus_result = {
            'schedule-info': {
                'id': bus_schedule.id,
                'date': bus_schedule.date.strftime('%Y-%m-%d'),
                'seats-available': bus_schedule.available_seats,
                'schedule' : {
                    'id' : bus_schedule.schedule.id,
                    'departure': bus_schedule.schedule.departure_at.strftime('%H:%M'),
                    'arrival': bus_schedule.schedule.arrival_at.strftime('%H:%M'),
                    'duration': bus_schedule.schedule.duration,
                    'departure-stand': source_stand,
                    'arrival-stand': destination_stand
                }
            },
            'bus': {
                'id': bus_schedule.bus.id,
                'reg-no': bus_schedule.bus.reg_no,
                'type': bus_schedule.bus.type
            },
            'route-info': {
                'source': source_halt.name,
                'source-id': source_halt.id,
                'destination': destination_halt.name,
                'destination-id': destination_halt.id,
                'distance': route_info.RouteInfo.distance,
                'fare': route_info.RouteInfo.fare
            }
        }
        available_buses.append(available_bus_result)

    return jsonify({
        'success': True,
        'status': 200,
        'results': available_buses
    }), 200



"""
Pass Booking Api's requests
Get a list of all pass bookings

"""
# route to get pass **not required**
@bp.route('/pass', methods=['GET'])
def get_pass():
    passes = Pass.query.all()
    pass_list = []
    for p in passes:

        # route info source and destination query
        route_info = p.route_info
        source = route_info.source.name
        destination = route_info.destination.name

        pass_list.append({
            'id': p.id, 
            'valid_from': p.valid_from, 
            'valid_to': p.valid_to, 
            'status': p.status, 
            'price': p.price, 
            'source': source,
            'destination': destination})
        

    return jsonify({
        'success': True,
        'result': pass_list,
        'status': 200
    }), 200


# api to create a new pass for passenger
@bp.route('/passenger/<passenger_id>/passes', methods=['POST'])
def create_passenger_pass(passenger_id):
    # Retrieve the passenger using the passenger_id
    passenger = Passenger.query.get(passenger_id)

    # check if passenger exists
    if not passenger:
        return jsonify({
            'success': False,
            'message': 'Passenger not found',
            'status': 400
        }), 400

    # request pass data
    valid_from = request.json.get('valid-from')
    valid_to = request.json.get('valid-to')
    route_info_id = request.json.get('route-info-id')
    price = request.json.get('price')

    if not route_info_id:
        return jsonify({
            'success': False,
            'message': 'provide a route for pass',
            'status': 400
        }), 400

    # query for existing pass
    existing_pass = Pass.query.filter(
        Pass.passenger_id == passenger_id, 
        Pass.valid_from <= valid_to, 
        Pass.valid_to >= valid_from, 
        Pass.route_info_id == route_info_id,
    ).first()
    if existing_pass:
        return jsonify({
            'success': False,
            'message': 'Already created pass having same dates, source & destination',
            'status': 401
        }), 401

    # create pass
    new_pass = Pass(
        valid_from = valid_from,
        valid_to = valid_to,
        status = 'active',
        price = price,
        passenger_id = passenger_id,
        route_info_id = route_info_id,
    )

    # insert pass to db
    db.session.add(new_pass)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Pass created successfully',
        'pass_id': new_pass.id,
        # 'payment_id': payment.id,
        'status': 200
    }), 200
    


# api to get pass created by passenger
@bp.route("/passenger/<passenger_id>/passes", methods=['GET'])
def get_user_passes(passenger_id):
    # Retrieve the passenger using the passenger_id
    passenger = Passenger.query.get(passenger_id)

    # check if passenger exists
    if not passenger:
        return jsonify({
        'success': False,
        'message': 'passenger not found',
        'status': 400}), 400
    
    # Query Pass model to get passes on passenger-id
    passes = Pass.query.filter_by(passenger_id=passenger_id).all()

    # Store the list of passes in pass_data array-list
    pass_data = []
    for p in passes:
        if p:
            valid_from = p.valid_from.strftime('%Y-%m-%d')
            valid_to = p.valid_to.strftime('%Y-%m-%d')

            # route info source and destination query
            route_info = p.route_info
            source = route_info.source.name
            destination = route_info.destination.name

            pass_data.append({
                'id': p.id,
                'source': source,
                'destination': destination,
                'status': p.status,
                'valid-from': valid_from,
                'valid-to': valid_to,
                'price': p.price,
            })

            return jsonify({
                'success': True,
                'result': pass_data,
                'status': 200
            }), 200

    return jsonify({
        'success': False,
        'message': 'create a new pass to view',
        'status': 400
    }), 400


# validate pass for onboarding
@bp.route("/passenger/<passenger_id>/passes/<pass_id>/validate-pass", methods=['POST'])
def validate_pass_onboarding(passenger_id, pass_id):
    passenger = Passenger.query.get(passenger_id)
    if not passenger:
        return jsonify({
            'success': False,
            'message': 'Passenger not found',
            'status': 401
        }), 401

    pass_model = Pass.query.filter_by(id=pass_id, passenger_id=passenger_id).first()
    if not pass_model:
        return jsonify({
            'success': False,
            'message': 'Pass not found',
            'status': 402
        }), 402

    travel_date_str = request.json.get('travel-date')
    travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d').date()

    bus_schedule_id = request.json.get('bus-schedule-id')
    booked_at = request.json.get('booked-at')

    if not bus_schedule_id or not booked_at:
        return jsonify({
            'success': False,
            'message': 'Please provide a bus schedule and booking time for the pass holder',
            'status': 420
        }), 420

    if pass_model.valid_from <= travel_date <= pass_model.valid_to:
        if pass_model.usage_counter < 2:
            try:
                # Allocate the pass to a bus schedule if seats are available
                allocated = PassBooking.allocate_pass_to_bus_schedule(pass_id, bus_schedule_id, booked_at)
                if allocated:
                    # Increment the usage counter only if it's the same travel date
                    pass_model.usage_counter += 1
                    db.session.commit()

                    return jsonify({
                        'success': True,
                        'message': 'Pass is valid for travel and allocated to the bus schedule',
                        'status': 200
                    }), 200
                else:
                    db.session.rollback()
                    return jsonify({
                        'success': False,
                        'message': 'Pass is valid for travel today, but no seats are available in the bus schedule',
                        'status': 403}), 403

            except SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': 'Failed to allocate pass to bus schedule. Database error occurred.',
                    'status': 404}), 404

        else:
            return jsonify({
                'success': False,
                'message': 'Pass has already been used twice today',
                'status': 400}), 400
    else:
        return jsonify({
            'success': False,
            'message': 'Pass is not valid for the specified travel date',
            'status': 400}), 400
