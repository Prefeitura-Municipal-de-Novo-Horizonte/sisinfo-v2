"""
Serviço para operações com Fornecedores.

Este módulo contém a lógica de negócio de Supplier,
usando ServiceResult para retornos padronizados.
"""
from typing import Optional
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.forms import BaseInlineFormSet

from core.services import ServiceResult
from .models import Supplier, Contact
from .forms import SupplierForm
from bidding_procurement.models import Bidding, MaterialBidding


class SupplierService:
    """
    Serviço responsável pela lógica de negócios relacionada a Fornecedores.
    
    Usa ServiceResult para retornos padronizados.
    """

    @staticmethod
    def get_all_suppliers() -> QuerySet[Supplier]:
        """Retorna todos os fornecedores cadastrados."""
        return Supplier.objects.all()

    @staticmethod
    def get_supplier_by_slug(slug: str) -> ServiceResult:
        """
        Retorna um fornecedor específico pelo slug.
        
        Args:
            slug: Slug do fornecedor
            
        Returns:
            ServiceResult com Supplier ou erro 404
        """
        try:
            supplier = Supplier.objects.get(slug=slug)
            return ServiceResult.ok(data=supplier)
        except Supplier.DoesNotExist:
            return ServiceResult.fail(error="Fornecedor não encontrado.")

    @staticmethod
    def create_supplier(form: SupplierForm, form_contact: BaseInlineFormSet) -> ServiceResult:
        """
        Cria um novo fornecedor e seus contatos.
        
        Args:
            form: Formulário do fornecedor
            form_contact: Formset de contatos
            
        Returns:
            ServiceResult com Supplier criado ou erros
        """
        if not form.is_valid():
            return ServiceResult.fail(
                error="Dados do fornecedor inválidos.",
                errors=list(form.errors.values())
            )
        
        if not form_contact.is_valid():
            return ServiceResult.fail(
                error="Dados de contato inválidos.",
                errors=list(form_contact.errors)
            )
        
        try:
            supplier = form.save()
            form_contact.instance = supplier
            form_contact.save()
            return ServiceResult.ok(
                data=supplier,
                message=f"Fornecedor {supplier.trade} criado com sucesso!"
            )
        except Exception as e:
            return ServiceResult.fail(error=str(e))

    @staticmethod
    def update_supplier(form: SupplierForm, form_contact: BaseInlineFormSet) -> ServiceResult:
        """
        Atualiza um fornecedor e seus contatos.
        
        Args:
            form: Formulário do fornecedor
            form_contact: Formset de contatos
            
        Returns:
            ServiceResult de sucesso ou erros
        """
        if not form.is_valid():
            return ServiceResult.fail(
                error="Dados do fornecedor inválidos.",
                errors=list(form.errors.values())
            )
        
        if not form_contact.is_valid():
            return ServiceResult.fail(
                error="Dados de contato inválidos.",
                errors=list(form_contact.errors)
            )
        
        try:
            supplier = form.save()
            form_contact.save()
            return ServiceResult.ok(
                data=supplier,
                message=f"Fornecedor {supplier.trade} atualizado com sucesso!"
            )
        except Exception as e:
            return ServiceResult.fail(error=str(e))

    @staticmethod
    def delete_supplier(supplier: Supplier) -> ServiceResult:
        """
        Exclui um fornecedor.
        
        Args:
            supplier: Instância de Supplier
            
        Returns:
            ServiceResult de sucesso ou erro
        """
        try:
            name = supplier.trade
            supplier.delete()
            return ServiceResult.ok(message=f"Fornecedor {name} excluído com sucesso!")
        except Exception as e:
            return ServiceResult.fail(error=str(e))

    @staticmethod
    def delete_contact(contact_id: int) -> ServiceResult:
        """
        Exclui um contato de fornecedor.
        
        Args:
            contact_id: ID do contato
            
        Returns:
            ServiceResult com supplier e mensagem
        """
        try:
            contact = Contact.objects.get(id=contact_id)
            supplier = contact.supplier
            contact_value = contact.value
            contact.delete()
            return ServiceResult.ok(
                data=supplier,
                message=f"Contato {contact_value} excluído com sucesso!"
            )
        except Contact.DoesNotExist:
            return ServiceResult.fail(error="Contato não encontrado.")
        except Exception as e:
            return ServiceResult.fail(error=str(e))

    @staticmethod
    def get_supplier_details(slug: str) -> ServiceResult:
        """
        Retorna todos os detalhes relacionados a um fornecedor.
        
        Args:
            slug: Slug do fornecedor
            
        Returns:
            ServiceResult com contexto ou erro
        """
        try:
            supplier = Supplier.objects.get(slug=slug)
        except Supplier.DoesNotExist:
            return ServiceResult.fail(error="Fornecedor não encontrado.")
        
        contacts = Contact.objects.filter(supplier=supplier)
        materials = MaterialBidding.objects.filter(supplier=supplier)
        biddings = Bidding.objects.filter(
            material_associations__supplier=supplier
        ).distinct()
        
        return ServiceResult.ok(data={
            'supplier': supplier,
            'contacts': contacts,
            'materials': materials,
            'biddings': biddings,
        })
