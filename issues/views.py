from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests

def home(request):
    return render(request, 'issues/home.html')

def login(request):
    return render(request, 'issues/login.html')

@login_required
def select_repository(request):
    if request.method == 'POST':
        repo_url = request.POST.get('repo_url', '')
        try:
            # Extract owner and repo from URL like https://github.com/owner/repo
            parts = repo_url.strip('/').split('/')
            owner, repo = parts[-2], parts[-1]
            return redirect('issues_list', owner=owner, repo=repo)
        except:
            return render(request, 'issues/select_repository.html', {'error': 'Invalid repository URL'})
    
    return render(request, 'issues/select_repository.html')

@login_required
def issues_list(request, owner, repo):
    social = request.user.social_auth.get(provider='github')
    access_token = social.extra_data['access_token']
    
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get repository info
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    repo_response = requests.get(repo_url, headers=headers)
    
    if repo_response.status_code != 200:
        return render(request, 'issues/error.html', {
            'message': 'Repository not found or access denied'
        })
    
    # Get issues
    issues_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    response = requests.get(issues_url, headers=headers, params={'state': 'all'})
    
    if response.status_code == 200:
        issues = response.json()
        return render(request, 'issues/issues_list.html', {
            'issues': issues,
            'owner': owner,
            'repo': repo,
            'repo_data': repo_response.json()
        })
    else:
        return render(request, 'issues/error.html', {
            'message': 'Failed to fetch issues'
        }) 