# functions/users/main.py

def get_users(request):
    # Return a simple static users list as JSON
    return {"users": ["alice", "bob", "carol"]}, 200
