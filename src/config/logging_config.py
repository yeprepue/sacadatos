# src/config/logging_config.py
"""Configuración de logging con Loguru"""
from loguru import logger
import sys
import os
from pathlib import Path


def setup_logging():
    """Configura el logging para toda la app"""
    logger.remove()
    
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Console - desarrollo con colores
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Crear directorio de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Archivo de logs general
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Archivo de errores
    logger.add(
        "logs/error_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}"
    )
    
    return logger


setup_logging()
