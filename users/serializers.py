from rest_framework import serializers
from .models import User
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model =  User
    # These are only fields that we want to serialize
    fields = ['id', 'name', 'email', 'password']
    extra_kwargs = {
      'password': {'write_only': True}
    }

  def create(self, validated_data):
    # We are extracting the password from the validated data
    password = validated_data.pop('password', None)

    # We pass the validated data to a database but without the password
    instance = self.Meta.model(**validated_data)
    if password is not None:
      # #### 
      # This is a function provided by django
      # This way we hash the password using django method
      # The hash is using PBKDF2 algorith with a SHA256 hash
      # password stretching mechanism recommended by NIST
      # ###
      instance.set_password(password)
    instance.save()
    # We return the instance of the created User, but we don't want to return 
    # the password, so thats why we add extra_kwargs in a serializer
    return instance
  