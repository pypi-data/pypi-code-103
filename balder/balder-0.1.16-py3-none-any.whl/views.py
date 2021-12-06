from graphene_file_upload.django import FileUploadGraphQLView
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.clickjacking import xframe_options_exempt

try:
    import channels_graphql_ws
    FileUploadGraphQLView.graphiql_template = "balder/graphiql-ws.html"
except:
    FileUploadGraphQLView.graphiql_template  = "balder/graphiql.html"
    pass


BalderView = xframe_options_exempt(csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True)))
BalderViewCsrfExempt = csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))
BalderViewXFrameExempt = xframe_options_exempt(BalderViewCsrfExempt)