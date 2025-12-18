from fiscal.models import Invoice, InvoiceItem

class Command(BaseCommand):
    help = 'Remove todas as notas fiscais e seus itens (Reset para testes)'

    def handle(self, *args, **options):
        self.stdout.write("Apagando itens de nota...")
        count_items, _ = InvoiceItem.objects.all().delete()
        self.stdout.write(f"{count_items} itens removidos.")

        self.stdout.write("Apagando notas fiscais...")
        count_invoices, _ = Invoice.objects.all().delete()
        self.stdout.write(f"{count_invoices} notas removidas.")

        self.stdout.write(self.style.SUCCESS('Sucesso! Base de notas limpa.'))
