from typing import Dict, Any
from organizational_structure.models import Direction, Sector
from reports.models import Report
from authenticate.models import ProfessionalUser

class DashboardService:
    """
    Serviço responsável pela agregação de dados para o Dashboard.
    """

    @staticmethod
    def get_dashboard_data(user: ProfessionalUser) -> Dict[str, int]:
        """
        Retorna os dados consolidados para o dashboard do usuário.
        
        Args:
            user (ProfessionalUser): O usuário logado.
            
        Returns:
            dict: Dicionário contendo as contagens de relatórios, setores, etc.
        """
        total_reports_user = Report.objects.filter(professional=user).count()
        total_reports = Report.objects.all().count()
        total_sectors = Sector.objects.all().count()
        total_directions = Direction.objects.all().count()
        total_reports_accountable = Report.objects.all().filter(pro_accountable=user).count()
        
        return {
            'total_reports': total_reports,
            'total_reports_user': total_reports_user,
            'total_sectors': total_sectors,
            'total_directions': total_directions,
            'total_reports_accountable': total_reports_accountable,
        }
