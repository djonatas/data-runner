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
    JobsConfig, ExecutionOptions, Variable, VariableType
)
from .connections import ConnectionFactory
from .repository import DuckDBRepository
from .variable_processor import VariableProcessor
from .dependency_manager import DependencyManager
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
                
                # Detectar ciclos
                cycles = self.dependency_manager.detect_cycles()
                if cycles:
                    self.logger.warning(f"Ciclos detectados: {cycles}")
                else:
                    self.logger.info("Dependências validadas com sucesso")
            
            self.logger.info("Configurações carregadas com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            raise
    
    def _parse_connections_config(self, data: dict) -> ConnectionsConfig:
        """Converte dados JSON em ConnectionsConfig"""
        from .types import ConnectionType, ConnectionParams
        
        connections = []
        for conn_data in data.get("connections", []):
            # Converter tipo de string para enum
            conn_type = ConnectionType(conn_data["type"])
            
            # Criar parâmetros
            params = ConnectionParams(**conn_data["params"])
            
            # Criar conexão
            connection = Connection(
                name=conn_data["name"],
                type=conn_type,
                params=params
            )
            connections.append(connection)
        
        return ConnectionsConfig(
            default_duckdb_path=data["defaultDuckDbPath"],
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
        
        return JobsConfig(jobs=jobs, variables=variables)
    
    def get_job(self, query_id: str) -> Optional[Job]:
        """Obtém job por query_id"""
        if not self.jobs_config:
            return None
        
        for job in self.jobs_config.jobs:
            if job.query_id == query_id:
                return job
        return None
    
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
        
        # Buscar conexão
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
            self.logger.info(f"Conexão: {job.connection}")
            self.logger.info(f"Tipo: {job.type.value}")
            self.logger.info(f"Tabela alvo: {target_table}")
            
            # Processar SQL (apenas para conexões que não são CSV)
            sql = None
            if job.sql and connection_config.type.value != "csv":
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
            elif connection_config.type.value == "csv":
                self.logger.info("Processando arquivo CSV (sem SQL)")
            else:
                raise ValueError("Job deve ter SQL definido para conexões de banco de dados")
            
            if options.dry_run:
                self.logger.info("DRY RUN - Nenhuma execução será realizada")
                job_run.status = JobStatus.SUCCESS
                job_run.rowcount = 0
                job_run.finished_at = datetime.now().isoformat()
                return job_run
            
            # Executar query
            db_connection = ConnectionFactory.create_connection(connection_config)
            
            try:
                df = db_connection.execute_query(sql)
                rowcount = len(df)
                
                self.logger.info(f"Query executada com sucesso. Linhas retornadas: {rowcount}")
                
                # Salvar resultado baseado no tipo
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
                
                job_run.status = JobStatus.SUCCESS
                job_run.rowcount = rowcount
                
            finally:
                db_connection.close()
            
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
        
        for query_id in execution_order:
            # Pular se já foi executado ou falhou
            if query_id in completed_jobs or query_id in failed_jobs:
                continue
            
            # Verificar se pode executar (dependências atendidas)
            if self.dependency_manager and not self.dependency_manager.can_execute_job(query_id, completed_jobs):
                self.logger.warning(f"Job {query_id} não pode ser executado - dependências não atendidas")
                failed_jobs.add(query_id)
                continue
            
            try:
                self.logger.info(f"Executando job {query_id}")
                result = self.run_job(query_id, options)
                results.append(result)
                
                if result.status == JobStatus.SUCCESS:
                    completed_jobs.add(query_id)
                    self.logger.info(f"Job {query_id} executado com sucesso")
                else:
                    failed_jobs.add(query_id)
                    self.logger.error(f"Job {query_id} falhou")
                    
            except Exception as e:
                self.logger.error(f"Erro ao executar job {query_id}: {e}")
                failed_jobs.add(query_id)
                
                # Criar JobRun de erro
                job_run = JobRun.create_new(query_id, JobType.CARGA)  # Tipo padrão
                job_run.status = JobStatus.ERROR
                job_run.error = str(e)
                job_run.finished_at = datetime.now().isoformat()
                results.append(job_run)
        
        return results
    
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
