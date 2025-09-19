"""
Orquestrador principal para execução de jobs
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from .types import (
    Job, JobRun, JobType, JobStatus, Connection, ConnectionsConfig, 
    JobsConfig, ExecutionOptions, Variable, VariableType, JobGroup
)
from .connections import ConnectionFactory
from .repository import DuckDBRepository
from .variable_processor import VariableProcessor
from .dependency_manager import DependencyManager
from .env_processor import EnvironmentVariableProcessor
from .validation_engine import ValidationEngine
from .sql_utils import (
    expand_env_vars, apply_limit, sanitize_table_name, 
    get_default_target_table, truncate_sql_for_log
)


class JobRunner:
    """Orquestrador principal para execução de jobs"""
    
    def __init__(self, config_dir: str = "config"):
        """
        Inicializa o runner
        
        Args:
            config_dir: Diretório com arquivos de configuração
        """
        self.config_dir = config_dir
        self.connections_config: Optional[ConnectionsConfig] = None
        self.jobs_config: Optional[JobsConfig] = None
        self.repository: Optional[DuckDBRepository] = None
        self.variable_processor: Optional[VariableProcessor] = None
        self.dependency_manager: Optional[DependencyManager] = None
        self.validation_engine: Optional[ValidationEngine] = None
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_configs(self):
        """Carrega configurações dos arquivos JSON"""
        try:
            # Carregar conexões
            connections_path = os.path.join(self.config_dir, "connections.json")
            with open(connections_path, 'r', encoding='utf-8') as f:
                connections_data = json.load(f)
            
            self.connections_config = self._parse_connections_config(connections_data)
            
            # Carregar jobs
            jobs_path = os.path.join(self.config_dir, "jobs.json")
            with open(jobs_path, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            
            self.jobs_config = self._parse_jobs_config(jobs_data)
            
            # Inicializar repositório
            self.repository = DuckDBRepository(self.connections_config.default_duckdb_path)
            
            # Inicializar processador de variáveis
            if self.jobs_config and self.jobs_config.variables:
                self.variable_processor = VariableProcessor(self.jobs_config.variables)
                self.logger.info(f"Processador de variáveis inicializado com {len(self.jobs_config.variables)} variáveis")
            else:
                self.variable_processor = VariableProcessor()
            
            # Inicializar gerenciador de dependências
            if self.jobs_config:
                self.dependency_manager = DependencyManager(self.jobs_config.jobs)
                
                # Validar dependências
                errors = self.dependency_manager.validate_dependencies()
                if errors:
                    self.logger.warning(f"Dependências inválidas encontradas: {errors}")
                else:
                    self.logger.info("Dependências validadas com sucesso")
                
                # Detectar ciclos
                cycles = self.dependency_manager.detect_cycles()
                if cycles:
                    self.logger.warning(f"Ciclos detectados: {cycles}")
            
            # Inicializar motor de validação
            self.validation_engine = ValidationEngine()
            
            self.logger.info("Configurações carregadas com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            raise
    
    def _parse_connections_config(self, data: dict) -> ConnectionsConfig:
        """Converte dados JSON em ConnectionsConfig"""
        from .types import ConnectionType, ConnectionParams
        
        # Processar variáveis de ambiente nos dados
        env_processor = EnvironmentVariableProcessor()
        processed_data = env_processor.process_dict(data)
        
        connections = []
        for conn_data in processed_data.get("connections", []):
            # Converter tipo de string para enum
            conn_type = ConnectionType(conn_data["type"])
            
            # Criar parâmetros (já processados com variáveis de ambiente)
            params = ConnectionParams(**conn_data["params"])
            
            # Criar conexão
            connection = Connection(
                name=conn_data["name"],
                type=conn_type,
                params=params
            )
            connections.append(connection)
        
        return ConnectionsConfig(
            default_duckdb_path=processed_data["defaultDuckDbPath"],
            connections=connections
        )
    
    def _parse_jobs_config(self, data: dict) -> JobsConfig:
        """Converte dados JSON em JobsConfig"""
        jobs = []
        for job_data in data.get("jobs", []):
            job = Job(
                query_id=job_data["queryId"],
                type=JobType(job_data["type"]),
                connection=job_data["connection"],
                sql=job_data.get("sql"),  # Opcional para conexões CSV
                target_table=job_data.get("targetTable"),
                dependencies=job_data.get("dependencies")  # Lista de dependências
            )
            jobs.append(job)
        
        # Carregar variáveis se existirem
        variables = None
        if "variables" in data:
            variables = {}
            for var_name, var_data in data["variables"].items():
                variable = Variable(
                    name=var_name,
                    value=var_data["value"],
                    type=VariableType(var_data["type"]),
                    description=var_data.get("description")
                )
                variables[var_name] = variable
        
        # Carregar grupos de jobs se existirem
        job_groups = None
        if "job_groups" in data:
            job_groups = {}
            for group_name, group_data in data["job_groups"].items():
                job_group = JobGroup(
                    name=group_name,
                    description=group_data.get("description"),
                    job_ids=group_data.get("job_ids", [])
                )
                job_groups[group_name] = job_group
        
        return JobsConfig(jobs=jobs, variables=variables, job_groups=job_groups)
    
    def get_job(self, query_id: str) -> Optional[Job]:
        """Obtém job por query_id"""
        if not self.jobs_config:
            return None
        
        for job in self.jobs_config.jobs:
            if job.query_id == query_id:
                return job
        return None
    
    def get_job_group(self, group_name: str) -> Optional[JobGroup]:
        """Obtém grupo de jobs por nome"""
        if not self.jobs_config or not self.jobs_config.job_groups:
            return None
        
        return self.jobs_config.job_groups.get(group_name)
    
    def list_job_groups(self) -> List[JobGroup]:
        """Lista todos os grupos de jobs disponíveis"""
        if not self.jobs_config or not self.jobs_config.job_groups:
            return []
        
        return list(self.jobs_config.job_groups.values())
    
    def run_job_group(self, group_name: str, options: ExecutionOptions = None) -> List[JobRun]:
        """Executa um grupo de jobs em sequência"""
        if options is None:
            options = ExecutionOptions()
        
        # Carregar configs se necessário
        if not self.jobs_config:
            self.load_configs()
        
        # Obter grupo
        job_group = self.get_job_group(group_name)
        if not job_group:
            raise ValueError(f"Grupo de jobs não encontrado: {group_name}")
        
        if not job_group.job_ids:
            raise ValueError(f"Grupo '{group_name}' não possui jobs configurados")
        
        self.logger.info(f"Executando grupo de jobs: {group_name}")
        self.logger.info(f"Jobs no grupo: {job_group.job_ids}")
        
        # Executar jobs do grupo
        return self.run_jobs(job_group.job_ids, options)
    
    def list_jobs(self) -> List[Job]:
        """Lista todos os jobs disponíveis"""
        if not self.jobs_config:
            return []
        return self.jobs_config.jobs
    
    def get_connection(self, connection_name: str) -> Optional[Connection]:
        """Obtém conexão por nome"""
        if not self.connections_config:
            return None
        
        for conn in self.connections_config.connections:
            if conn.name == connection_name:
                return conn
        return None
    
    def run_job(self, query_id: str, options: ExecutionOptions = None) -> JobRun:
        """
        Executa um job específico
        
        Args:
            query_id: ID da query
            options: Opções de execução
            
        Returns:
            JobRun com resultado da execução
        """
        if options is None:
            options = ExecutionOptions()
        
        # Carregar configs se necessário
        if not self.connections_config or not self.jobs_config:
            self.load_configs()
        
        # Buscar job
        job = self.get_job(query_id)
        if not job:
            raise ValueError(f"Job não encontrado: {query_id}")
        
        # Buscar conexão (não obrigatória para jobs de validação)
        connection_config = None
        if job.connection:
            connection_config = self.get_connection(job.connection)
            if not connection_config:
                raise ValueError(f"Conexão não encontrada: {job.connection}")
        
        # Criar JobRun
        job_run = JobRun.create_new(query_id, job.type)
        job_run.connection = job.connection
        job_run.started_at = datetime.now().isoformat()
        
        # Determinar tabela alvo
        target_table = options.save_as or job.target_table
        if not target_table:
            target_table = get_default_target_table(query_id, job.type.value)
        
        target_table = sanitize_table_name(target_table)
        job_run.target_table = target_table
        
        try:
            self.logger.info(f"Iniciando execução do job {query_id}")
            self.logger.info(f"Conexão: {job.connection or 'N/A'}")
            self.logger.info(f"Tipo: {job.type.value}")
            self.logger.info(f"Tabela alvo: {target_table}")
            
            # Para jobs de validação, não processar SQL próprio
            if job.type == JobType.VALIDATION:
                self.logger.info("Job de validação - executando validação diretamente")
            else:
                # Processar SQL (apenas para conexões que não são CSV)
                sql = None
                if job.sql and connection_config and connection_config.type.value != "csv":
                    sql = expand_env_vars(job.sql)
                    
                    # Processar variáveis personalizadas
                    if self.variable_processor:
                        try:
                            sql = self.variable_processor.process_sql(sql)
                            self.logger.info("Variáveis processadas com sucesso")
                        except Exception as e:
                            self.logger.error(f"Erro ao processar variáveis: {e}")
                            raise
                    
                    if options.limit:
                        sql = apply_limit(sql, options.limit)
                    
                    self.logger.info(f"SQL: {truncate_sql_for_log(sql)}")
                elif connection_config and connection_config.type.value == "csv":
                    self.logger.info("Processando arquivo CSV (sem SQL)")
                else:
                    raise ValueError("Job deve ter SQL definido para conexões de banco de dados")
            
            if options.dry_run:
                self.logger.info("DRY RUN - Nenhuma execução será realizada")
                job_run.status = JobStatus.SUCCESS
                job_run.rowcount = 0
                job_run.finished_at = datetime.now().isoformat()
                return job_run
            
            # Executar query (apenas para jobs que não são de validação)
            if job.type != JobType.VALIDATION:
                db_connection = ConnectionFactory.create_connection(connection_config)
                
                try:
                    df = db_connection.execute_query(sql)
                    rowcount = len(df)
                    
                    self.logger.info(f"Query executada com sucesso. Linhas retornadas: {rowcount}")
                finally:
                    db_connection.close()
            else:
                # Para jobs de validação, df e rowcount serão definidos na seção de validação
                df = None
                rowcount = 0
            
            # Processar resultado baseado no tipo
            if job.type == JobType.CARGA:
                # Para carga, substituir tabela
                self.repository.save_dataframe(df, target_table, replace=True)
                self.logger.info(f"Dados salvos na tabela {target_table}")
                
            elif job.type == JobType.BATIMENTO:
                # Para batimento, salvar em val_<query_id>
                val_table = f"val_{query_id}"
                val_table = sanitize_table_name(val_table)
                self.repository.save_dataframe(df, val_table, replace=True)
                self.logger.info(f"Resultado de batimento salvo na tabela {val_table}")
                
            elif job.type == JobType.EXPORT_CSV:
                # Para export-csv, exportar para arquivo CSV
                if not job.csv_file:
                    raise ValueError("Job export-csv deve ter 'csv_file' definido")
                
                # Configurar parâmetros CSV com valores padrão
                separator = job.csv_separator or ","
                encoding = job.csv_encoding or "utf-8"
                include_header = job.csv_include_header if job.csv_include_header is not None else True
                
                csv_path = self.repository.export_dataframe_to_csv(
                    df, job.csv_file, separator, encoding, include_header
                )
                
                job_run.csv_file = csv_path
                self.logger.info(f"Dados exportados para CSV: {csv_path}")
                
            elif job.type == JobType.VALIDATION:
                # Para validation, executar validação personalizada
                if not job.validation_file:
                    raise ValueError("Job validation deve ter 'validation_file' definido")
                
                if not job.main_query:
                    raise ValueError("Job validation deve ter 'main_query' definido")
                
                # Buscar dados da query principal
                main_job = self.get_job(job.main_query)
                if not main_job:
                    raise ValueError(f"Job principal não encontrado: {job.main_query}")
                
                main_connection_config = self.get_connection(main_job.connection)
                if not main_connection_config:
                    raise ValueError(f"Conexão do job principal não encontrada: {main_job.connection}")
                
                # Executar query principal
                main_db_connection = ConnectionFactory.create_connection(main_connection_config)
                try:
                    # Processar SQL da query principal
                    main_sql = expand_env_vars(main_job.sql)
                    if self.variable_processor:
                        main_sql = self.variable_processor.process_sql(main_sql)
                    
                    main_df = main_db_connection.execute_query(main_sql)
                    self.logger.info(f"Dados da query principal carregados: {len(main_df)} linhas")
                    
                    # Executar validação
                    context = {
                        "main_query_id": job.main_query,
                        "validation_query_id": query_id,
                        "main_connection": main_job.connection,
                        "validation_connection": job.connection
                    }
                    
                    validation_result = self.validation_engine.execute_validation(
                        job.validation_file, main_df, context
                    )
                    
                    # Armazenar resultado da validação
                    job_run.validation_file = job.validation_file
                    job_run.validation_result = validation_result.to_json()
                    job_run.rowcount = len(main_df)
                    
                    if validation_result.success:
                        self.logger.info(f"Validação executada com sucesso: {validation_result.message}")
                    else:
                        self.logger.warning(f"Validação falhou: {validation_result.message}")
                        # Não falha o job, apenas registra o resultado
                    
                finally:
                    main_db_connection.close()
            
            # Definir status de sucesso
            job_run.status = JobStatus.SUCCESS
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Erro na execução do job {query_id}: {error_msg}")
            job_run.status = JobStatus.ERROR
            job_run.error = error_msg
            job_run.rowcount = 0
        
        finally:
            job_run.finished_at = datetime.now().isoformat()
            
            # Salvar auditoria
            if self.repository:
                self.repository.save_job_run(job_run)
                self.logger.info(f"Auditoria salva. Run ID: {job_run.run_id}")
        
        return job_run
    
    def run_jobs(self, query_ids: List[str], options: ExecutionOptions = None) -> List[JobRun]:
        """
        Executa múltiplos jobs respeitando dependências
        
        Args:
            query_ids: Lista de IDs de queries
            options: Opções de execução
            
        Returns:
            Lista de JobRuns com resultados
        """
        if options is None:
            options = ExecutionOptions()
        
        # Carregar configs se necessário
        if not self.dependency_manager:
            self.load_configs()
        
        results = []
        completed_jobs = set()
        failed_jobs = set()
        
        # Obter ordem de execução considerando dependências
        try:
            if self.dependency_manager:
                # Filtrar apenas jobs solicitados e suas dependências
                all_required_jobs = self._get_all_required_jobs(query_ids)
                execution_order = self._get_execution_order_for_jobs(all_required_jobs)
            else:
                execution_order = query_ids
        except Exception as e:
            self.logger.error(f"Erro ao calcular ordem de execução: {e}")
            # Fallback para execução sequencial
            execution_order = query_ids
        
        self.logger.info(f"Ordem de execução: {execution_order}")
        
        # Logs de progresso melhorados
        total_jobs = len(execution_order)
        start_time = datetime.now()
        
        print(f"\n🚀 Data-Runner - Executando Pipeline")
        print("=" * 80)
        print(f"📋 Jobs: {', '.join(query_ids) if len(query_ids) <= 5 else f'{len(query_ids)} jobs'}")
        print(f"🔄 Ordem de execução: {' → '.join(execution_order[:3])}{'...' if len(execution_order) > 3 else ''}")
        print(f"📊 Total de jobs: {total_jobs}")
        print()
        
        for i, query_id in enumerate(execution_order, 1):
            # Pular se já foi executado ou falhou
            if query_id in completed_jobs or query_id in failed_jobs:
                continue
            
            # Verificar se pode executar (dependências atendidas)
            if self.dependency_manager and not self.dependency_manager.can_execute_job(query_id, completed_jobs):
                print(f"⚠️  Job '{query_id}' não pode ser executado - dependências não atendidas")
                failed_jobs.add(query_id)
                continue
            
            # Calcular tempo decorrido e estimativa
            elapsed_time = datetime.now() - start_time
            avg_time_per_job = elapsed_time.total_seconds() / max(i - 1, 1)
            remaining_jobs = total_jobs - i + 1
            estimated_remaining = avg_time_per_job * remaining_jobs
            
            print(f"⏳ [{i}/{total_jobs}] Executando: {query_id}")
            print(f"⏱️  Tempo decorrido: {self._format_duration(elapsed_time.total_seconds())}")
            if i > 1:
                print(f"🔮 Estimativa restante: {self._format_duration(estimated_remaining)}")
            print()
            
            job_start_time = datetime.now()
            
            try:
                result = self.run_job(query_id, options)
                results.append(result)
                
                job_duration = datetime.now() - job_start_time
                
                if result.status == JobStatus.SUCCESS:
                    completed_jobs.add(query_id)
                    print(f"✅ Job '{query_id}' executado com sucesso!")
                    print(f"📈 Resultados: {result.rowcount or 0} linhas processadas")
                    print(f"⏱️  Tempo: {self._format_duration(job_duration.total_seconds())}")
                    if result.csv_file:
                        print(f"💾 Arquivo CSV: {result.csv_file}")
                    print()
                else:
                    failed_jobs.add(query_id)
                    print(f"❌ Job '{query_id}' falhou: {result.error}")
                    print()
                    
            except Exception as e:
                job_duration = datetime.now() - job_start_time
                print(f"❌ Erro ao executar job '{query_id}': {e}")
                print(f"⏱️  Tempo: {self._format_duration(job_duration.total_seconds())}")
                print()
                failed_jobs.add(query_id)
                
                # Criar JobRun de erro
                job_run = JobRun.create_new(query_id, JobType.CARGA)  # Tipo padrão
                job_run.status = JobStatus.ERROR
                job_run.error = str(e)
                job_run.finished_at = datetime.now().isoformat()
                results.append(job_run)
        
        # Resumo final
        total_time = datetime.now() - start_time
        success_count = len(completed_jobs)
        error_count = len(failed_jobs)
        
        print("🎉 Pipeline executado!")
        print("=" * 80)
        print(f"📊 Total: {total_jobs} jobs")
        print(f"✅ Sucessos: {success_count}")
        print(f"❌ Erros: {error_count}")
        print(f"⏱️  Tempo total: {self._format_duration(total_time.total_seconds())}")
        print()
        
        return results
    
    def _format_duration(self, seconds: float) -> str:
        """
        Formata duração em segundos para formato legível
        
        Args:
            seconds: Duração em segundos
            
        Returns:
            String formatada (ex: "2m 30s", "45s", "1h 15m")
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            if remaining_seconds < 1:
                return f"{minutes}m"
            else:
                return f"{minutes}m {remaining_seconds:.0f}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            if remaining_minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {remaining_minutes}m"
    
    def _get_all_required_jobs(self, query_ids: List[str]) -> List[str]:
        """
        Obtém todos os jobs necessários incluindo dependências
        
        Args:
            query_ids: Lista de jobs solicitados
            
        Returns:
            Lista completa de jobs incluindo dependências
        """
        if not self.dependency_manager:
            return query_ids
        
        required = set(query_ids)
        to_process = list(query_ids)
        
        while to_process:
            current = to_process.pop(0)
            deps = self.dependency_manager.get_job_dependencies(current)
            
            for dep in deps:
                if dep not in required:
                    required.add(dep)
                    to_process.append(dep)
        
        return list(required)
    
    def _get_execution_order_for_jobs(self, query_ids: List[str]) -> List[str]:
        """
        Obtém ordem de execução para jobs específicos
        
        Args:
            query_ids: Lista de jobs
            
        Returns:
            Ordem de execução
        """
        if not self.dependency_manager:
            return query_ids
        
        # Filtrar jobs para incluir apenas os solicitados
        all_jobs = self.dependency_manager.jobs
        filtered_jobs = [job for job in all_jobs.values() if job.query_id in query_ids]
        
        # Criar novo gerenciador apenas com jobs filtrados
        filtered_manager = DependencyManager(filtered_jobs)
        return filtered_manager.get_execution_order()
    
    def list_variables(self) -> Dict[str, Any]:
        """Lista todas as variáveis disponíveis"""
        if not self.variable_processor:
            return {}
        return self.variable_processor.list_variables()
    
    def validate_variables(self) -> Dict[str, str]:
        """Valida todas as variáveis e retorna erros encontrados"""
        if not self.variable_processor:
            return {}
        return self.variable_processor.validate_variables()
    
    def add_variable(self, variable: Variable):
        """Adiciona uma variável ao processador"""
        if not self.variable_processor:
            self.variable_processor = VariableProcessor()
        self.variable_processor.add_variable(variable)
    
    def get_csv_info(self, connection_name: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um arquivo CSV
        
        Args:
            connection_name: Nome da conexão CSV
            
        Returns:
            Informações sobre o arquivo CSV
        """
        connection_config = self.get_connection(connection_name)
        if not connection_config:
            raise ValueError(f"Conexão não encontrada: {connection_name}")
        
        if connection_config.type.value != "csv":
            raise ValueError(f"Conexão {connection_name} não é do tipo CSV")
        
        db_connection = ConnectionFactory.create_connection(connection_config)
        if hasattr(db_connection, 'get_file_info'):
            return db_connection.get_file_info()
        else:
            return {"error": "Conexão CSV não suporta get_file_info"}
    
    def get_execution_order(self) -> List[str]:
        """Retorna ordem de execução dos jobs considerando dependências"""
        if not self.dependency_manager:
            return [job.query_id for job in self.jobs_config.jobs] if self.jobs_config else []
        return self.dependency_manager.get_execution_order()
    
    def get_execution_groups(self) -> List[List[str]]:
        """Retorna grupos de jobs que podem ser executados em paralelo"""
        if not self.dependency_manager:
            return [[job.query_id for job in self.jobs_config.jobs]] if self.jobs_config else []
        return self.dependency_manager.get_execution_groups()
    
    def validate_dependencies(self) -> List[str]:
        """Valida dependências entre jobs"""
        if not self.dependency_manager:
            return []
        return self.dependency_manager.validate_dependencies()
    
    def detect_cycles(self) -> List[List[str]]:
        """Detecta ciclos nas dependências"""
        if not self.dependency_manager:
            return []
        return self.dependency_manager.detect_cycles()
    
    def get_job_dependencies(self, job_id: str) -> List[str]:
        """Retorna dependências de um job"""
        if not self.dependency_manager:
            return []
        return self.dependency_manager.get_job_dependencies(job_id)
    
    def get_dependent_jobs(self, job_id: str) -> List[str]:
        """Retorna jobs que dependem do job especificado"""
        if not self.dependency_manager:
            return []
        return self.dependency_manager.get_dependent_jobs(job_id)
