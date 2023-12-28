from difflib import SequenceMatcher


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def get_missing_list(lists):
    enrolled = lists.enrolled_list
    approved = lists.approved_list
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
            approved_student['email'] = approved_student['email'].strip().lower()
            approved_student['fullname'] = approved_student['fullname'].strip().lower()
            missing.append(approved_student)

    return missing

def get_comparisons(lists):
    enrolled = lists.enrolled_list
    missing = lists.missing_list

    comparisons = []
    enrolled_list = []
    enrolled_emails = []
    enrolled_fullnames = []

    for student_group in enrolled:
        for student in student_group[1]:
            student['email'] = student['email'].strip().lower()
            student['fullname'] = student['fullname'].strip().lower()

            enrolled_list.append(student)
            enrolled_emails.append(student['email'])
            enrolled_fullnames.append(student['fullname'])

    for missing_student in missing:
        for fullname in enrolled_fullnames:
            missing_name_split = missing_student['fullname'].split(' ')
            fullname_split = fullname.split(' ')

            if missing_name_split[0] == fullname_split[0]:
                similarity = similar(missing_student['fullname'], fullname)
                if similarity == 1:
                    ... # TODO: remover estes nomes da lista de alunos faltantes
                if similarity > 0.3:
                    comparison = [missing_student['fullname'], fullname, enrolled_emails[enrolled_fullnames.index(fullname)]]

                    if lists.unknown_list:
                        if comparison not in lists.unknown_list:
                            comparisons.append(comparison)
                    else:
                        comparisons.append(comparison)


    return comparisons

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
