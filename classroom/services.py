from classroom.models import Lists


class UpdateMissingStudentsList:
    # Classe de serviço que controla a atualização da lista de alunos faltantes.

    def __init__(self, group_id, not_missing_list, missing_list):
        # Definindo o estado interno

        self.lists = Lists.objects.find_by_group_id(group_id)
        self.not_missing_list = not_missing_list
        self.missing_list = missing_list

    def execute(self):
        # Função principal da classe, que trata os dados, salva o 
        # objeto no banco de dados e retorna as listas para a view

        self._clean_not_missing_list()
        self._clean_comparison_list()
        self.lists.save()
        print('sucesso')

    def _clean_not_missing_list(self):
        # Tratando lista de alunos não faltantes
        for item in self.not_missing_list:
            item = item.split(',')
            for student in self.lists.missing_list:
                if student.get('fullname') == item[0]:
                    self.lists.missing_list.remove(student) 

    def _clean_comparison_list(self):
        # Removendo comparações que já foram feitas
        unknown_comparisons = []
        for item in self.missing_list:
            item = item.split(',')
            unknown_comparisons.append(item)
        if self.lists.unknown_list:
            for item in unknown_comparisons:
                self.lists.unknown_list.append(item)
        else:
            self.lists.unknown_list = unknown_comparisons
