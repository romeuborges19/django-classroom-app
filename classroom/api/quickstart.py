import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/classroom.courses.readonly"]


def get_courses():
  """Shows basic usage of the Classroom API.
  Prints the names of the first 10 courses the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("classroom/api/token.json"):
    creds = Credentials.from_authorized_user_file("classroom/api/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "classroom/api/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("classroom/api/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("classroom", "v1", credentials=creds)

    # Call the Classroom API
    results = service.courses().list(pageSize=10).execute()
    courses = results.get("courses", [])

    if not courses:
      print("No courses found.")
      return
    # Prints the names of the first 10 courses.
    print("Courses:")

    result = []
    print(courses)
    for course in courses:
        course = {"id": course['id'], "name": course["name"]}
        result.append(course) 
        print(course["name"])

    return result

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
