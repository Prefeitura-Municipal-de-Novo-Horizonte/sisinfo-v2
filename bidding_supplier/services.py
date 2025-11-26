from typing import Optional, Tuple, List
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.forms import BaseInlineFormSet

from .models import Supplier, Contact
from .forms import SupplierForm
from bidding_procurement.models import Bidding, MaterialBidding

class SupplierService:
    """
    Serviço responsável pela lógica de negócios relacionada a Fornecedores.
    """

    @staticmethod
    def get_all_suppliers() -> QuerySet[Supplier]:
        """Retorna todos os fornecedores cadastrados."""
        return Supplier.objects.all()

    @staticmethod
    def get_supplier_by_slug(slug: str) -> Supplier:
        """Retorna um fornecedor específico pelo slug ou 404 se não encontrado."""
        return get_object_or_404(Supplier, slug=slug)

    @staticmethod
    def create_supplier(form: SupplierForm, form_contact: BaseInlineFormSet) -> bool:
        """
        Cria um novo fornecedor e seus contatos.
        
        Args:
            form (SupplierForm): Formulário do fornecedor.
            form_contact (BaseInlineFormSet): Formset de contatos.
            
        Returns:
            bool: True se sucesso, False caso contrário.
        """
        if form.is_valid() and form_contact.is_valid():
            supplier = form.save()
            form_contact.instance = supplier
            form_contact.save()
            return True
        return False

    @staticmethod
    def update_supplier(form: SupplierForm, form_contact: BaseInlineFormSet) -> bool:
        """
        Atualiza um fornecedor e seus contatos.
        
        Args:
            form (SupplierForm): Formulário do fornecedor.
            form_contact (BaseInlineFormSet): Formset de contatos.
            
        Returns:
            bool: True se sucesso, False caso contrário.
        """
        if form.is_valid() and form_contact.is_valid():
            form.save()
            form_contact.save()
            return True
        return False

    @staticmethod
    def delete_supplier(supplier: Supplier) -> bool:
        """
        Exclui um fornecedor.
        
        Returns:
            bool: True se excluído com sucesso (retorno do método delete do Django).
        """
        return supplier.delete()

    @staticmethod
    def delete_contact(contact_id: int) -> Tuple[Supplier, str]:
        """
        Exclui um contato de fornecedor.
        
        Args:
            contact_id (int): ID do contato.
            
        Returns:
            tuple: (Supplier instance, str message)
        """
        contact = get_object_or_404(Contact, id=contact_id)
        supplier = contact.supplier
        contact_value = contact.value
        contact.delete()
        msg = f'O contato {contact_value} do fornecedor {supplier.trade} foi excluido com sucesso!'
        return supplier, msg

    @staticmethod
    def get_supplier_details(slug: str) -> dict:
        """
        Retorna todos os detalhes relacionados a um fornecedor.
        
        Args:
            slug (str): Slug do fornecedor.
            
        Returns:
            dict: Contexto com supplier, contacts, materials e biddings.
        """
        supplier = get_object_or_404(Supplier, slug=slug)
        contacts = Contact.objects.filter(supplier=supplier)
        materials = MaterialBidding.objects.filter(supplier=supplier)
        biddings = Bidding.objects.filter(material_associations__supplier=supplier).distinct()
        
        return {
            'supplier': supplier,
            'contacts': contacts,
            'materials': materials,
            'biddings': biddings,
        }
