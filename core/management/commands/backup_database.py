"""
Django management command para criar backups do banco de dados.

Suporta múltiplos ambientes (dev/produção) e formatos (JSON/SQL).
"""
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import subprocess


class Command(BaseCommand):
    help = 'Cria backup do banco de dados (JSON ou SQL)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--environment',
            type=str,
            choices=['dev', 'production', 'current'],
            default='current',
            help='Ambiente do banco de dados (dev, production ou current)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'sql', 'both'],
            default='both',
            help='Formato do backup (json, sql ou both)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Diretório para salvar os backups'
        )
        parser.add_argument(
            '--prefix',
            type=str,
            default='backup',
            help='Prefixo para o nome do arquivo'
        )

    def handle(self, *args, **options):
        environment = options['environment']
        backup_format = options['format']
        output_dir = options['output_dir']
        prefix = options['prefix']

        # Criar diretório de backups se não existir
        os.makedirs(output_dir, exist_ok=True)

        # Timestamp para o nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Determinar qual banco usar
        if environment == 'current':
            db_url = settings.DATABASES['default']
            env_label = 'current'
        else:
            db_url = self._get_database_url(environment)
            env_label = environment

        self.stdout.write(
            self.style.SUCCESS(f'\n🔄 Criando backup do ambiente: {env_label}\n')
        )

        # Criar backup JSON
        if backup_format in ['json', 'both']:
            self._create_json_backup(output_dir, prefix, env_label, timestamp)

        # Criar backup SQL
        if backup_format in ['sql', 'both']:
            self._create_sql_backup(output_dir, prefix, env_label, timestamp, db_url)

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Backup concluído! Arquivos salvos em: {output_dir}/\n')
        )

    def _get_database_url(self, environment):
        """Lê DATABASE_URL do arquivo .env para o ambiente especificado."""
        env_file = os.path.join(settings.BASE_DIR, '.env')
        
        if not os.path.exists(env_file):
            self.stdout.write(
                self.style.ERROR('❌ Arquivo .env não encontrado!')
            )
            return None

        with open(env_file, 'r') as f:
            lines = f.readlines()

        # Procurar pela linha correta
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('DATABASE_URL='):
                if environment == 'dev':
                    # Primeira DATABASE_URL não comentada
                    if 'localhost' in line or '127.0.0.1' in line:
                        return self._parse_database_url(line)
                elif environment == 'production':
                    # DATABASE_URL com domínio externo
                    if 'localhost' not in line and '127.0.0.1' not in line:
                        return self._parse_database_url(line)

        # Procurar em linhas comentadas
        for line in lines:
            line = line.strip()
            if line.startswith('# DATABASE_URL='):
                if environment == 'production':
                    if 'localhost' not in line and '127.0.0.1' not in line:
                        return self._parse_database_url(line.replace('# ', ''))

        self.stdout.write(
            self.style.WARNING(f'⚠️  DATABASE_URL para {environment} não encontrada, usando atual')
        )
        return settings.DATABASES['default']

    def _parse_database_url(self, line):
        """Parse DATABASE_URL para dicionário de configuração."""
        # Extrair URL
        url = line.split('=', 1)[1].strip().strip('"')
        
        # Parse básico (postgres://user:pass@host:port/db)
        import re
        pattern = r'postgres://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)'
        match = re.match(pattern, url)
        
        if match:
            user, password, host, port, dbname = match.groups()
            return {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': dbname,
                'USER': user,
                'PASSWORD': password,
                'HOST': host,
                'PORT': port,
            }
        
        return None

    def _create_json_backup(self, output_dir, prefix, env_label, timestamp):
        """Cria backup em formato JSON usando dumpdata."""
        filename = f'{prefix}_{env_label}_{timestamp}.json'
        filepath = os.path.join(output_dir, filename)

        self.stdout.write(f'📦 Criando backup JSON: {filename}')

        try:
            with open(filepath, 'w') as f:
                call_command(
                    'dumpdata',
                    '--natural-foreign',
                    '--natural-primary',
                    '--indent', '2',
                    stdout=f
                )
            
            # Verificar tamanho do arquivo
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ JSON criado: {filename} ({size_mb:.2f} MB)')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro ao criar JSON: {str(e)}')
            )

    def _create_sql_backup(self, output_dir, prefix, env_label, timestamp, db_config):
        """Cria backup em formato SQL usando pg_dump."""
        filename = f'{prefix}_{env_label}_{timestamp}.sql'
        filepath = os.path.join(output_dir, filename)

        self.stdout.write(f'📦 Criando backup SQL: {filename}')

        # Usar configuração atual se não foi fornecida
        if not db_config:
            db_config = settings.DATABASES['default']

        # Verificar se é PostgreSQL
        if 'postgresql' not in db_config.get('ENGINE', ''):
            self.stdout.write(
                self.style.WARNING('   ⚠️  Backup SQL disponível apenas para PostgreSQL')
            )
            return

        try:
            # Verificar se está usando Docker
            use_docker = self._is_using_docker(db_config)
            
            if use_docker:
                self._create_sql_backup_docker(filepath, db_config, filename)
            else:
                self._create_sql_backup_local(filepath, db_config, filename)
                
        except FileNotFoundError:
            self.stdout.write(
                self.style.WARNING('   ⚠️  pg_dump não encontrado. Instale PostgreSQL client.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro ao criar SQL: {str(e)}')
            )

    def _is_using_docker(self, db_config):
        """Verifica se Docker está disponível para usar pg_dump."""
        try:
            # Verificar se Docker está instalado e rodando
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n')
                # Procurar por containers com 'db' ou 'postgres' no nome
                for container in containers:
                    if 'db' in container.lower() or 'postgres' in container.lower():
                        self.docker_container = container
                        return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return False

    def _create_sql_backup_docker(self, filepath, db_config, filename):
        """Cria backup SQL usando Docker (funciona para qualquer banco!)."""
        self.stdout.write(f'   🐳 Usando Docker container: {self.docker_container}')
        
        host = db_config.get('HOST', 'localhost')
        port = db_config.get('PORT', 5432)
        user = db_config.get('USER', 'postgres')
        dbname = db_config.get('NAME', 'postgres')
        password = db_config.get('PASSWORD', '')
        
        # Mostrar info do banco
        if host not in ['localhost', '127.0.0.1']:
            self.stdout.write(f'   🌐 Conectando em banco remoto: {host}:{port}')
        
        # Comando pg_dump dentro do container
        # Usar variáveis de ambiente para passar senha
        cmd = [
            'docker', 'exec',
            '-e', f'PGPASSWORD={password}',  # Passar senha via env var
            self.docker_container,
            'pg_dump',
            '-h', host,  # Pode ser localhost ou remoto!
            '-p', str(port),
            '-U', user,
            '-d', dbname,
            '--no-owner',
            '--no-acl',
        ]
        
        # Executar e salvar output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Salvar output em arquivo
            with open(filepath, 'w') as f:
                f.write(result.stdout)
            
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ SQL criado: {filename} ({size_mb:.2f} MB)')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro no pg_dump: {result.stderr}')
            )

    def _create_sql_backup_local(self, filepath, db_config, filename):
        """Cria backup SQL usando pg_dump local."""
        cmd = [
            'pg_dump',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config.get('USER', 'postgres'),
            '-d', db_config.get('NAME', 'postgres'),
            '-f', filepath,
            '--no-owner',
            '--no-acl',
        ]

        # Configurar senha via variável de ambiente
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config.get('PASSWORD', '')

        # Executar pg_dump
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ SQL criado: {filename} ({size_mb:.2f} MB)')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro no pg_dump: {result.stderr}')
            )

