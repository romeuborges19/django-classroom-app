def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def get_missing_students_list(approved, enrolled):
    missing = []
    enrolled_list = []
    enrolled_emails = []
    enrolled_fullnames = []

    # Organizando dados dos alunos matriculados
    for student_group in enrolled:
        for student in student_group[1]:
            student['email'] = student['email'].strip().lower()
            student['fullname'] = student['fullname'].strip().lower()

            enrolled_list.append(student)
            enrolled_emails.append(student['email'])
            enrolled_fullnames.append(student['fullname'])

    # Criando lista inicial de alunos faltantes
    for approved_student in approved:
        if approved_student['email'].strip().lower() not in enrolled_emails:
            missing.append(approved_student)

    return missing
