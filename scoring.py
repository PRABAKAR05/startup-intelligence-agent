def calculate_placement_score(startup_data):
    """
    Calculates the Placement Score (0-100) based on:
    Recent Funding      30 points
    Open Roles          30 points
    Internships         20 points
    Fresher Jobs        10 points
    Remote Friendly     10 points
    """
    score = 0
    
    if startup_data.get('recent_funding'):
        score += 30
        
    open_roles = startup_data.get('open_roles', [])
    if len(open_roles) > 0:
        score += 30
        
    internships = startup_data.get('internships', [])
    if len(internships) > 0:
        score += 20
        
    fresher_jobs = startup_data.get('fresher_jobs', [])
    if len(fresher_jobs) > 0:
        score += 10
        
    # Check remote friendliness in hiring or internships
    is_remote = False
    if startup_data.get('remote_status', '').lower() == 'remote':
        is_remote = True
    for job in internships + fresher_jobs:
        if job.get('remote_status', '').lower() == 'remote':
            is_remote = True
            break
            
    if is_remote:
        score += 10
        
    return score

def calculate_hiring_score(startup_data):
    """
    Calculates a general Hiring Score (0-100) based on overall growth signals.
    """
    score = 0
    if startup_data.get('recent_funding'):
        score += 40
    if startup_data.get('likely_hiring_soon', '').upper() == 'YES':
        score += 30
    if len(startup_data.get('open_roles', [])) > 0:
        score += 30
    return score

def score_startups(startups_dict):
    """
    Takes a dictionary of startups (keyed by name) and calculates scores.
    """
    for name, data in startups_dict.items():
        data['placement_score'] = calculate_placement_score(data)
        data['hiring_score'] = calculate_hiring_score(data)
    return startups_dict
