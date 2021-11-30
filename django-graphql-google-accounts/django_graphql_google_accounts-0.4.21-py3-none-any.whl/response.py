from graphql import GraphQLError

TOKEN_EXPIRE_RESPONSE = GraphQLError('AuthenticationError', extensions={
    'code': 401,
    'name': 'UNAUTHENTICATED',
    'message': 'Authentication Error',
})

INVALID_SIGNATURE_RESPONSE = GraphQLError('Invalid Signature', extensions={
    'code': 400,
    'name': 'INVALID SIGNATURE',
    'message': 'Invalid Signature Error',
})
