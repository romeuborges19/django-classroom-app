import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials, credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.rosters",
    "https://www.googleapis.com/auth/classroom.profile.emails",
    "https://www.googleapis.com/auth/classroom.profile.photos",
]

class GCApi:
    def __init__(self):
        creds = None

        if os.path.exists("classroom/api/token.json"):
            creds = Credentials.from_authorized_user_file("classroom/api/token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "classroom/api/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8080)

            with open("classroom/api/token.json", "w") as token:
                token.write(creds.to_json())

        if creds:
            self.creds = creds
        else:
            self.creds = None

    def get_course_data(self, courses):
        service = build("classroom", "v1", credentials=self.creds)

        try:
            classes_info = []
            for course_id in courses:
                course = service.courses().get(id=course_id).execute()
                api_query = service.courses().students().list(courseId=course_id).execute()
                students_data = []
                students_data.append(api_query['students'])

                while 'nextPageToken' in api_query:
                    api_query = service.courses().students().list(
                        courseId=course_id, 
                        pageToken=api_query['nextPageToken']).execute()

                    students_data.append(api_query['students'])                   

                students_list = []
                i = 1
                for students in students_data:
                    for student in students:
                        students_list.append({"id": i,
                                              "fullname": student['profile']['name']['fullName'], 
                                              "email": student['profile']['emailAddress']})
                        
                        i += 1
                
                course['students'] = students_list
                classes_info.append(course)
            return classes_info
        except HttpError as error:
            print(f"An error has ocurred: {error}")

    def get_courses(self):
        try:
            service = build("classroom", "v1", credentials=self.creds)

            results = service.courses().list(pageSize=10).execute()
            courses = results.get("courses", [])

            if not courses:
                print("No courses found.")
                return
            
            result = []
            for course in courses:
                course = {"id": course['id'], "name": course['name']}
                result.append(course)

            return result
        except HttpError as error:
            print(f"An error has ocurred: {error}")
            
