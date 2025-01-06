import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests

logger = logging.getLogger('issues')


def home(request):
    return render(request, 'issues/home.html')


def login(_request):
    return redirect('social:begin', 'github')


@login_required
def select_repository(request):
    # Get recent repositories from session
    recent_repos = request.session.get('recent_repos', [])

    if request.method == 'POST':
        repo_url = request.POST.get('repo_url', '')
        try:
            # Extract owner and repo from URL like https://github.com/owner/repo
            parts = repo_url.strip('/').split('/')
            owner, repo = parts[-2], parts[-1]

            # Add to recent repos
            repo_data = {'owner': owner, 'repo': repo,
                         'url': f'https://github.com/{owner}/{repo}'}

            # Remove if already exists (to move it to the top)
            recent_repos = [
                r for r in recent_repos if r['url'] != repo_data['url']]

            # Add to the beginning and limit to 5 recent repos
            recent_repos.insert(0, repo_data)
            recent_repos = recent_repos[:5]

            # Save back to session
            request.session['recent_repos'] = recent_repos
            request.session.modified = True

            return redirect('issues_list', owner=owner, repo=repo)
        except Exception as e:
            logger.error(
                f"Invalid repository URL: {repo_url}. Error: {str(e)}")
            return render(request, 'issues/select_repository.html', {
                'error': 'Invalid repository URL',
                'recent_repos': recent_repos
            })

    return render(request, 'issues/select_repository.html', {'recent_repos': recent_repos})


@login_required
def issues_list(request, owner, repo):
    social = request.user.social_auth.get(provider='github')
    access_token = social.extra_data['access_token']

    logger.info(f"Attempting to access repository {owner}/{repo}")

    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

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

    # Get issues with state and search filter
    issues_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    state = request.GET.get('state', 'closed')  # Default to closed issues
    search_query = request.GET.get('q', '').strip()
    
    params = {'state': state}
    if state == 'all':
        params['state'] = 'all'
    
    response = requests.get(issues_url, headers=headers, params=params)

    logger.info(f"Issues API response status: {response.status_code}")
    if response.status_code == 200:
        issues = response.json()
        
        # Filter issues by search query if provided
        if search_query:
            search_query = search_query.lower()
            filtered_issues = []
            for issue in issues:
                title = issue['title'].lower()
                body = issue.get('body', '').lower() if issue.get('body') else ''
                if search_query in title or search_query in body:
                    filtered_issues.append(issue)
            issues = filtered_issues

        # Add to recent repos if successful
        recent_repos = request.session.get('recent_repos', [])
        repo_data = {'owner': owner, 'repo': repo,
                     'url': f'https://github.com/{owner}/{repo}'}

        # Remove if already exists (to move it to the top)
        recent_repos = [
            r for r in recent_repos if r['url'] != repo_data['url']]

        # Add to the beginning and limit to 5 recent repos
        recent_repos.insert(0, repo_data)
        recent_repos = recent_repos[:5]

        # Save back to session
        request.session['recent_repos'] = recent_repos
        request.session.modified = True

        return render(request, 'issues/issues_list.html', {
            'issues': issues,
            'owner': owner,
            'repo': repo,
            'repo_data': repo_response.json(),
            'current_state': state
        })
    else:
        error_message = response.json().get('message', 'Unknown error')
        logger.error(
            f"Failed to fetch issues for {owner}/{repo}. Status code: {response.status_code}, Error: {error_message}")
        return render(request, 'issues/error.html', {
            'message': f'Failed to fetch issues: {error_message}'
        })
