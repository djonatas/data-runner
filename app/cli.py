"""
Interface de linha de comando para o Data-Runner
"""

import click
from typing import List, Optional
from .runner import JobRunner
from .types import ExecutionOptions


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Data-Runner - Executor de consultas/processos parametrizado por JSON"""
    pass


@cli.command()
def list_jobs():
    """Lista todos os jobs disponíveis"""
    try:
        runner = JobRunner()
        runner.load_configs()
        
        jobs = runner.list_jobs()
        
        if not jobs:
            click.echo("Nenhum job encontrado.")
            return
        
        click.echo("\n📋 Jobs Disponíveis:")
        click.echo("=" * 80)
        
        for job in jobs:
            target_table = job.target_table or f"stg_{job.query_id}" if job.type.value == "carga" else f"val_{job.query_id}"
            click.echo(f"ID: {job.query_id}")
            click.echo(f"Tipo: {job.type.value}")
            click.echo(f"Conexão: {job.connection}")
            click.echo(f"Tabela alvo: {target_table}")
            click.echo(f"SQL: {job.sql[:100]}{'...' if len(job.sql) > 100 else ''}")
            click.echo("-" * 80)
    
    except Exception as e:
        click.echo(f"❌ Erro ao listar jobs: {e}", err=True)


@cli.command()
@click.option('--id', 'query_id', required=True, help='ID da query para executar')
@click.option('--duckdb', 'duckdb_path', help='Caminho personalizado para o DuckDB')
@click.option('--dry-run', is_flag=True, help='Mostra o que faria sem executar')
@click.option('--limit', type=int, help='Limita o número de linhas retornadas')
@click.option('--save-as', 'save_as', help='Nome personalizado para a tabela alvo')
def run(query_id: str, duckdb_path: Optional[str], dry_run: bool, 
        limit: Optional[int], save_as: Optional[str]):
    """Executa um job específico"""
    try:
        runner = JobRunner()
        runner.load_configs()
        
        # Configurar opções
        options = ExecutionOptions(
            dry_run=dry_run,
            limit=limit,
            save_as=save_as,
            duckdb_path=duckdb_path
        )
        
        # Executar job
        result = runner.run_job(query_id, options)
        
        # Exibir resultado
        click.echo(f"\n🎯 Execução Concluída:")
        click.echo(f"Run ID: {result.run_id}")
        click.echo(f"Status: {result.status.value if result.status else 'N/A'}")
        click.echo(f"Linhas processadas: {result.rowcount or 0}")
        click.echo(f"Tabela alvo: {result.target_table or 'N/A'}")
        
        if result.error:
            click.echo(f"❌ Erro: {result.error}")
        else:
            click.echo("✅ Execução bem-sucedida!")
    
    except Exception as e:
        click.echo(f"❌ Erro na execução: {e}", err=True)


@cli.command()
@click.option('--ids', 'query_ids', required=True, help='IDs das queries separados por vírgula')
@click.option('--duckdb', 'duckdb_path', help='Caminho personalizado para o DuckDB')
@click.option('--dry-run', is_flag=True, help='Mostra o que faria sem executar')
@click.option('--limit', type=int, help='Limita o número de linhas retornadas')
@click.option('--save-as', 'save_as', help='Nome personalizado para a tabela alvo')
def run_batch(query_ids: str, duckdb_path: Optional[str], dry_run: bool,
              limit: Optional[int], save_as: Optional[str]):
    """Executa múltiplos jobs em sequência"""
    try:
        # Parse dos IDs
        ids_list = [id.strip() for id in query_ids.split(',') if id.strip()]
        
        if not ids_list:
            click.echo("❌ Nenhum ID válido fornecido", err=True)
            return
        
        runner = JobRunner()
        runner.load_configs()
        
        # Configurar opções
        options = ExecutionOptions(
            dry_run=dry_run,
            limit=limit,
            save_as=save_as,
            duckdb_path=duckdb_path
        )
        
        # Executar jobs
        results = runner.run_jobs(ids_list, options)
        
        # Exibir resumo
        click.echo(f"\n📊 Resumo da Execução em Lote:")
        click.echo("=" * 80)
        
        success_count = 0
        error_count = 0
        
        for result in results:
            status_icon = "✅" if result.status and result.status.value == "success" else "❌"
            click.echo(f"{status_icon} {result.query_id}: {result.status.value if result.status else 'N/A'} "
                      f"({result.rowcount or 0} linhas)")
            
            if result.status and result.status.value == "success":
                success_count += 1
            else:
                error_count += 1
        
        click.echo("-" * 80)
        click.echo(f"Total: {len(results)} jobs")
        click.echo(f"Sucessos: {success_count}")
        click.echo(f"Erros: {error_count}")
    
    except Exception as e:
        click.echo(f"❌ Erro na execução em lote: {e}", err=True)


@cli.command()
@click.option('--query-id', help='Filtrar por query_id específico')
@click.option('--limit', type=int, default=50, help='Número máximo de registros')
def history(query_id: Optional[str], limit: int):
    """Exibe histórico de execuções"""
    try:
        runner = JobRunner()
        runner.load_configs()
        
        if not runner.repository:
            click.echo("❌ Repositório não inicializado", err=True)
            return
        
        # Buscar histórico
        history_df = runner.repository.get_job_runs(query_id, limit)
        
        if history_df.empty:
            click.echo("Nenhum histórico encontrado.")
            return
        
        click.echo(f"\n📈 Histórico de Execuções:")
        click.echo("=" * 120)
        
        for _, row in history_df.iterrows():
            status_icon = "✅" if row['status'] == 'success' else "❌"
            click.echo(f"{status_icon} {row['query_id']} | {row['type']} | "
                      f"{row['started_at']} | {row['status']} | "
                      f"{row['rowcount'] or 0} linhas | {row['target_table'] or 'N/A'}")
            
            if row['error']:
                click.echo(f"    Erro: {row['error']}")
    
    except Exception as e:
        click.echo(f"❌ Erro ao buscar histórico: {e}", err=True)


@cli.command()
@click.option('--table', help='Nome da tabela para inspecionar')
def inspect(table: Optional[str]):
    """Inspeciona tabelas no DuckDB"""
    try:
        runner = JobRunner()
        runner.load_configs()
        
        if not runner.repository:
            click.echo("❌ Repositório não inicializado", err=True)
            return
        
        if table:
            # Inspecionar tabela específica
            click.echo(f"\n🔍 Inspeção da Tabela: {table}")
            click.echo("=" * 60)
            
            # Informações da tabela
            info_df = runner.repository.get_table_info(table)
            if 'error' in info_df.columns:
                click.echo(f"❌ {info_df['error'].iloc[0]}")
                return
            
            click.echo("Estrutura:")
            for _, row in info_df.iterrows():
                click.echo(f"  {row['column_name']}: {row['column_type']}")
            
            # Contagem de linhas
            row_count = runner.repository.get_table_row_count(table)
            click.echo(f"\nLinhas: {row_count}")
        
        else:
            # Listar todas as tabelas
            tables = runner.repository.list_tables()
            
            if not tables:
                click.echo("Nenhuma tabela encontrada.")
                return
            
            click.echo(f"\n📋 Tabelas no DuckDB:")
            click.echo("=" * 60)
            
            for table_name in tables:
                row_count = runner.repository.get_table_row_count(table_name)
                click.echo(f"{table_name}: {row_count} linhas")
    
    except Exception as e:
        click.echo(f"❌ Erro na inspeção: {e}", err=True)


@cli.command()
@click.option('--table', 'table_name', required=True, help='Nome da tabela para remover')
@click.option('--confirm', is_flag=True, help='Confirma a remoção sem pedir confirmação interativa')
def drop_table(table_name: str, confirm: bool):
    """Remove uma tabela específica do DuckDB"""
    try:
        runner = JobRunner()
        runner.load_configs()
        
        if not runner.repository:
            click.echo("❌ Repositório não inicializado", err=True)
            return
        
        # Verificar se tabela existe
        info_df = runner.repository.get_table_info(table_name)
        if 'error' in info_df.columns:
            click.echo(f"❌ Tabela '{table_name}' não encontrada")
            return
        
        # Mostrar informações da tabela antes de remover
        row_count = runner.repository.get_table_row_count(table_name)
        click.echo(f"\n🗑️  Remoção de Tabela")
        click.echo("=" * 50)
        click.echo(f"Tabela: {table_name}")
        click.echo(f"Linhas: {row_count}")
        
        # Confirmar remoção
        if not confirm:
            if not click.confirm(f"\n⚠️  Tem certeza que deseja remover a tabela '{table_name}'?"):
                click.echo("❌ Operação cancelada")
                return
        
        # Remover tabela
        try:
            success = runner.repository.drop_table(table_name)
            
            if success:
                click.echo(f"✅ Tabela '{table_name}' removida com sucesso!")
            else:
                click.echo(f"❌ Erro ao remover tabela '{table_name}'")
        except ValueError as ve:
            click.echo(f"🚫 {ve}", err=True)
        except Exception as e:
            click.echo(f"❌ Erro ao remover tabela: {e}", err=True)
    
    except Exception as e:
        click.echo(f"❌ Erro ao remover tabela: {e}", err=True)


if __name__ == '__main__':
    cli()
