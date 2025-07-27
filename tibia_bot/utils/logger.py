"""
Logger - Sistema de logging configurável
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(name: str = "tibia_bot", level: str = "INFO") -> logging.Logger:
    """
    Configura sistema de logging com arquivo rotativo e console
    """
    # Criar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar logger principal
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Evitar handlers duplicados
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo (com rotação)
    file_handler = RotatingFileHandler(
        log_dir / "tibia_bot.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para erros críticos (arquivo separado)
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=2*1024*1024,  # 2MB
        backupCount=2,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info(f"Logger configurado: {name}")
    return logger

def get_logger(name: str) -> logging.Logger:
    """Obtém logger existente"""
    return logging.getLogger(f"tibia_bot.{name}")