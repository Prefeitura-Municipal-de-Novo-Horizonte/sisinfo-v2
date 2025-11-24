from django import forms

from dashboard.models import MaterialBidding


class MaterialBiddingForm(forms.ModelForm):
    """
    Form para vincular um Material a uma Licitação.
    
    Este form é usado para adicionar materiais existentes a uma licitação
    ou gerenciar o status de materiais já vinculados.
    """
    class Meta:
        model = MaterialBidding
        fields = ['material', 'status', 'price_snapshot']
    
    def __init__(self, *args, bidding=None, exclude_materials=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se há uma licitação especificada, filtra materiais disponíveis
        if bidding and not self.instance.pk:
            from dashboard.models import Material
            # Mostra apenas materiais que NÃO estão nesta licitação
            already_in = MaterialBidding.objects.filter(
                bidding=bidding
            ).values_list('material_id', flat=True)
            
            self.fields['material'].queryset = Material.objects.exclude(
                id__in=already_in
            )
        
        # Aplicar estilos Tailwind
        for field in self.fields.values():
            field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
