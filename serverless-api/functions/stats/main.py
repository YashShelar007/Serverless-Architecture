# functions/stats/main.py

def get_stats(request):
    # Return some static stats as JSON
    return {"active_users": 23, "uptime": "99.9%"}, 200
