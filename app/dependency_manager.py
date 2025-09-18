"""
Gerenciador de dependências entre jobs
"""

from typing import List, Dict, Set, Optional
from collections import defaultdict, deque
from .types import Job


class DependencyManager:
    """Gerenciador de dependências entre jobs"""
    
    def __init__(self, jobs: List[Job]):
        """
        Inicializa o gerenciador de dependências
        
        Args:
            jobs: Lista de jobs para analisar dependências
        """
        self.jobs = {job.query_id: job for job in jobs}
        self.dependencies = self._build_dependency_graph()
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Constrói o grafo de dependências
        
        Returns:
            Dicionário com dependências de cada job
        """
        dependencies = defaultdict(set)
        
        for job in self.jobs.values():
            if job.dependencies:
                dependencies[job.query_id] = set(job.dependencies)
        
        return dict(dependencies)
    
    def validate_dependencies(self) -> List[str]:
        """
        Valida se todas as dependências são válidas
        
        Returns:
            Lista de erros encontrados (vazia se tudo OK)
        """
        errors = []
        
        for job_id, deps in self.dependencies.items():
            if job_id not in self.jobs:
                errors.append(f"Job '{job_id}' não encontrado")
                continue
            
            for dep in deps:
                if dep not in self.jobs:
                    errors.append(f"Dependência '{dep}' do job '{job_id}' não encontrada")
                elif dep == job_id:
                    errors.append(f"Job '{job_id}' não pode depender de si mesmo")
        
        return errors
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Detecta ciclos no grafo de dependências
        
        Returns:
            Lista de ciclos encontrados
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node):
            if node in rec_stack:
                # Encontrou um ciclo
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Visitar dependências
            for dep in self.dependencies.get(node, set()):
                dfs(dep)
            
            rec_stack.remove(node)
            path.pop()
        
        for job_id in self.jobs.keys():
            if job_id not in visited:
                dfs(job_id)
        
        return cycles
    
    def get_execution_order(self) -> List[str]:
        """
        Retorna a ordem de execução dos jobs usando ordenação topológica
        
        Returns:
            Lista de query_ids na ordem de execução
        """
        # Validar dependências primeiro
        errors = self.validate_dependencies()
        if errors:
            raise ValueError(f"Dependências inválidas: {errors}")
        
        # Detectar ciclos
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Ciclos detectados: {cycles}")
        
        # Ordenação topológica usando Kahn's algorithm
        in_degree = defaultdict(int)
        
        # Calcular graus de entrada
        for job_id in self.jobs.keys():
            in_degree[job_id] = 0
        
        for job_id, deps in self.dependencies.items():
            for dep in deps:
                in_degree[job_id] += 1
        
        # Fila de jobs sem dependências
        queue = deque([job_id for job_id in self.jobs.keys() if in_degree[job_id] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Atualizar graus de entrada dos dependentes
            for job_id, deps in self.dependencies.items():
                if current in deps:
                    in_degree[job_id] -= 1
                    if in_degree[job_id] == 0:
                        queue.append(job_id)
        
        return result
    
    def get_dependent_jobs(self, job_id: str) -> List[str]:
        """
        Retorna jobs que dependem do job especificado
        
        Args:
            job_id: ID do job
            
        Returns:
            Lista de query_ids que dependem do job
        """
        dependents = []
        
        for job, deps in self.dependencies.items():
            if job_id in deps:
                dependents.append(job)
        
        return dependents
    
    def get_job_dependencies(self, job_id: str) -> List[str]:
        """
        Retorna dependências de um job
        
        Args:
            job_id: ID do job
            
        Returns:
            Lista de query_ids das dependências
        """
        return list(self.dependencies.get(job_id, set()))
    
    def get_execution_groups(self) -> List[List[str]]:
        """
        Retorna grupos de jobs que podem ser executados em paralelo
        
        Returns:
            Lista de grupos, onde cada grupo pode ser executado em paralelo
        """
        execution_order = self.get_execution_order()
        groups = []
        remaining_jobs = set(self.jobs.keys())
        
        while remaining_jobs:
            # Jobs que podem ser executados agora (sem dependências não resolvidas)
            current_group = []
            
            for job_id in list(remaining_jobs):
                deps = self.dependencies.get(job_id, set())
                # Job pode ser executado se todas suas dependências já foram executadas
                if deps.issubset(set(execution_order[:len(execution_order) - len(remaining_jobs)])):
                    current_group.append(job_id)
            
            if not current_group:
                # Se não há jobs que podem ser executados, há um problema
                raise ValueError(f"Não é possível executar jobs restantes: {remaining_jobs}")
            
            groups.append(current_group)
            remaining_jobs -= set(current_group)
        
        return groups
    
    def can_execute_job(self, job_id: str, completed_jobs: Set[str]) -> bool:
        """
        Verifica se um job pode ser executado dado os jobs já completados
        
        Args:
            job_id: ID do job
            completed_jobs: Set de query_ids já completados
            
        Returns:
            True se o job pode ser executado
        """
        if job_id not in self.jobs:
            return False
        
        deps = self.dependencies.get(job_id, set())
        return deps.issubset(completed_jobs)
    
    def get_next_executable_jobs(self, completed_jobs: Set[str]) -> List[str]:
        """
        Retorna jobs que podem ser executados agora
        
        Args:
            completed_jobs: Set de query_ids já completados
            
        Returns:
            Lista de query_ids que podem ser executados
        """
        executable = []
        
        for job_id in self.jobs.keys():
            if job_id not in completed_jobs and self.can_execute_job(job_id, completed_jobs):
                executable.append(job_id)
        
        return executable
