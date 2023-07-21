from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializer

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

import jwt, datetime

# Create your views here.
class RegisterView(APIView):
  def post(self, request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
  
class LoginView(APIView):
  def post(self, request):
    # We assign variables for email and password
    email = request.data['email']
    password = request.data['password']
    # Search user in database by email (unique)
    user = User.objects.filter(email=email).first()
    
    # If not found, raise exception 
    if user is None:
      raise AuthenticationFailed('User not found!')

    # Now we need to compare password, using standart Django function to check password
    # as the password in Database is Hashed, we cannot check it raw password 
    if not user.check_password(password):
      raise AuthenticationFailed('Incorrect password!')
    
    payload = {
      'id': user.id,
      # Here we define HOW LONG WILL THE TOKEN LAST
      'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
      # Define at what time the token was created?
      'iat': datetime.datetime.utcnow()
    }
    ###
    # We define a token encoding and decoding with an algorithm
    # We define a secret here, but it can be stored in any other place
    ###
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    # This gives error, but in video is decoding it 
    # (In postman looks same password as from up "my version")
    # In youtube comments it says that is not needed to be decoded anymore so approach from up is okay
    # token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

    # We don't want to return a token as Response, we want to return it with cookies
    
    response = Response()
    # With httponly, we assign that this token is only accesible via http,
    # this way it is not accesible by Front End (in this particular case)
    response.set_cookie(key='jwt', value=token, httponly=True)
    response.date = {
      'jwt': token
    }
    return response
  
  
class UserView(APIView):
  # Now we need to get the cookie and retrieve a user from it
  def get(self, request):
    # with this we get the cookie that we wont
    token = request.COOKIES.get('jwt')

    if not token:
      raise AuthenticationFailed('Unauthenticated')
    
    try:
      # We decode the token from cookie, and pass a secret key, 
      # notice! in algorithms now we add HS256 to array
      payload = jwt.decode(token, key='secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
      raise AuthenticationFailed('Unauthenticated')
    
    user = User.objects.filter(id=payload['id']).first()
    serializer = UserSerializer(user)
    return Response(serializer.data)
    
  
class LogoutView(APIView):
  def post(self, request):
    # In order to logout we only need to remove the cookie this way 
    # we define the name of deleted cookie and return response with success
    response = Response()
    response.delete_cookie('jwt')
    response.data = {
      'message': 'success'
    }
    return response