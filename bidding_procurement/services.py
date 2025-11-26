from typing import Tuple, Optional, Union
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import Bidding, Material, MaterialBidding
from .forms import BiddingForm, MaterialBiddingForm, MaterialForm

class BiddingService:
    """
    Serviço responsável pela lógica de negócios relacionada a Licitações.
    """
    
    @staticmethod
    def get_all_biddings() -> QuerySet[Bidding]:
        """Retorna todas as licitações cadastradas."""
        return Bidding.objects.all()

    @staticmethod
    def get_bidding_by_slug(slug: str) -> Bidding:
        """Retorna uma licitação específica pelo slug ou 404 se não encontrada."""
        return get_object_or_404(Bidding, slug=slug)

    @staticmethod
    def create_bidding(form: BiddingForm) -> Optional[Bidding]:
        """
        Cria uma nova licitação a partir de um formulário validado.
        
        Args:
            form (BiddingForm): Formulário preenchido.
            
        Returns:
            Bidding: A instância criada se sucesso, None caso contrário.
        """
        if form.is_valid():
            return form.save()
        return None

    @staticmethod
    def update_bidding(bidding: Bidding, form: BiddingForm) -> Optional[Bidding]:
        """
        Atualiza uma licitação existente.
        
        Args:
            bidding (Bidding): Instância a ser atualizada.
            form (BiddingForm): Formulário com novos dados.
            
        Returns:
            Bidding: A instância atualizada se sucesso, None caso contrário.
        """
        if form.is_valid():
            return form.save()
        return None

    @staticmethod
    def delete_bidding(bidding: Bidding) -> None:
        """Exclui uma licitação."""
        bidding.delete()

    @staticmethod
    def toggle_status(bidding: Bidding) -> str:
        """
        Alterna o status da licitação entre Ativo ('1') e Inativo ('2').
        
        Returns:
            str: Mensagem de sucesso descrevendo a ação realizada.
        """
        if bidding.status == '1':
            bidding.status = '2'
            msg = f"A licitação {bidding.name} foi desativada com sucesso!"
        else:
            bidding.status = '1'
            msg = f"A licitação {bidding.name} foi ativada com sucesso!"
        bidding.save()
        return msg

    @staticmethod
    def add_material_to_bidding(bidding: Bidding, form: MaterialBiddingForm) -> Tuple[bool, str]:
        """
        Vincula um material a uma licitação.
        
        Args:
            bidding (Bidding): A licitação alvo.
            form (MaterialBiddingForm): Formulário com dados da vinculação.
            
        Returns:
            tuple: (bool success, str message)
        """
        if form.is_valid():
            material_bidding = form.save(commit=False)
            material_bidding.bidding = bidding
            try:
                material_bidding.save()
                return True, "Material vinculado com sucesso!"
            except IntegrityError:
                return False, "Este material já está vinculado a esta licitação!"
        return False, "Erro ao vincular material. Verifique os dados."

    @staticmethod
    def toggle_material_status(material_bidding_id: int) -> Tuple[MaterialBidding, str]:
        """
        Alterna o status de um material dentro de uma licitação.
        
        Args:
            material_bidding_id (int): ID da relação MaterialBidding.
            
        Returns:
            tuple: (MaterialBidding instance, str message)
        """
        material_bidding = get_object_or_404(MaterialBidding, id=material_bidding_id)
        if material_bidding.status == '1':
            material_bidding.status = '2'
            msg = f"O material {material_bidding.material.name} foi desativado nesta licitação!"
        else:
            material_bidding.status = '1'
            msg = f"O material {material_bidding.material.name} foi ativado nesta licitação!"
        material_bidding.save()
        return material_bidding, msg

class MaterialService:
    """
    Serviço responsável pela lógica de negócios relacionada a Materiais.
    """
    
    @staticmethod
    def get_all_materials() -> QuerySet[Material]:
        """Retorna todos os materiais cadastrados."""
        return Material.objects.all()

    @staticmethod
    def get_material_by_slug(slug: str) -> Material:
        """Retorna um material específico pelo slug ou 404 se não encontrado."""
        return get_object_or_404(Material, slug=slug)

    @staticmethod
    def create_material(form: MaterialForm) -> Optional[Material]:
        """Cria um novo material."""
        if form.is_valid():
            return form.save()
        return None

    @staticmethod
    def update_material(material: Material, form: MaterialForm) -> Optional[Material]:
        """Atualiza um material existente."""
        if form.is_valid():
            return form.save()
        return None

    @staticmethod
    def delete_material(material: Material) -> None:
        """Exclui um material."""
        material.delete()
