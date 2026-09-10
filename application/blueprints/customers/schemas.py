from application.extensions import ma
from application.models import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        # load_only means the password can be sent IN, but never comes back OUT
        # in a response. Without this every GET would leak passwords.
        load_only = ("password",)


# Only email and password. Used to validate the login route.
class LoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        fields = ("email", "password")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()
