from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from .serializer import *
from rest_framework.response import Response


class ReactView(APIView):
    def get(self, request):
        output_list = [{"employee": item.employee,
                   "department": item.department}
                   for item in React.objects.all()]
        
        # print(output_list)
        return Response(output_list)
    
    def post(self, request):
        serializer = ReactSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        
    # def put(self, request, pk):
    #     try:
    #         react = React.objects.get(pk=pk)
    #     except React.DoesNotExist:
    #         return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        
    #     serializer = ReactSerializer(react, data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # # DELETE: Delete a record
    # def delete(self, request, pk):
    #     try:
    #         react = React.objects.get(pk=pk)
    #         react.delete()
    #         return Response({"message": "Record deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    #     except React.DoesNotExist:
    #         return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)