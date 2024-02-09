import os.path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.challenges import base64
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
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://mail.google.com/"
]

class GoogleAPI:
    # Classe que obtém as credenciais para que seja realizada a conexão
    # com as APIs disponibilizadas pelo Google.

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
                if api_query.get('students'):
                    students_data.append(api_query.get('students'))

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
                else:
                    course['students'] = ''
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

    def send_invitations(self, course_id, receipt_list):
        try:
            service = build("classroom", "v1", credentials=self.creds)

            for email in receipt_list:
                # invitation = service.invitations().create(body={'courseId':course_id, 'role':'STUDENT', 'userId': email}).execute()
                print(f'convite NÃO enviado para {email}. ')
        except HttpError as error:
            print(f"An error has ocurred: {error}")

    def send_email(self, email_list, subject: str, content: str):
        try:
            service = build("gmail", "v1", credentials=self.creds)
            
            message = EmailMessage()
            message.set_content(content)
            message.set_type("text/html")
            message.set_charset("UTF-8")

            message["To"] = "romeuborges19@gmail.com" 
            message["From"] = "comais@mail.uft.edu.br"
            message["Subject"] = subject
            print(message)

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"raw": encoded_message}

            send_message = (
                service.users().messages().send(userId="me", body=create_message).execute()
            )

            print(f'message id: {send_message["id"]}')
        except HttpError as error:
            print(f"An error occurred: {error}")

    def call_gmail(self):
        try:
            service = build("gmail", "v1", credentials=self.creds)
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            if not labels:
                print("No labels found.")
                return
            print("Labels:")
            for label in labels:
                print(label["name"])

        except HttpError as error:
            print(f"An error occurred: {error}")
