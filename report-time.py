import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import json

# Dane dostępowe do JIRA
JIRA_URL = "https://twoja_domena.atlassian.net"
API_ENDPOINT = f"{JIRA_URL}/rest/api/2/search"
USERNAME = "twój_email"
API_TOKEN = "twój_api_token"  # API token wygenerowany w ustawieniach JIRA
USER_XYZ = "XYZ"  # Nazwa użytkownika, dla którego chcesz pobrać zadania

# Zapytanie JQL (Jira Query Language)
jql_query = f'assignee = "{USER_XYZ}" AND status = "In Progress"'

# Parametry zapytania
params = {
    "jql": jql_query,
    "fields": ["key", "summary", "status", "assignee", "timespent"]  # Dodajemy 'timespent'
}

# Wysyłanie zapytania GET do API
response = requests.get(
    API_ENDPOINT,
    params=params,
    auth=HTTPBasicAuth(USERNAME, API_TOKEN),
    headers={"Content-Type": "application/json"}
)

# Funkcja do przeliczania sekund na godziny i minuty
def format_time_spent(seconds):
    if seconds is None:
        return "No time reported"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

# Funkcja do sprawdzenia, czy dzisiaj zaraportowano czas
def check_time_reported_today(issue_key):
    worklog_endpoint = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/worklog"
    worklog_response = requests.get(
        worklog_endpoint,
        auth=HTTPBasicAuth(USERNAME, API_TOKEN),
        headers={"Content-Type": "application/json"}
    )
    
    if worklog_response.status_code == 200:
        worklogs = worklog_response.json()["worklogs"]
        today = datetime.now().date()

        for worklog in worklogs:
            worklog_date = datetime.strptime(worklog['started'], "%Y-%m-%dT%H:%M:%S.%f%z").date()
            if worklog_date == today:
                return True
        return False
    else:
        print(f"Error fetching worklogs for {issue_key}: {worklog_response.status_code}, {worklog_response.text}")
        return False

# Funkcja do raportowania czasu pracy
def report_time(issue_key, time_seconds):
    worklog_endpoint = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/worklog"
    
    # Tworzenie danych do zapytania POST (raportowanie pracy)
    now = datetime.now()
    worklog_data = {
        "timeSpentSeconds": time_seconds,
        "started": now.strftime("%Y-%m-%dT%H:%M:%S.000%z")  # Czas rozpoczęcia pracy
    }
    
    # Wysyłanie żądania POST do JIRA
    worklog_response = requests.post(
        worklog_endpoint,
        auth=HTTPBasicAuth(USERNAME, API_TOKEN),
        headers={"Content-Type": "application/json"},
        data=json.dumps(worklog_data)
    )
    
    if worklog_response.status_code == 201:
        print(f"Time successfully reported for task {issue_key}.")
    else:
        print(f"Error reporting time for {issue_key}: {worklog_response.status_code}, {worklog_response.text}")

# Sprawdzanie, czy odpowiedź jest poprawna
if response.status_code == 200:
    issues = response.json()["issues"]
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        time_spent = issue['fields']['timespent']  # Czas w sekundach
        formatted_time = format_time_spent(time_spent)
        
        # Sprawdzanie, czy dzisiaj zaraportowano czas
        reported_today = check_time_reported_today(key)
        reported_today_text = "Yes" if reported_today else "No"
        
        print(f"Task: {key}, Summary: {summary}, Status: {status}, Time Reported: {formatted_time}, Reported Today: {reported_today_text}")
        
        # Jeśli nie zaraportowano dzisiaj, raportujemy czas
        if not reported_today:
            # Zakładamy, że raportujemy np. 1 godzinę pracy (3600 sekund)
            report_time(key, 3600)
else:
    print(f"Error fetching data: {response.status_code}, {response.text}")
