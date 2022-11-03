from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,\
    CreateAPIView
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from django.contrib.auth import authenticate

from .models import Poll, Choice
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer, UserSerializer


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def destroy(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=kwargs['pk'])
        if not request.user == poll.created_by:
            raise PermissionDenied("You can not delete this poll.")
        return super().destroy(request, *args, **kwargs)


class PollList(ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class PollDetail(RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class ChoiceList(ListCreateAPIView):
    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs['pk'])
        return queryset
    serializer_class = ChoiceSerializer

    def post(self, request, *args, **kwargs):
        vote = VoteSerializer(data=request.data)
        if vote.is_valid():
            vote.save()
            return Response(vote.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vote.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateVote(APIView):
    serializer_class = VoteSerializer

    def post(self, request, pk, choice_pk):
        voted_by = request.data.get("voted_by")
        data = {'choice': choice_pk, 'poll': pk, 'voted_by': voted_by}
        serializer = VoteSerializer(data=data)
        if serializer.is_valid():
            vote = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class LoginView(APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

