import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
import requests
import re

logger = logging.getLogger('issues')


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
        except Exception as e:
            logger.error(
                f"Invalid repository URL: {repo_url}. Error: {str(e)}")
            return render(request, 'issues/select_repository.html', {'error': 'Invalid repository URL'})

    return render(request, 'issues/select_repository.html')


@login_required
def issues_list(request, owner, repo):
    social = request.user.social_auth.get(provider='github')
    access_token = social.extra_data['access_token']

    logger.info(f"Attempting to access repository {owner}/{repo}")

    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # First check what permissions we have
    user_url = 'https://api.github.com/user'
    user_response = requests.get(user_url, headers=headers)
    logger.info(f"User API response status: {user_response.status_code}")
    if user_response.status_code == 200:
        logger.info(f"Authenticated as: {user_response.json().get('login')}")

    # Check installation permissions
    installation_url = f'https://api.github.com/user/installations'
    install_response = requests.get(installation_url, headers=headers)
    logger.info(f"Installation API response: {install_response.status_code}")
    if install_response.status_code == 200:
        logger.info(f"Installations: {install_response.text}")

    # Get repository info
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    repo_response = requests.get(repo_url, headers=headers)

    logger.info(f"Repository API response status: {repo_response.status_code}")
    if repo_response.status_code != 200:
        error_message = repo_response.json().get('message', 'Unknown error')
        logger.error(
            f"Failed to fetch repository {owner}/{repo}. Status code: {repo_response.status_code}, Error: {error_message}")
        return render(request, 'issues/error.html', {
            'message': f'Repository access error: {error_message}'
        })

    # Get issues
    issues_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    response = requests.get(issues_url, headers=headers,
                            params={'state': 'all'})

    logger.info(f"Issues API response status: {response.status_code}")
    if response.status_code == 200:
        issues = response.json()
        return render(request, 'issues/issues_list.html', {
            'issues': issues,
            'owner': owner,
            'repo': repo,
            'repo_data': repo_response.json()
        })
    else:
        error_message = response.json().get('message', 'Unknown error')
        logger.error(
            f"Failed to fetch issues for {owner}/{repo}. Status code: {response.status_code}, Error: {error_message}")
        return render(request, 'issues/error.html', {
            'message': f'Failed to fetch issues: {error_message}'
        })


def logout_view(request):
    return render(request, 'registration/logout.html')


@login_required
def proxy_github_asset(request, path):
    """Proxy requests to GitHub assets with proper authentication."""
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    try:
        social = request.user.social_auth.get(provider='github')
        access_token = social.extra_data['access_token']

        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3.raw',
        }

        # Reconstruct the full GitHub URL
        github_url = f'https://github.com/{path}'

        # Make the authenticated request to GitHub
        response = requests.get(github_url, headers=headers, stream=True)

        if response.status_code == 200:
            # Stream the response back to the client
            return HttpResponse(
                response.raw.read(),
                content_type=response.headers.get(
                    'content-type', 'application/octet-stream')
            )
        else:
            logger.error(
                f"Failed to fetch GitHub asset: {response.status_code}")
            return HttpResponse(status=response.status_code)

    except Exception as e:
        logger.error(f"Error proxying GitHub asset: {str(e)}")
        return HttpResponse(status=500)
