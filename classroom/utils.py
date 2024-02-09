import csv
from difflib import SequenceMatcher
import io

class EnrolledStudentsListDoesNotExist(Exception):
    pass

class ApprovedStudentsListDoesNotExist(Exception):
    pass 

class MissingStudentListDoesNotExist(Exception):
    pass

class ListsDoesNotExist(Exception):
    pass


def is_ajax(request):
    # Método que verifica se requisição é Ajax
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def get_missing_list(lists):
    # Função que gera lista de alunos faltantes de um grupo a partir da comparação 
    # entre a lista de alunos aprovados e a lista de alunos já matriculados
    enrolled = lists.enrolled_list
    if not enrolled:
        raise EnrolledStudentsListDoesNotExist()

    approved = lists.approved_list
    if not approved:
        raise ApprovedStudentsListDoesNotExist()

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
    # Podem existir alunos que estão matriculados no curso, mas foram registrados
    # na lista de alunos faltantes. Esta função obtém alunos com nomes semelhantes
    # na lista de matriculados e de alunos faltantes e disponibiliza as comparações
    # para que a lista de alunos faltantes seja ajustada manualmente.

    if not lists:
        raise ListsDoesNotExist("Listas não definidas.")

    enrolled = lists.enrolled_list
    if not enrolled:
        raise EnrolledStudentsListDoesNotExist("Lista de alunos matriculados não foi registrada.")

    approved = lists.approved_list
    if not approved:
        raise ApprovedStudentsListDoesNotExist("Lista de alunos aprovados não foi registrada.")

    missing = lists.missing_list
    if not missing:
        raise MissingStudentListDoesNotExist("Lista de alunos faltantes não foi registrada.")

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
        next = False
        for fullname in enrolled_fullnames:
            missing_name_split = missing_student['fullname'].split(' ')
            fullname_split = fullname.split(' ')

            if missing_name_split[0] == fullname_split[0]:
                similarity = similar(missing_student['fullname'], fullname)
                if similarity == 1:
                    lists.missing_list.remove(missing_student)
                    next = True
                if similarity > 0.3 and not next:
                    comparison = [missing_student['fullname'], fullname, enrolled_emails[enrolled_fullnames.index(fullname)]]

                    if lists.unknown_list:
                        if comparison not in lists.unknown_list:
                            comparisons.append(comparison)
                    else:
                        comparisons.append(comparison)
        if next:
            continue

        lists.save()
    return comparisons

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def read_csv(file):
    # Função que lê arquivo csv que possui colunas "fullname" e "email" 
    # e retorna lista com seu conteúdo.
    f = io.TextIOWrapper(file)

    reader = csv.DictReader(f)
    content = []

    for row in reader:
        content.append({
            "fullname": row['fullname'], 
            "email": row['email']
        })    

    return content

def get_recipient_list(email_list):
    recipient_list = ''
    for recipient in email_list:
        sep = ', '
        if email_list.index(recipient) == (len(email_list)-1):
            sep = '.'
        recipient_list += (recipient + sep) 
    return recipient_list

