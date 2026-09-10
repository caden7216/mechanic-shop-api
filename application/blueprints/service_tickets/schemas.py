from application.extensions import ma
from application.models import ServiceTicket
from application.blueprints.mechanics.schemas import MechanicSchema


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    # show the assigned mechanics inside the ticket, instead of just their ids
    mechanics = ma.Nested(MechanicSchema, many=True, dump_only=True)

    class Meta:
        model = ServiceTicket
        # auto schemas skip foreign keys unless we ask, and we need customer_id
        include_fk = True


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
