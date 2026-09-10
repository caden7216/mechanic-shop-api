from marshmallow import Schema, fields

from application.extensions import ma
from application.models import ServiceTicket
from application.blueprints.mechanics.schemas import MechanicSchema
from application.blueprints.inventory.schemas import InventorySchema


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    # show the assigned mechanics and the parts inside the ticket,
    # instead of just their ids
    mechanics = ma.Nested(MechanicSchema, many=True, dump_only=True)
    parts = ma.Nested(InventorySchema, many=True, dump_only=True)

    class Meta:
        model = ServiceTicket
        # auto schemas skip foreign keys unless we ask, and we need customer_id
        include_fk = True


# Used by the PUT /<id>/edit route. Two lists of mechanic ids.
class EditTicketSchema(Schema):
    add_ids = fields.List(fields.Int(), load_default=[])
    remove_ids = fields.List(fields.Int(), load_default=[])


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_ticket_schema = EditTicketSchema()
