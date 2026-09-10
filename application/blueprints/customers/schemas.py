from application.extensions import ma
from application.models import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
