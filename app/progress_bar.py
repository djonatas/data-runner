"""
Barra de progresso para execução de validações
"""

import time
import sys
from typing import Optional
from datetime import datetime, timedelta


class ProgressBar:
    """Barra de progresso para validação por registro"""
    
    def __init__(self, total: int, description: str = "Processando", 
                 width: int = 50, show_eta: bool = True):
        """
        Inicializa a barra de progresso
        
        Args:
            total: Número total de itens a processar
            description: Descrição do processo
            width: Largura da barra em caracteres
            show_eta: Se deve mostrar estimativa de tempo
        """
        self.total = total
        self.description = description
        self.width = width
        self.show_eta = show_eta
        self.current = 0
        self.start_time = None
        self.last_update_time = None
        self.last_update_count = 0
        
    def start(self):
        """Inicia o cronômetro"""
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_update_count = 0
        self._print_initial()
    
    def update(self, increment: int = 1, force_update: bool = False):
        """
        Atualiza o progresso
        
        Args:
            increment: Quantos itens foram processados desde a última atualização
            force_update: Força a atualização mesmo se não passou tempo suficiente
        """
        self.current += increment
        current_time = time.time()
        
        # Atualizar apenas a cada 0.1 segundos ou se forçado
        if force_update or (current_time - self.last_update_time) >= 0.1:
            self._print_progress()
            self.last_update_time = current_time
            self.last_update_count = self.current
    
    def finish(self):
        """Finaliza a barra de progresso"""
        self.current = self.total
        self._print_final()
    
    def _print_initial(self):
        """Imprime o cabeçalho inicial"""
        print(f"\n🚀 {self.description}")
        print("=" * 60)
    
    def _print_progress(self):
        """Imprime a barra de progresso atual"""
        if self.total == 0:
            return
        
        # Calcular porcentagem
        percentage = (self.current / self.total) * 100
        
        # Calcular barras preenchidas
        filled = int((self.current / self.total) * self.width)
        bar = "█" * filled + "░" * (self.width - filled)
        
        # Calcular tempo decorrido
        elapsed_time = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed_time)
        
        # Calcular ETA se habilitado
        eta_str = ""
        if self.show_eta and self.current > 0:
            eta = self._calculate_eta(elapsed_time)
            if eta:
                eta_str = f" | ETA: {self._format_time(eta)}"
        
        # Calcular velocidade (registros por segundo)
        speed = self.current / elapsed_time if elapsed_time > 0 else 0
        speed_str = f" | {speed:.1f} reg/s"
        
        # Imprimir linha de progresso
        line = (f"\r[{bar}] {percentage:5.1f}% "
                f"({self.current}/{self.total}) "
                f"| Tempo: {elapsed_str}{eta_str}{speed_str}")
        
        sys.stdout.write(line)
        sys.stdout.flush()
    
    def _print_final(self):
        """Imprime o resultado final"""
        elapsed_time = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed_time)
        speed = self.total / elapsed_time if elapsed_time > 0 else 0
        
        print(f"\n✅ Processamento concluído!")
        print(f"   📊 Total: {self.total} registros")
        print(f"   ⏱️  Tempo total: {elapsed_str}")
        print(f"   🚀 Velocidade média: {speed:.1f} registros/segundo")
        print("=" * 60)
    
    def _calculate_eta(self, elapsed_time: float) -> Optional[float]:
        """
        Calcula o tempo estimado para conclusão
        
        Args:
            elapsed_time: Tempo decorrido em segundos
            
        Returns:
            Tempo estimado em segundos ou None se não for possível calcular
        """
        if self.current <= 0 or elapsed_time <= 0:
            return None
        
        # Calcular velocidade atual
        current_speed = self.current / elapsed_time
        
        # Se a velocidade for muito baixa, usar média recente
        if self.current >= 10:
            recent_time = time.time() - self.last_update_time
            if recent_time > 0:
                recent_speed = (self.current - self.last_update_count) / recent_time
                # Usar média ponderada (70% velocidade atual, 30% velocidade recente)
                current_speed = (current_speed * 0.7) + (recent_speed * 0.3)
        
        # Calcular tempo restante
        remaining = self.total - self.current
        if current_speed > 0:
            return remaining / current_speed
        
        return None
    
    def _format_time(self, seconds: float) -> str:
        """
        Formata tempo em segundos para string legível
        
        Args:
            seconds: Tempo em segundos
            
        Returns:
            String formatada (ex: "2m 30s" ou "1h 15m 30s")
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        
        if minutes < 60:
            return f"{minutes}m {remaining_seconds}s"
        
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        
        return f"{hours}h {remaining_minutes}m {remaining_seconds}s"


class ValidationProgressBar(ProgressBar):
    """Barra de progresso específica para validação"""
    
    def __init__(self, total: int, validation_file: str, output_table: Optional[str] = None):
        """
        Inicializa barra de progresso para validação
        
        Args:
            total: Número total de registros a validar
            validation_file: Nome do arquivo de validação
            output_table: Nome da tabela de output (opcional)
        """
        description = f"Validando {total} registros"
        if output_table:
            description += f" → {output_table}"
        
        super().__init__(
            total=total,
            description=description,
            width=40,
            show_eta=True
        )
        
        self.validation_file = validation_file
        self.output_table = output_table
        self.success_count = 0
        self.error_count = 0
    
    def update_with_result(self, success: bool, increment: int = 1):
        """
        Atualiza progresso com resultado da validação
        
        Args:
            success: Se a validação foi bem-sucedida
            increment: Quantos registros foram processados
        """
        if success:
            self.success_count += increment
        else:
            self.error_count += increment
        
        self.update(increment)
    
    def _print_final(self):
        """Imprime resultado final com estatísticas de validação"""
        elapsed_time = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed_time)
        speed = self.total / elapsed_time if elapsed_time > 0 else 0
        success_rate = (self.success_count / self.total * 100) if self.total > 0 else 0
        
        print(f"\n✅ Validação concluída!")
        print(f"   📊 Total processado: {self.total} registros")
        print(f"   ✅ Sucessos: {self.success_count} ({success_rate:.1f}%)")
        print(f"   ❌ Erros: {self.error_count}")
        print(f"   ⏱️  Tempo total: {elapsed_str}")
        print(f"   🚀 Velocidade: {speed:.1f} registros/segundo")
        
        if self.output_table:
            print(f"   💾 Resultados salvos em: {self.output_table}")
        
        print("=" * 60)


def create_validation_progress_bar(total: int, validation_file: str, 
                                 output_table: Optional[str] = None) -> ValidationProgressBar:
    """
    Cria uma barra de progresso para validação
    
    Args:
        total: Número total de registros
        validation_file: Nome do arquivo de validação
        output_table: Nome da tabela de output
        
    Returns:
        ValidationProgressBar configurada
    """
    return ValidationProgressBar(total, validation_file, output_table)
