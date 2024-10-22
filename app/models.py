
from decouple import config
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute
from pynamodb.models import Model
import uuid


# Define the user model
class UserModel(Model):
    class Meta:
        table_name = "users"
        region = config('AWS_REGION')
        host = config('DATABASE_HOST')
        
        if config('ENVIRONMENT') == 'local':
            host = config('DATABASE_HOST')

    id = UnicodeAttribute(hash_key=True, default=str(uuid.uuid4()))
    email = UnicodeAttribute(null=False)
    hashed_password = UnicodeAttribute(null=False)
    is_active = BooleanAttribute(default=True)
    is_superuser = BooleanAttribute(default=False)
    access_token = UnicodeAttribute(null=True)