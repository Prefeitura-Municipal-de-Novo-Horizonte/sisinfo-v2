"""
Mixins compartilhados para formulários e outras utilidades.
"""


class CapitalizeFieldMixin:
    """
    Mixin para formulários que precisam capitalizar campos de texto.
    
    Fornece o método `extract_from_clean` que capitaliza cada palavra
    de um campo de texto.
    
    Exemplo:
        class MyForm(CapitalizeFieldMixin, forms.ModelForm):
            def clean_name(self):
                return self.extract_from_clean("name")
    """
    
    def extract_from_clean(self, field_name):
        """
        Capitaliza cada palavra de um campo de texto.
        
        Args:
            field_name (str): Nome do campo a ser capitalizado
            
        Returns:
            str: Texto com cada palavra capitalizada
        """
        name = self.cleaned_data.get(field_name)
        if name:
            words = [w.capitalize() for w in name.split()]
            return " ".join(words)
        return name


class TailwindFormMixin:
    """
    Mixin para aplicar estilos Tailwind CSS aos campos do formulário.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"


class TailwindFilterMixin:
    """
    Mixin para aplicar estilos Tailwind CSS aos campos de filtro (FilterSet).
    Estilo tipo 'Search Box' (arredondado, com fundo).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.form.fields.values():
            field.widget.attrs['class'] = "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full"
