import secrets
from datetime import datetime
from flask.views import MethodView
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from flask import Blueprint, make_response, jsonify, request

from project.server import ma, db
from project.server.models import Parcel, User, Receiver,Sender
from flask_cors import cross_origin
from project.server.utils import get_recipient_id, get_customer_id

parcel_blueprint = Blueprint('parcel', __name__)

class ParcelSchema(ma.Schema):
    class Meta:
        fields = (
            'id',
            'item',
            'sender_id',
            'teller_id',
            'receiver_id',
            'dispatch_date',
            'arrival_date',
            'delivered_date',
            'delivered',
            'cost',
            'quantity'
        )

parcels_schema = ParcelSchema(many=True)

class ListParcelAPI(MethodView):
    def get(self):
        try:
            category = request.args.get('category')

            if category == 'received':
                parcels = Parcel.query.filter_by(delivered=True)
                result = parcels_schema.dump(parcels)
                return make_response(jsonify(result)), 200
            else:
                parcels = Parcel.query.order_by(Parcel.id.desc())
                result = parcels_schema.dump(parcels)
                return make_response(jsonify(result)), 200

        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Could not get parcels. Please try again'
            }
            return make_response(jsonify(responseObject)), 400

class CreateParcelAPI(MethodView):
    decorators = [jwt_required(), cross_origin()]
    def post(self):
        try:
            post_data = request.get_json()

            print(post_data)

            customer_id = post_data.get('customer_id')
            receiver_id = post_data.get('receiver_id')

            parcel_data = post_data.get('parcel')

            parcel = Parcel(
                item=parcel_data.get('item'),
                dispatch_date=parcel_data.get('dispatch_date'),
                arrival_date=parcel_data.get('arrival_date'),
                cost=int(parcel_data.get('cost')),
                quantity=int(parcel_data.get('quantity')),
                sender_id=int(customer_id),
                delivered=False,
                delivered_date=None,
                receiver_id=int(receiver_id),
                teller_id=get_jwt_identity()
            )

            db.session.add(parcel)
            db.session.commit()

            print(post_data)

            return make_response(jsonify({'status':'success', 'message': 'Parcel saved successfully.'}))
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Could not add parcel. Please try again'
            }
            return make_response(jsonify(responseObject)), 400

class DetailParcelAPI(MethodView):
    # decorators = [jwt_required()]
    # @todo ===> add auth
    def get(self, parcel_id):
        print(parcel_id)
        # try:
        parcel = Parcel.query.filter_by(id=parcel_id).first()
        teller_id = parcel.teller_id
        sender_id = parcel.sender_id
        receiver_id = parcel.receiver_id

        sender = Sender.query.filter_by(id=sender_id).first()
        receiver = Receiver.query.filter_by(id=receiver_id).first()
        teller = User.query.filter_by(id=teller_id).first()

        responseObject = {
            'id': parcel.id,
            'item': parcel.item,
            'quantity': parcel.quantity,
            'dispatch_date': parcel.dispatch_date,
            'arrival_date': parcel.arrival_date,
            'delivered_date': parcel.delivered_date,
            'delivered': parcel.delivered,
            'cost': parcel.cost,
            'sender': {
                'id': sender.id,
                'full_name': sender.full_name,
                'phone': sender.phone,
                'email': sender.email,
                'center': sender.center
            },
            'receiver': {
                'id': receiver.id,
                'full_name': receiver.full_name,
                'phone': receiver.phone,
                'email': receiver.email,
                'center': receiver.center
            },
            'teller': {
                'id': teller.id,
                'first_name': teller.first_name,
                'last_name': teller.last_name,
                'email': teller.email,
                'role': teller.role
            },
        }
        return make_response(jsonify(responseObject)), 200
        # except Exception as e:
        #     responseObject = {
        #         'status': 'fail',
        #         'message': 'Could not find parcel with that id. Please try again'
        #     }
        #     return make_response(jsonify(responseObject)), 400

class UpdateParcelAPI(MethodView):
    decorators = [jwt_required()]
    def put(self, parcel_no):
        # try:
        parcel = Parcel.query.filter_by(parcel_no=parcel_no).first()

        update_data = request.get_json()

        sender_name = update_data.get('sender_name', None)
        sender_phone = update_data.get('sender_phone', None)
        sender_address = update_data.get('sender_address', None)
        receiver_name = update_data.get('receiver_name', None)
        receiver_phone = update_data.get('receiver_phone', None)
        parcel_quantity = update_data.get('parcel_quantity', None)

        if sender_phone:
            parcel.sender_name = sender_name
        if sender_phone:
            parcel.sender_phone = sender_phone
        if sender_address:
            parcel.sender_address = sender_address
        if receiver_name:
            parcel.receiver_name = receiver_name
        if receiver_phone:
            parcel.receiver_phone = receiver_phone
        if parcel_quantity:
            parcel.parcel_quantity = parcel_quantity

        booked_by = User.query.filter_by(id=get_jwt_identity()).first()
        parcel.teller_id = get_jwt_identity()

        db.session.commit()

        responseObject = {
            'id': parcel.id,
            'sender_name': parcel.sender_name,
            'sender_phone': parcel.sender_phone,
            'sender_address': parcel.sender_address,
            'receiver_name': parcel.receiver_name,
            'receiver_phone': parcel.receiver_phone,
            'parcel_quantity': parcel.parcel_quantity,
            'parcel_no': parcel.parcel_no,
            'booked_by': f'{booked_by.first_name} {booked_by.last_name}',
        }
        return make_response(jsonify(responseObject)), 200
        # except Exception as e:
        #     responseObject = {
        #         'status': 'fail',
        #         'message': 'Could not find parcel with that id. Please try again'
        #     }
        #     return make_response(jsonify(responseObject)), 400

class DeleteParcelAPI(MethodView):
    decorators = [jwt_required()]
    def delete(self, parcel_no):
        try:
            parcel = Parcel.query.filter_by(parcel_no=parcel_no).first()

            db.session.delete(parcel)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Parcel deleted successfully.'
            })), 200
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Could not delete the parcel. Please try again'
            }
            return make_response(jsonify(responseObject)), 400

parcels_list_view = ListParcelAPI.as_view('parcels_list_api')
parcels_create_view = CreateParcelAPI.as_view('parcels_create_api')
parcels_detail_view = DetailParcelAPI.as_view('parcels_detail_api')
parcels_update_view = UpdateParcelAPI.as_view('parcels_update_api')
parcels_delete_view = DeleteParcelAPI.as_view('parcels_delete_api')

parcel_blueprint.add_url_rule(
    '/api/parcels/list',
    view_func=parcels_list_view,
    methods=['GET']
)

parcel_blueprint.add_url_rule(
    '/api/parcels/create',
    view_func=parcels_create_view,
    methods=['POST']
)

parcel_blueprint.add_url_rule(
    '/api/parcels/<int:parcel_id>',
    view_func=parcels_detail_view,
    methods=['GET']
)

parcel_blueprint.add_url_rule(
    '/api/parcels/<string:parcel_no>',
    view_func=parcels_update_view,
    methods=['PUT']
)

parcel_blueprint.add_url_rule(
    '/api/parcels/<string:parcel_no>',
    view_func=parcels_delete_view,
    methods=['DELETE']
)


