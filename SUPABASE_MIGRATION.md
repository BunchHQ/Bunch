# Personal Notes

The planned flow

1. User signs up on the Next frontend, it calls supabase to complete the signup, and upon successful signup, redirect to /onboarding
2. After the signup completes, requests to Django backend will contain a jwt token, which will be used for authentication
3. /onboarding complete request will then create/update the User model with data, skipping it will still create/update one, with default data

4. Django middlewares will handle auth stuff, and creating shadow users

# TODO

### Backend

- implement supabase integration tests
- ensure auth works correctly
- clearup permissions logic

### Frontend

- almost everything
- remove clerk
- add supabase and auth
- implement onboarding and not onboarding -> redirect -> onboarding logic
