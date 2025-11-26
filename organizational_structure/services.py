from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.forms import ModelForm

from .models import Direction, Sector
from reports.models import Report

class StructureService:
    """
    Serviço responsável pela lógica de negócios relacionada à Estrutura Organizacional (Diretorias e Setores).
    """

    # --- Direction Methods ---
    @staticmethod
    def get_all_directions() -> QuerySet[Direction]:
        """Retorna todas as diretorias cadastradas."""
        return Direction.objects.all()

    @staticmethod
    def get_direction_by_slug(slug: str) -> Direction:
        """Retorna uma diretoria específica pelo slug ou 404 se não encontrada."""
        return get_object_or_404(Direction, slug=slug)

    @staticmethod
    def create_direction(form: ModelForm) -> bool:
        """
        Cria uma nova diretoria.
        
        Args:
            form (ModelForm): Formulário da diretoria.
            
        Returns:
            bool: True se sucesso, False caso contrário.
        """
        if form.is_valid():
            form.save()
            return True
        return False

    @staticmethod
    def update_direction(form: ModelForm) -> bool:
        """
        Atualiza uma diretoria existente.
        
        Args:
            form (ModelForm): Formulário da diretoria.
            
        Returns:
            bool: True se sucesso, False caso contrário.
        """
        if form.is_valid():
            form.save()
            return True
        return False

    @staticmethod
    def delete_direction(direction: Direction) -> None:
        """Exclui uma diretoria."""
        direction.delete()

    @staticmethod
    def get_direction_details(slug: str) -> Dict[str, Any]:
        """
        Retorna detalhes da diretoria e seus setores.
        
        Args:
            slug (str): Slug da diretoria.
            
        Returns:
            dict: Contexto com diretoria, setores e total_setores.
        """
        diretoria = get_object_or_404(Direction, slug=slug)
        setores = Sector.objects.filter(direction=diretoria.id)
        total_setores = setores.count()
        
        return {
            'diretoria': diretoria,
            'setores': setores,
            'total_setores': total_setores,
        }

    # --- Sector Methods ---
    @staticmethod
    def get_all_sectors() -> QuerySet[Sector]:
        """Retorna todos os setores cadastrados."""
        return Sector.objects.all()

    @staticmethod
    def get_sector_by_slug(slug: str) -> Sector:
        """Retorna um setor específico pelo slug ou 404 se não encontrado."""
        return get_object_or_404(Sector, slug=slug)

    @staticmethod
    def create_sector(form: ModelForm) -> bool:
        """
        Cria um novo setor.
        
        Args:
            form (ModelForm): Formulário do setor.
            
        Returns:
            bool: True se sucesso, False caso contrário.
        """
        if form.is_valid():
            form.save()
            return True
        return False

    @staticmethod
    def update_sector(form: ModelForm) -> bool:
        """
        Atualiza um setor existente.
        
        Args:
            form (ModelForm): Formulário do setor.
            
        Returns:
            bool: True se sucesso, False caso contrário.
        """
        if form.is_valid():
            form.save()
            return True
        return False

    @staticmethod
    def delete_sector(sector: Sector) -> None:
        """Exclui um setor."""
        sector.delete()

    @staticmethod
    def get_sector_details(slug: str) -> Dict[str, Any]:
        """
        Retorna detalhes do setor e seus relatórios.
        
        Args:
            slug (str): Slug do setor.
            
        Returns:
            dict: Contexto com setor e reports.
        """
        setor = get_object_or_404(Sector, slug=slug)
        reports = Report.objects.filter(sector=setor)
        
        return {
            'setor': setor,
            'reports': reports,
        }
